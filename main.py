from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from render_report import renderizar_relatorio
from schemas import LeadProfileInput, FinalReportData, Opportunity
from models import calculate_scores, opportunityTracker
import asyncpg
import os
from dotenv import load_dotenv
import json
import re
from urllib.parse import urlparse

load_dotenv()

app = FastAPI(
    title="Diagnóstico IA Hunter v2",
    description="API para qualificação e geração de relatórios com base em dados de formulário.",
    version="2.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Connection ---
DB_POOL = None

def parse_database_url(database_url):
    """
    Parse and validate database URL
    """
    try:
        parsed = urlparse(database_url)
        
        if not all([parsed.scheme, parsed.hostname, parsed.username, parsed.password]):
            return None
            
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/') or 'postgres'
        }
    except Exception as e:
        print(f"Erro ao fazer parse da URL: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    global DB_POOL
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url or database_url.strip() == "":
        print("⚠️  DATABASE_URL não configurado. Executando sem banco de dados.")
        DB_POOL = None
        return
    
    # Parse da URL
    db_config = parse_database_url(database_url)
    if not db_config:
        print("⚠️  DATABASE_URL malformada. Executando sem banco de dados.")
        DB_POOL = None
        return
    
    try:
        print(f"🔄 Tentando conectar ao banco: {db_config['host']}:{db_config['port']}")
        
        # Testa conexão individual primeiro
        conn = await asyncpg.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl='require'  # Supabase requer SSL
        )
        
        # Testa uma query simples
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        print(f"✅ Teste de conexão bem-sucedido! Resultado: {result}")
        
        # Cria o pool de conexões
        DB_POOL = await asyncpg.create_pool(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl='require',
            min_size=1,
            max_size=5,
            server_settings={
                'application_name': 'ai-hunter-backend',
            }
        )
        print("✅ Pool de conexões criado com sucesso!")
        
    except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
        print(f"❌ Erro de autenticação: {e}")
        print("   Verifique as credenciais do Supabase.")
        DB_POOL = None
    except asyncpg.exceptions.CannotConnectNowError as e:
        print(f"❌ Erro de conexão: {e}")
        print("   O Supabase pode estar indisponível.")
        DB_POOL = None
    except Exception as e:
        print(f"❌ Erro inesperado: {type(e).__name__}: {e}")
        print("   Continuando sem banco de dados...")
        DB_POOL = None

@app.on_event("shutdown")
async def shutdown_event():
    if DB_POOL:
        await DB_POOL.close()
        print("🔒 Pool de conexões fechado.")

# --- API Endpoints ---

@app.post("/api/v2/diagnostico", response_class=HTMLResponse)
async def run_full_diagnostic_flow(form_data: LeadProfileInput):
    """
    Receives form data, saves it, runs analysis, updates the record,
    and returns a fully rendered HTML report.
    """
    
    try:
        print(f"📝 Processando dados para: {form_data.name}")
        
        # 1. Run AI analysis and scoring (independente do DB)
        radar_scores, final_score = calculate_scores(form_data)
        print(f"📊 Scores calculados - Final: {final_score}")
        
        opportunities_result = await opportunityTracker.run(deps=form_data)
        if not opportunities_result or not opportunities_result.output:
            raise HTTPException(status_code=500, detail="Failed to generate opportunities.")
        
        opportunities = opportunities_result.output.opportunities
        print(f"💡 Geradas {len(opportunities)} oportunidades")

        # 2. Consolidate data for the report
        report_data = FinalReportData(
            empresa={"nome": form_data.name or "Sua Empresa"},
            scores_radar=radar_scores,
            score_final=final_score,
            relatorio_oportunidades=opportunities,
            relatorio_riscos=[ 
                {"titulo": "Segurança de Dados", "descricao": "A implementação de IA exige atenção redobrada à segurança dos dados e conformidade com a LGPD."},
                {"titulo": "Gestão da Mudança", "descricao": "A adoção de novas tecnologias requer uma comunicação clara e treinamento para garantir a adesão da equipe."}
            ]
        )

        # 3. Save to database (se disponível)
        if DB_POOL:
            try:
                await save_to_database(form_data, report_data)
            except Exception as db_error:
                print(f"⚠️  Erro ao salvar no banco: {db_error}")
                # Não falha a API se não conseguir salvar
        else:
            print("⚠️  Executando sem salvar no banco de dados")

        # 4. Render and return the final HTML report
        html_content = renderizar_relatorio(report_data.dict())
        print("✅ Relatório HTML gerado com sucesso")
        return HTMLResponse(content=html_content, status_code=200)

    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def save_to_database(form_data: LeadProfileInput, report_data: FinalReportData):
    """Helper function to save data to database"""
    async with DB_POOL.acquire() as conn:
        try:
            async with conn.transaction():
                # Ajustado para corresponder exatamente ao schema
                lead_id = await conn.fetchval(
                    """
                    INSERT INTO lead_profiles (
                        lead_email, lead_phone, name, 
                        raw_p1_sector, raw_p2_company_size, raw_p3_role, 
                        raw_p4_main_pain, raw_p5_critical_area, raw_p6_pain_quant,
                        raw_p7_digital_maturity, raw_p8_investment, raw_p9_urgency, 
                        status, ai_score_final, ai_scores_json, ai_full_report_json
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    RETURNING id
                    """,
                    form_data.p0_email, 
                    form_data.p_phone, 
                    form_data.name,
                    form_data.p1_sector, 
                    form_data.p2_company_size, 
                    form_data.p3_role,
                    form_data.p4_main_pain, 
                    form_data.p5_critical_area, 
                    form_data.p6_pain_quant,
                    form_data.p7_digital_maturity, 
                    form_data.p8_investment, 
                    form_data.p9_urgency,
                    'COMPLETED',  # status
                    report_data.score_final,
                    json.dumps(report_data.scores_radar.dict()),
                    json.dumps(report_data.dict())
                )
                print(f"✅ Dados salvos no banco com ID: {lead_id}")
        except Exception as e:
            print(f"❌ Erro ao salvar no banco: {e}")
            raise

@app.get("/")
def read_root():
    return {
        "message": "Bem-vindo ao Diagnóstico IA Hunter v2!", 
        "db_status": "connected" if DB_POOL else "disconnected",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected" if DB_POOL else "disconnected",
        "version": "2.0.0"
    }

@app.get("/test-db")
async def test_database():
    """Endpoint para testar a conexão com o banco"""
    if not DB_POOL:
        return {"status": "no_connection", "message": "Database pool not initialized"}
    
    try:
        async with DB_POOL.acquire() as conn:
            result = await conn.fetchval('SELECT NOW()')
            return {"status": "success", "timestamp": str(result)}
    except Exception as e:
        return {"status": "error", "message": str(e)}