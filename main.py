from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from render_report import renderizar_relatorio
from schemas import LeadProfileInput, FinalReportData, Opportunity
from models import calculate_scores, opportunityTracker, researchAgent
from database import db_manager, get_db_pool
from webhook_service import convert_html_to_pdf_and_send_webhook
import json
import logging
import asyncio

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# --- Events ---
@app.on_event("startup")
async def startup_event():
    """
    Inicializa a conexão com o banco de dados
    """
    logger.info("🚀 Iniciando aplicação...")
    success = await db_manager.initialize()
    
    if success:
        logger.info("✅ Aplicação iniciada com banco de dados conectado")
    else:
        logger.warning("⚠️  Aplicação iniciada SEM banco de dados")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Fecha a conexão com o banco de dados
    """
    await db_manager.close()
    logger.info("🛑 Aplicação finalizada")

# --- API Endpoints ---

@app.post("/api/v2/diagnostico", response_class=HTMLResponse)
async def run_full_diagnostic_flow(form_data: LeadProfileInput):
    """
    Receives form data, saves it, runs analysis, updates the record,
    and returns a fully rendered HTML report.
    """
    
    try:
        logger.info(f"📝 Processando dados para: {form_data.name}")
        
        # 1. Run AI analysis and scoring (independente do DB)
        radar_scores, final_score = calculate_scores(form_data)
        logger.info(f"📊 Scores calculados - Final: {final_score}")
        
        opportunities_result = await opportunityTracker.run(deps=form_data)
        if not opportunities_result or not opportunities_result.output:
            raise HTTPException(status_code=500, detail="Failed to generate opportunities.")
        
        opportunities = opportunities_result.output.opportunities
        logger.info(f"💡 Geradas {len(opportunities)} oportunidades")
        
        # Corrigido o f-string para funcionar corretamente
        introduction_result = await researchAgent.run(
            f"Faça a pesquisa de mercado para o setor {form_data.p1_sector} de 400 caracteres em dois parágrafos",
            deps=form_data
        )
        introduction_output = introduction_result.output if introduction_result and introduction_result.output else "Introdução não disponível."
        
        # 2. Consolidate data for the report
        report_data = FinalReportData(
            empresa={"nome": form_data.name or "Sua Empresa"},
            scores_radar=radar_scores,
            score_final=final_score,
            introduction=introduction_output,
            relatorio_oportunidades=opportunities,
            relatorio_riscos=[ 
                {"titulo": "Segurança de Dados", "descricao": "A implementação de IA exige atenção redobrada à segurança dos dados e conformidade com a LGPD."},
                {"titulo": "Gestão da Mudança", "descricao": "A adoção de novas tecnologias requer uma comunicação clara e treinamento para garantir a adesão da equipe."}
            ]
        )

        # 3. Save to database (se disponível)
        if db_manager.is_connected():
            try:
                await save_to_database(form_data, report_data)
            except Exception as db_error:
                logger.warning(f"⚠️  Erro ao salvar no banco: {db_error}")
                # Não falha a API se não conseguir salvar
        else:
            logger.warning("⚠️  Executando sem salvar no banco de dados")

        # 4. Render HTML report
        html_content = renderizar_relatorio(report_data.dict())
        logger.info("✅ Relatório HTML gerado com sucesso")
        
        # 5. Convert form_data to dict for webhook
        form_data_dict = form_data.model_dump(by_alias=True)
        
        # 6. Send to webhook in background (não bloqueia a resposta)
        logger.info("🔄 Enviando dados para webhook em background...")
        
        # Usar try/except para não quebrar a API se o webhook falhar
        try:
            asyncio.create_task(
                convert_html_to_pdf_and_send_webhook(form_data_dict, html_content)
            )
        except Exception as webhook_error:
            logger.warning(f"⚠️  Erro ao iniciar task do webhook: {webhook_error}")

        # 7. Return HTML immediately
        return HTMLResponse(content=html_content, status_code=200)
    

    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def save_to_database(form_data: LeadProfileInput, report_data: FinalReportData):
    """Helper function to save data to database"""
    pool = await get_db_pool()
    if not pool:
        raise Exception("Database pool not available")
    
    async with pool.acquire() as conn:
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
                logger.info(f"✅ Dados salvos no banco com ID: {lead_id}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no banco: {e}")
            raise

@app.get("/")
def read_root():
    return {
        "message": "Bem-vindo ao Diagnóstico IA Hunter v2!", 
        "db_status": "connected" if db_manager.is_connected() else "disconnected",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db_manager.is_connected() else "disconnected",
        "version": "2.0.0"
    }

@app.get("/test-db")
async def test_database():
    """Endpoint para testar a conexão com o banco"""
    if not db_manager.is_connected():
        return {"status": "no_connection", "message": "Database pool not initialized"}
    
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval('SELECT NOW()')
            return {"status": "success", "timestamp": str(result)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/db-info")
async def database_info():
    """Endpoint para obter informações sobre o banco"""
    if not db_manager.is_connected():
        return {"status": "disconnected", "message": "No database connection available"}
    
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Informações básicas
            version = await conn.fetchval('SELECT version()')
            current_db = await conn.fetchval('SELECT current_database()')
            user = await conn.fetchval('SELECT current_user')
            
            # Verificar se a tabela existe
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
                "version": version.split()[0:2],  # Mostra só PostgreSQL X.X
                "table_lead_profiles_exists": table_exists
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
