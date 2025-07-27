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
        logger.info(f"📊 Scores radar: {radar_scores}")
        
        # 2. Generate opportunities
        try:
            logger.info("💡 Gerando oportunidades...")
            opportunities_result = await opportunityTracker.run(deps=form_data)
            if not opportunities_result or not opportunities_result.output:
                raise Exception("OpportunityTracker retornou resultado vazio")
            
            opportunities = opportunities_result.output.opportunities
            logger.info(f"💡 Geradas {len(opportunities)} oportunidades")
        except Exception as opp_error:
            logger.error(f"❌ Erro ao gerar oportunidades: {opp_error}")
            # Fallback com oportunidades padrão
            from schemas import Opportunity
            opportunities = [
                Opportunity(
                    titulo="Automação de Processos Básicos",
                    descricao=f"Implementar soluções de automação para reduzir tarefas manuais na área de {form_data.p5_critical_area}",
                    roi_estimado="150-200%",
                    timeline="3-6 meses",
                    investimento="R$ 25.000 - R$ 50.000"
                ),
                Opportunity(
                    titulo="Análise de Dados Inteligente",
                    descricao="Desenvolver dashboards e relatórios automatizados para melhorar a tomada de decisão",
                    roi_estimado="120-180%",
                    timeline="2-4 meses", 
                    investimento="R$ 15.000 - R$ 35.000"
                ),
                Opportunity(
                    titulo="Chatbot de Atendimento",
                    descricao="Implementar assistente virtual para automatizar o atendimento inicial aos clientes",
                    roi_estimado="100-150%",
                    timeline="1-3 meses",
                    investimento="R$ 10.000 - R$ 25.000"
                )
            ]
        
        # 3. Generate introduction - CORRIGIDO
        try:
            logger.info("🔍 Gerando introdução de pesquisa de mercado...")
            introduction_result = await researchAgent.run("Faça uma introdução para o relatorio com um panorama da IA para empresas como essa", deps=form_data)
            introduction_output = introduction_result.output if introduction_result and introduction_result.output else None
            
            if not introduction_output:
                raise Exception("ResearchAgent retornou resultado vazio")
                
            logger.info("✅ Introdução gerada com sucesso")
            logger.info(f"Introdução (primeiros 100 chars): {introduction_output[:100]}...")
        except Exception as intro_error:
            logger.error(f"❌ Erro ao gerar introdução: {intro_error}")
            # Fallback com introdução personalizada
            introduction_output = f"O setor de {form_data.p1_sector} está passando por uma transformação digital acelerada, especialmente para empresas de {form_data.p2_company_size}. A implementação de inteligência artificial neste segmento apresenta oportunidades significativas de otimização, redução de custos e crescimento sustentável. Com o gargalo atual em {form_data.p4_main_pain}, há potencial imediato para soluções que automatizem processos e melhorem a eficiência operacional."
        
        # 4. Consolidate data for the report - ESTRUTURA CORRIGIDA
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

        # 5. Save to database (se disponível)
        if db_manager.is_connected():
            try:
                await save_to_database(form_data, report_data)
                logger.info("✅ Dados salvos no banco com sucesso")
            except Exception as db_error:
                logger.warning(f"⚠️  Erro ao salvar no banco: {db_error}")
                # Não falha a API se não conseguir salvar
        else:
            logger.warning("⚠️  Executando sem salvar no banco de dados")

        # 6. Render HTML report - DADOS CORRETOS PARA O TEMPLATE - CORRIGIDO
        try:
            template_data = report_data.dict()
            logger.info(f"🔍 DEBUG - Keys disponíveis em template_data: {list(template_data.keys())}")
            logger.info(f"🔍 DEBUG - template_data completo: {template_data}")
        except Exception as dict_error:
            logger.error(f"❌ Erro ao converter report_data para dict: {dict_error}")
            # Fallback manual
            template_data = {}
        
        # Garantir que os dados estão na estrutura correta para o template - PROTEÇÃO CONTRA KeyError
        template_data_fixed = {
            "empresa": template_data.get("empresa", {"nome": form_data.name or "Sua Empresa"}),
            "introduction": template_data.get("introduction", introduction_output),  # USAR A VARIÁVEL DIRETA
            "scores_radar": template_data.get("scores_radar", radar_scores.dict()),  # USAR A VARIÁVEL DIRETA
            "score_final": template_data.get("score_final", final_score),  # USAR A VARIÁVEL DIRETA
            "relatorio_oportunidades": template_data.get("relatorio_oportunidades", []),
            "relatorio_riscos": template_data.get("relatorio_riscos", []),
            "data_geracao": None,  # Será preenchido pelo render_report
            "ano_atual": None      # Será preenchido pelo render_report
        }
        
        logger.info(f"📊 Dados finais para template:")
        logger.info(f"   - score_final: {template_data_fixed['score_final']}")
        logger.info(f"   - introduction (100 chars): {str(template_data_fixed['introduction'])[:100]}...")
        logger.info(f"   - scores_radar keys: {list(template_data_fixed['scores_radar'].keys()) if isinstance(template_data_fixed['scores_radar'], dict) else 'NOT_DICT'}")
        logger.info(f"   - oportunidades count: {len(template_data_fixed['relatorio_oportunidades'])}")
        
        html_content = renderizar_relatorio(template_data_fixed)
        logger.info("✅ Relatório HTML gerado com sucesso")
        
        # 7. Convert form_data to dict for webhook
        form_data_dict = form_data.model_dump(by_alias=True)
        
        # 8. Send to webhook in background (não bloqueia a resposta)
        logger.info("🔄 Enviando dados para webhook em background...")
        
        # Usar try/except para não quebrar a API se o webhook falhar
        try:
            asyncio.create_task(
                convert_html_to_pdf_and_send_webhook(form_data_dict, html_content)
            )
        except Exception as webhook_error:
            logger.warning(f"⚠️  Erro ao iniciar task do webhook: {webhook_error}")

        # 9. Return HTML immediately
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
                    json.dumps(report_data.scores_radar),
                    json.dumps(report_data)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)