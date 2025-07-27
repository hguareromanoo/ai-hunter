import asyncio
import asyncpg
import socket

async def test_connection():
    """Função async para testar conexão"""
    SUPABASE_CONFIG = {
        'host': 'db.kplggxyetwbbkrxkgwha.supabase.co',
        'port': 5432,  
        'user': 'postgres',
        'password': 'Gyxhed-ridmib-0wudci',
        'database': 'postgres'
    }
    
    try:
        print("🔄 Testando conexão...")
        
        # DNS
        ip = socket.gethostbyname(SUPABASE_CONFIG['host'])
        print(f"✅ DNS: {ip}")
        
        # PostgreSQL
        conn = await asyncpg.connect(**SUPABASE_CONFIG, ssl='require')
        result = await conn.fetchval('SELECT current_database()')
        print(f"✅ Database: {result}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# Execute na célula do Jupyter
task = asyncio.create_task(test_connection())
result = await task
print(f"Resultado: {result}")