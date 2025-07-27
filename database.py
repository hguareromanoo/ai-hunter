import asyncpg
import os
from urllib.parse import urlparse
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    def get_config_from_env_vars(self) -> Optional[Dict[str, Any]]:
        """
        Constrói configuração a partir de variáveis separadas
        Mais seguro para senhas com caracteres especiais
        """
        host = os.environ.get("DB_HOST")
        port = os.environ.get("DB_PORT", "5432")
        user = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASSWORD")
        database = os.environ.get("DB_NAME", "postgres")
        
        # Se não tem as variáveis básicas, retorna None
        if not all([host, user, password]):
            logger.error(f"Variáveis obrigatórias não encontradas - Host: {bool(host)}, User: {bool(user)}, Password: {bool(password)}")
            return None
        
        try:
            config = {
                'host': host.strip(),
                'port': int(port),
                'user': user.strip(),
                'password': password,  # Não faz strip na senha para preservar espaços
                'database': database.strip()
            }
            
            logger.info(f"Usando variáveis separadas: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
            return config
            
        except ValueError as e:
            logger.error(f"Erro ao converter porta: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao processar variáveis separadas: {e}")
            return None
    
    def parse_database_url(self, database_url: str) -> Optional[Dict[str, Any]]:
        """
        Parse DATABASE_URL com validação robusta
        Suporta formatos:
        - postgresql://user:pass@host:port/dbname
        - postgres://user:pass@host:port/dbname
        """
        if not database_url or database_url.strip() == "":
            logger.error("DATABASE_URL está vazia ou não definida")
            return None
        
        try:
            # Remove espaços em branco
            database_url = database_url.strip()
            
            # Parse da URL
            parsed = urlparse(database_url)
            
            # Validações básicas
            if not parsed.scheme:
                logger.error("Scheme (postgresql:// ou postgres://) não encontrado na DATABASE_URL")
                return None
            
            if parsed.scheme not in ['postgresql', 'postgres']:
                logger.error(f"Scheme inválido: {parsed.scheme}. Use 'postgresql' ou 'postgres'")
                return None
            
            if not parsed.hostname:
                logger.error("Hostname não encontrado na DATABASE_URL")
                return None
            
            if not parsed.username:
                logger.error("Username não encontrado na DATABASE_URL")
                return None
            
            if not parsed.password:
                logger.error("Password não encontrado na DATABASE_URL")
                return None
            
            # Limpar e validar componentes
            username = parsed.username.strip()
            password = parsed.password  # NÃO fazer strip na senha do Supabase
            hostname = parsed.hostname.strip()
            
            # Verificar se há caracteres problemáticos no username
            if any(char in username for char in ['"', "'", '\n', '\r', '\t']):
                logger.error("Username contém caracteres inválidos")
                return None
            
            # Extrair componentes
            config = {
                'host': hostname,
                'port': parsed.port or 5432,
                'user': username,
                'password': password,  # Senha sem modificações
                'database': parsed.path.lstrip('/') if parsed.path else 'postgres'
            }
            
            logger.info(f"DATABASE_URL parseada com sucesso: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
            return config
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse da DATABASE_URL: {e}")
            logger.error(f"URL fornecida (mascarada): {database_url[:30]}...")
            return None
    
    async def test_connection(self, db_config: Dict[str, Any]) -> bool:
        """
        Testa a conexão com o banco de dados
        Específico para Supabase com fallback SSL
        """
        try:
            logger.info(f"Testando conexão com {db_config['host']}:{db_config['port']}")
            logger.info(f"Usuário: {db_config['user']}")
            logger.info(f"Database: {db_config['database']}")
            
            # Para Supabase, sempre começar com SSL require
            ssl_modes = ['require', 'prefer']
            
            for ssl_mode in ssl_modes:
                try:
                    logger.info(f"🔄 Tentando com SSL {ssl_mode}...")
                    
                    conn = await asyncpg.connect(
                        host=db_config['host'],
                        port=db_config['port'],
                        user=db_config['user'],
                        password=db_config['password'],
                        database=db_config['database'],
                        ssl=ssl_mode,
                        command_timeout=20,  # Aumentado para Supabase
                        server_settings={
                            'application_name': 'ai-hunter-backend-test'
                        }
                    )
                    
                    # Teste básico
                    result = await conn.fetchval('SELECT version()')
                    current_db = await conn.fetchval('SELECT current_database()')
                    await conn.close()
                    
                    logger.info(f"✅ Conexão SSL {ssl_mode} testada com sucesso!")
                    logger.info(f"📊 Database: {current_db}")
                    logger.info(f"🏷️ PostgreSQL: {result.split()[1] if result else 'Unknown'}")
                    return True
                    
                except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
                    logger.error(f"❌ Erro de autenticação com SSL {ssl_mode}: {e}")
                    break  # Não tenta outros SSL se auth falhou
                except Exception as ssl_error:
                    logger.warning(f"⚠️ Falha com SSL {ssl_mode}: {ssl_error}")
                    continue  # Tenta próximo SSL mode
            
            # Se chegou aqui, todos os SSL modes falharam
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro inesperado na conexão: {type(e).__name__}: {e}")
            return False
    
    async def create_pool(self, db_config: Dict[str, Any]) -> Optional[asyncpg.Pool]:
        """
        Cria o pool de conexões otimizado para Supabase
        """
        try:
            logger.info("🔄 Criando pool de conexões...")
            
            # Para Supabase, usar configurações otimizadas
            ssl_modes = ['require', 'prefer']
            
            for ssl_mode in ssl_modes:
                try:
                    logger.info(f"🔄 Criando pool com SSL {ssl_mode}...")
                    
                    pool = await asyncpg.create_pool(
                        host=db_config['host'],
                        port=db_config['port'],
                        user=db_config['user'],
                        password=db_config['password'],
                        database=db_config['database'],
                        ssl=ssl_mode,
                        min_size=1,
                        max_size=5,  # Supabase tem limite de conexões
                        command_timeout=60,
                        max_queries=50000,
                        max_inactive_connection_lifetime=300,
                        server_settings={
                            'application_name': 'ai-hunter-backend',
                            'timezone': 'UTC'
                        }
                    )
                    
                    # Testa o pool
                    async with pool.acquire() as conn:
                        await conn.fetchval('SELECT 1')
                    
                    logger.info(f"✅ Pool de conexões criado com SSL {ssl_mode}!")
                    return pool
                    
                except Exception as ssl_error:
                    logger.warning(f"⚠️ Falha ao criar pool com SSL {ssl_mode}: {ssl_error}")
                    continue
            
            logger.error("❌ Não foi possível criar pool com nenhuma configuração SSL")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pool: {type(e).__name__}: {e}")
            return None
    
    async def initialize(self) -> bool:
        """
        Inicializa a conexão com o banco de dados
        Prioriza variáveis separadas por serem mais seguras para caracteres especiais
        """
        logger.info("🚀 Inicializando conexão com banco de dados...")
        
        # PRIORIDADE 1: Tenta variáveis separadas primeiro
        db_config = self.get_config_from_env_vars()
        
        if db_config:
            logger.info("✅ Usando variáveis de ambiente separadas (DB_HOST, DB_USER, etc.)")
        else:
            # PRIORIDADE 2: Fallback para DATABASE_URL
            logger.info("⚠️ Variáveis separadas não encontradas, tentando DATABASE_URL...")
            database_url = os.environ.get("DATABASE_URL")
            
            if not database_url:
                logger.error("❌ Nem variáveis separadas nem DATABASE_URL configuradas.")
                logger.info("💡 Configure as variáveis: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
                return False
            
            # Parse da URL
            db_config = self.parse_database_url(database_url)
            if not db_config:
                logger.error("❌ DATABASE_URL malformada ou inválida.")
                return False
        
        # Testa a conexão
        logger.info("🔍 Testando conectividade...")
        if not await self.test_connection(db_config):
            logger.error("❌ Falha no teste de conexão.")
            logger.info("💡 Verifique:")
            logger.info("   - Se as credenciais estão corretas")
            logger.info("   - Se o projeto Supabase está ativo")
            logger.info("   - Se não há restrições de firewall")
            return False
        
        # Cria o pool
        logger.info("🏊 Criando pool de conexões...")
        self.pool = await self.create_pool(db_config)
        if not self.pool:
            logger.error("❌ Falha ao criar pool de conexões.")
            return False
        
        logger.info("🎉 Banco de dados conectado com sucesso!")
        logger.info("📊 Status: Pool ativo e pronto para uso")
        return True
    
    async def close(self):
        """
        Fecha o pool de conexões
        """
        if self.pool:
            await self.pool.close()
            logger.info("🔒 Pool de conexões fechado.")
    
    def is_connected(self) -> bool:
        """
        Verifica se há conexão ativa
        """
        return self.pool is not None and not self.pool._closed

# Instância global
db_manager = DatabaseManager()

async def get_db_pool():
    """
    Retorna o pool de conexões ou None se não conectado
    """
    return db_manager.pool if db_manager.is_connected() else None

# Funções de utilidade para debug
async def test_db_health():
    """
    Testa a saúde da conexão
    """
    if not db_manager.is_connected():
        return {"status": "disconnected", "message": "Pool não inicializado"}
    
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval('SELECT NOW() as timestamp')
            return {"status": "healthy", "timestamp": str(result)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def get_db_info():
    """
    Obtém informações do banco
    """
    if not db_manager.is_connected():
        return {"status": "disconnected"}
    
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            version = await conn.fetchval('SELECT version()')
            current_db = await conn.fetchval('SELECT current_database()')
            user = await conn.fetchval('SELECT current_user')
            
            # Verifica se a tabela existe
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'lead_profiles'
                )
            """)
            
            return {
                "status": "connected",
                "database": current_db,
                "user": user,
                "version": version.split()[0:2],
                "table_lead_profiles_exists": table_exists,
                "pool_size": pool.get_size(),
                "pool_min_size": pool.get_min_size(),
                "pool_max_size": pool.get_max_size()
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}