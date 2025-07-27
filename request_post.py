import requests
import json
import os

# URL of the new v2 FastAPI endpoint
url = "http://0.0.0.0:8001///api/v2/diagnostico"

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

# Make the POST request
try:
    print(f"Sending request to {url}...")
    response = requests.post(url, data=json.dumps(form_data), headers=headers)
    response.raise_for_status()

    if 'text/html' in response.headers.get('Content-Type', ''):
        output_filename = 'final_report_from_api_v2.html'
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        abs_path = os.path.abspath(output_filename)
        print(f"\n✅ Success! Report generated from live API data.")
        print(f"   Saved to: {abs_path}")
        print("\nTo view the result, open the file in your browser.")
        
    else:
        print("Received a non-HTML response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\n❌ An error occurred during the request: {e}")
    print("   Please ensure the FastAPI server is running: uvicorn ai-hunter-backend.main:app --reload")
