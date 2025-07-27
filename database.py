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
        
        # ADICIONE ESTE BLOCO QUE ESTAVA FALTANDO:
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
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
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
            password = parsed.password.strip()
            hostname = parsed.hostname.strip()
            
            # Verificar se há caracteres problemáticos
            if any(char in username for char in ['"', "'", '\n', '\r', '\t']):
                logger.error("Username contém caracteres inválidos")
                return None
            
            if any(char in password for char in ['\n', '\r', '\t']):
                logger.error("Password contém caracteres inválidos")
                return None
            
            # Extrair componentes
            config = {
                'host': hostname,
                'port': parsed.port or 5432,
                'user': username,
                'password': password,
                'database': parsed.path.lstrip('/') if parsed.path else 'postgres'
            }
            
            logger.info(f"DATABASE_URL parseada com sucesso: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
            return config
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse da DATABASE_URL: {e}")
            logger.error(f"URL fornecida: {database_url[:50]}...")  # Mostra apenas o início para segurança
            return None
    
    async def test_connection(self, db_config: Dict[str, Any]) -> bool:
        """
        Testa a conexão com o banco de dados
        """
        try:
            logger.info(f"Testando conexão com {db_config['host']}:{db_config['port']}")
            logger.info(f"Usuário: {db_config['user'][:10]}...")
            logger.info(f"Database: {db_config['database']}")
            
            # Primeira tentativa com SSL obrigatório
            try:
                conn = await asyncpg.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    ssl='require',
                    command_timeout=15
                )
                
                result = await conn.fetchval('SELECT version()')
                await conn.close()
                logger.info(f"✅ Conexão SSL testada com sucesso!")
                return True
                
            except Exception as ssl_error:
                logger.warning(f"⚠️  Falha com SSL require: {ssl_error}")
                logger.info("🔄 Tentando com SSL prefer...")
                
                # Segunda tentativa com SSL prefer
                conn = await asyncpg.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    ssl='prefer',
                    command_timeout=15
                )
                
                result = await conn.fetchval('SELECT version()')
                await conn.close()
                logger.info(f"✅ Conexão SSL prefer testada com sucesso!")
                return True
            
        except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
            logger.error(f"❌ Erro de autenticação: {e}")
            logger.error("   Verifique username/password no Supabase")
            return False
        except asyncpg.exceptions.InvalidCatalogNameError as e:
            logger.error(f"❌ Banco de dados não encontrado: {e}")
            logger.error(f"   Verifique se o banco '{db_config['database']}' existe")
            return False
        except asyncpg.exceptions.CannotConnectNowError as e:
            logger.error(f"❌ Não foi possível conectar: {e}")
            logger.error("   O servidor pode estar indisponível")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado na conexão: {type(e).__name__}: {e}")
            logger.error(f"   Detalhes do erro: {str(e)}")
            return False
    
    async def create_pool(self, db_config: Dict[str, Any]) -> Optional[asyncpg.Pool]:
        """
        Cria o pool de conexões
        """
        try:
            logger.info("🔄 Criando pool de conexões...")
            
            # Tenta primeiro com SSL require
            try:
                pool = await asyncpg.create_pool(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    ssl='require',
                    min_size=1,
                    max_size=5,
                    command_timeout=60,
                    server_settings={
                        'application_name': 'ai-hunter-backend',
                    }
                )
                logger.info("✅ Pool de conexões criado com SSL require!")
                return pool
                
            except Exception as ssl_error:
                logger.warning(f"⚠️  Falha ao criar pool com SSL require: {ssl_error}")
                logger.info("🔄 Tentando pool com SSL prefer...")
                
                pool = await asyncpg.create_pool(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    ssl='prefer',
                    min_size=1,
                    max_size=5,
                    command_timeout=60,
                    server_settings={
                        'application_name': 'ai-hunter-backend',
                    }
                )
                logger.info("✅ Pool de conexões criado com SSL prefer!")
                return pool
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pool: {type(e).__name__}: {e}")
            logger.error(f"   Detalhes: {str(e)}")
            return None
    
    async def initialize(self) -> bool:
        """
        Inicializa a conexão com o banco de dados
        Prioriza variáveis separadas por serem mais seguras para caracteres especiais
        """
        # PRIORIDADE 1: Tenta variáveis separadas primeiro
        db_config = self.get_config_from_env_vars()
        
        if db_config:
            logger.info("✅ Usando variáveis de ambiente separadas (DB_HOST, DB_USER, etc.)")
        else:
            # PRIORIDADE 2: Fallback para DATABASE_URL se não tem variáveis separadas
            logger.info("⚠️  Variáveis separadas não encontradas, tentando DATABASE_URL...")
            database_url = os.environ.get("DATABASE_URL")
            
            if not database_url:
                logger.warning("❌ Nem variáveis separadas nem DATABASE_URL configuradas.")
                logger.info("💡 Configure as variáveis: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
                return False
            
            # Parse da URL
            db_config = self.parse_database_url(database_url)
            if not db_config:
                logger.error("❌ DATABASE_URL malformada.")
                return False
        
        # Testa a conexão
        if not await self.test_connection(db_config):
            logger.error("❌ Falha no teste de conexão.")
            return False
        
        # Cria o pool
        self.pool = await self.create_pool(db_config)
        if not self.pool:
            logger.error("❌ Falha ao criar pool.")
            return False
        
        logger.info("🎉 Banco de dados conectado com sucesso!")
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
        return self.pool is not None

# Instância global
db_manager = DatabaseManager()

async def get_db_pool():
    """
    Retorna o pool de conexões ou None se não conectado
    """
    return db_manager.pool if db_manager.is_connected() else None