import requests
import json
import os
import base64
import tempfile
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

async def convert_html_to_pdf_and_send_webhook(form_data: dict, html_content: str):
    """
    Envia dados completos (form_data + HTML) para o webhook
    """
    webhook_url = "https://flows.profissionalai.com.br/webhook-test/6e2f0fa5-6cc5-4415-943c-7d7b9a6a7719"
    
    try:
        logger.info("📤 Preparando dados para envio ao webhook...")
        
        # Prepara os dados completos para envio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Monta o JSON completo com form_data e HTML
        payload = {
            "form_data": form_data,
            "html_content": html_content,
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
        
        logger.info("📤 Enviando dados completos (form_data + HTML) para o webhook...")
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
        logger.error(f"❌ Erro ao enviar dados para webhook: {str(e)}")
        return False
