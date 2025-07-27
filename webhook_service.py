import requests
import json
import os
import base64
import tempfile
from datetime import datetime
from weasyprint import HTML, CSS
import logging

logger = logging.getLogger(__name__)

async def convert_html_to_pdf_and_send_webhook(form_data: dict, html_content: str):
    """
    Converte HTML para PDF usando WeasyPrint e envia dados completos para o webhook
    """
    webhook_url = "https://flows.profissionalai.com.br/webhook-test/6e2f0fa5-6cc5-4415-943c-7d7b9a6a7719"
    
    try:
        # Cria arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_temp:
            pdf_file = pdf_temp.name
        
        logger.info("🔄 Convertendo HTML para PDF usando WeasyPrint...")
        
        # CSS adicional para melhorar a formatação do PDF
        additional_css = CSS(string="""
            @page {
                size: A4;
                margin: 0.75in;
            }
            body {
                font-family: Arial, sans-serif;
                line-height: 1.4;
            }
            .chart-container {
                page-break-inside: avoid;
            }
            h1, h2, h3 {
                page-break-after: avoid;
            }
            table {
                page-break-inside: avoid;
            }
        """)
        
        # Converte HTML para PDF usando WeasyPrint
        html_doc = HTML(string=html_content)
        html_doc.write_pdf(pdf_file, stylesheets=[additional_css])
        
        logger.info(f"✅ PDF criado: {pdf_file}")
        
        # Lê o arquivo PDF como bytes e converte para base64
        with open(pdf_file, 'rb') as file:
            pdf_content = file.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Prepara os dados completos para envio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_diagnostico_{timestamp}.pdf"
        
        # Monta o JSON completo com form_data, html e PDF
        payload = {
            "form_data": form_data,
            "html_content": html_content,
            "pdf_data": {
                "filename": filename,
                "content": pdf_base64,
                "content_type": "application/pdf"
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "timestamp": timestamp,
                "client_name": form_data.get("name", "Unknown"),
                "client_email": form_data.get("email", "Unknown")
            }
        }
        
        # Headers para JSON
        json_headers = {
            "Content-Type": "application/json"
        }
        
        logger.info("📤 Enviando dados completos (form_data + HTML + PDF) para o webhook...")
        response = requests.post(webhook_url, data=json.dumps(payload), headers=json_headers)
        
        if response.status_code == 200:
            logger.info("✅ Dados enviados com sucesso para o webhook!")
            logger.info(f"Resposta: {response.text}")
            return True
        else:
            logger.error(f"❌ Erro ao enviar para webhook: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao converter HTML para PDF e enviar: {str(e)}")
        return False
    
    finally:
        # Remove arquivo temporário
        try:
            if 'pdf_file' in locals():
                os.unlink(pdf_file)
                logger.info("🗑️ Arquivo temporário removido.")
        except Exception as e:
            logger.error(f"⚠️ Erro ao remover arquivo temporário: {e}")