import requests
import json
import os
from datetime import datetime
import asyncio
import tempfile
import base64
from weasyprint import HTML, CSS

# URL of the new v2 FastAPI endpoint
url = "https://ai-hunter.onrender.com/api/v2/diagnostico"
url2="http://localhost:8000/api/v2/diagnostico"

# Sample form data matching the new LeadProfileInput schema, using aliases
form_data = {
    "name": "Maria Silva",
    "email": "maria.silva@corporate.com",
    "phone": "11999998888",
    "sector": "Serviços Profissionais (Consultoria, Advocacia, etc.)",
    "company_size": "51-250 funcionários",
    "role": "Gerente/Coordenador(a)",
    "main_pain": "Processos manuais e repetitivos que consomem muito tempo da equipe",
    "critical_area": "Financeiro/Cobrança",
    "pain_quantification": "Nossa equipe gasta umas 30 horas por mês em tarefas de faturamento manual.",
    "digital_maturity": "Usamos relatórios básicos e planilhas (Excel/Google Sheets)",
    "investment_capacity": "Até R$ 30.000 (projeto piloto/teste)",
    "urgency": "Alta - Gostaríamos de agir nos próximos 3 meses"
}

# Headers
headers = {
    "Content-Type": "application/json"
}

async def convert_html_to_pdf_and_send(form_data, html_content):
    webhook_url = "https://flows.profissionalai.com.br/webhook-test/6e2f0fa5-6cc5-4415-943c-7d7b9a6a7719"
    
    try:
        # Cria arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_temp:
            pdf_file = pdf_temp.name
        
        print(f"Convertendo HTML para PDF usando WeasyPrint...")
        
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
        """)
        
        # Converte HTML para PDF usando WeasyPrint
        html_doc = HTML(string=html_content)
        html_doc.write_pdf(pdf_file, stylesheets=[additional_css])
        
        print(f"PDF criado: {pdf_file}")
        
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
        
        print("Enviando dados completos (form_data + HTML + PDF) para o webhook...")
        response = requests.post(webhook_url, data=json.dumps(payload), headers=json_headers)
        
        if response.status_code == 200:
            print("Dados enviados com sucesso!")
            print(f"Resposta: {response.text}")
        else:
            print(f"Erro ao enviar: {response.status_code}")
            print(f"Resposta: {response.text}")
        
        # Remove arquivo temporário
        os.unlink(pdf_file)
        print("Arquivo temporário removido.")
        
        return True
            
    except Exception as e:
        print(f"Erro ao converter HTML para PDF e enviar: {str(e)}")
        # Remove arquivo temporário em caso de erro
        try:
            if 'pdf_file' in locals():
                os.unlink(pdf_file)
        except:
            pass
        return False

# Make the POST request
try:
    print(f"Sending request to {url}...")
    response = requests.post(url, data=json.dumps(form_data), headers=headers)
    response.raise_for_status()

    if 'text/html' in response.headers.get('Content-Type', ''):
        # Salva o HTML localmente para backup
        output_filename = 'final_report_from_api_v2.html'
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        abs_path = os.path.abspath(output_filename)
        print(f"\n✅ Success! Report generated from live API data.")
        print(f"   Saved to: {abs_path}")
        
        # Converte para PDF e envia para o webhook com os dados do formulário
        print("\nConvertendo para PDF e enviando dados completos para webhook...")
        asyncio.run(convert_html_to_pdf_and_send(form_data, response.text))
        
    else:
        print("Received a non-HTML response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\n❌ An error occurred during the request: {e}")
    print("   Please ensure the FastAPI server is running: uvicorn ai-hunter-backend.main:app --reload")

if __name__ == "__main__":
    with open('final_report_from_api_v2.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    asyncio.run(convert_html_to_pdf_and_send(form_data, html_content))