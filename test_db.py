#!/usr/bin/env python3
"""
Script para diagnosticar problemas de conexão com PostgreSQL/Supabase
"""

import asyncio
import asyncpg
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import sys

# Carrega variáveis de ambiente
load_dotenv()

async def test_connection_methods():
    """
    Testa diferentes métodos de conexão para diagnosticar o problema
    """
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada!")
        return
    
    print(f"🔍 DATABASE_URL encontrada: {database_url[:50]}...")
    
    # Parse da URL
    parsed = urlparse(database_url)
    print(f"📋 Componentes parseados:")
    print(f"   Scheme: {parsed.scheme}")
    print(f"   Host: {parsed.hostname}")
    print(f"   Port: {parsed.port or 5432}")
    print(f"   User: {parsed.username}")
    print(f"   Database: {parsed.path.lstrip('/') or 'postgres'}")
    print(f"   Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
    
    config = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/') or 'postgres'
    }
    
    # Testa diferentes configurações SSL
    ssl_configs = [
        ('require', 'SSL obrigatório'),
        ('prefer', 'SSL preferido'),
        ('allow', 'SSL permitido'),
        ('disable', 'SSL desabilitado')
    ]
    
    for ssl_mode, description in ssl_configs:
        print(f"\n🔄 Testando conexão com {description} ({ssl_mode})...")
        
        try:
            conn = await asyncpg.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                ssl=ssl_mode,
                command_timeout=10
            )
            
            # Testa uma query
            result = await conn.fetchval('SELECT version()')
            await conn.close()
            
            print(f"✅ SUCESSO com {description}!")
            print(f"   PostgreSQL: {result.split()[1]}")
            return True
            
        except Exception as e:
            print(f"❌ Falha com {description}: {type(e).__name__}: {e}")
            continue
    
    print(f"\n❌ Todas as tentativas de conexão falharam!")
    
    # Testa conexão com parâmetros individuais
    print(f"\n🔄 Testando com parâmetros separados...")
    try:
        conn = await asyncpg.connect(
            user=config['user'],
            password=config['password'],
            database=config['database'],
            host=config['host'],
            port=config['port']
        )
        
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        print(f"✅ SUCESSO com parâmetros separados!")
        
    except Exception as e:
        print(f"❌ Falha com parâmetros separados: {type(e).__name__}: {e}")

async def test_url_variations():
    """
    Testa diferentes formatos de URL
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return
    
    print(f"\n🔄 Testando variações da URL...")
    
    # Variações da URL para testar
    variations = [
        database_url,  # Original
        database_url.replace('postgresql://', 'postgres://'),  # Mudança de scheme
        database_url.replace('postgres://', 'postgresql://'),  # Mudança de scheme
    ]
    
    for i, url in enumerate(variations):
        if url == database_url and i > 0:
            continue  # Evita duplicatas
            
        print(f"\n   Variação {i+1}: {url[:50]}...")
        try:
            conn = await asyncpg.connect(url)
            result = await conn.fetchval('SELECT 1')
            await conn.close()
            print(f"   ✅ SUCESSO com variação {i+1}!")
            
        except Exception as e:
            print(f"   ❌ Falha: {type(e).__name__}: {e}")

async def test_asyncpg_version():
    """
    Testa a versão do asyncpg
    """
    print(f"\n📦 Informações do ambiente:")
    print(f"   Python: {sys.version}")
    print(f"   asyncpg: {asyncpg.__version__}")

async def main():
    """
    Executa todos os testes
    """
    print("🚀 Iniciando diagnóstico de conexão com banco de dados...")
    
    await test_asyncpg_version()
    await test_connection_methods()
    await test_url_variations()
    
    print(f"\n🏁 Diagnóstico concluído!")

if __name__ == "__main__":
    asyncio.run(main())