import requests
import json
import os
import time
from datetime import datetime

# Configurações
RENDER_URL = "https://ai-hunter.onrender.com/api/v2/diagnostico"
LOCAL_URL = "http://localhost:8001/api/v2/diagnostico"

# Use RENDER_URL por padrão, LOCAL_URL para testes locais
API_URL = RENDER_URL

# Mock data baseado no LeadProfileInput schema
test_form_data = {
    "name": "Joao Silva",
    "email": "joao.silva@empresa.com",
    "phone": "11987654321",
    "sector": "Tecnologia e Software",
    "company_size": "11-50 funcionários",
    "role": "CEO/Founder",
    "main_pain": "Falta de automação nos processos internos da empresa",
    "critical_area": "Vendas/Marketing",
    "pain_quantification": "Perdemos cerca de 20 horas semanais em tarefas manuais que poderiam ser automatizadas.",
    "digital_maturity": "Usamos ferramentas básicas de produtividade (CRM simples, e-mail)",
    "investment_capacity": "R$ 30.001 - R$ 100.000 (investimento estruturado)",
    "urgency": "Média - Gostaríamos de implementar nos próximos 6 meses"
}

# Headers
headers = {
    "Content-Type": "application/json",
    "User-Agent": "TestScript/1.0"
}

def test_health_check():
    """Testa se a API está funcionando"""
    try:
        health_url = API_URL.replace("/api/v2/diagnostico", "/health")
        print(f"🔍 Testando health check: {health_url}")
        
        response = requests.get(health_url, timeout=30)
        if response.status_code == 200:
            print("✅ Health check passou!")
            print(f"   Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_root_endpoint():
    """Testa o endpoint raiz"""
    try:
        root_url = API_URL.replace("/api/v2/diagnostico", "/")
        print(f"🔍 Testando endpoint raiz: {root_url}")
        
        response = requests.get(root_url, timeout=30)
        if response.status_code == 200:
            print("✅ Endpoint raiz funcionando!")
            print(f"   Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no endpoint raiz: {e}")
        return False

def test_diagnostico_endpoint():
    """Testa o endpoint principal de diagnóstico"""
    try:
        print(f"🚀 Testando diagnóstico: {API_URL}")
        print(f"📋 Dados de teste: {test_form_data['name']} - {test_form_data['email']}")
        
        start_time = time.time()
        
        response = requests.post(
            API_URL, 
            data=json.dumps(test_form_data), 
            headers=headers,
            timeout=120  # 2 minutos de timeout para o diagnóstico
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Tempo de resposta: {duration:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📁 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            if 'text/html' in response.headers.get('Content-Type', ''):
                # Salva o HTML recebido
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f'teste_diagnostico_{timestamp}.html'
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                abs_path = os.path.abspath(filename)
                file_size = len(response.text.encode('utf-8'))
                
                print("✅ Diagnóstico realizado com sucesso!")
                print(f"   📄 HTML salvo em: {abs_path}")
                print(f"   📏 Tamanho do arquivo: {file_size:,} bytes")
                print(f"   🔗 Para visualizar: file://{abs_path}")
                
                # Verifica se contém elementos essenciais
                html_content = response.text.lower()
                checks = {
                    "título": "diagnóstico" in html_content or "relatório" in html_content,
                    "nome_cliente": test_form_data['name'].lower() in html_content,
                    "gráfico_radar": "radar" in html_content or "chart" in html_content,
                    "oportunidades": "oportunidade" in html_content,
                    "css": "<style" in html_content or "stylesheet" in html_content
                }
                
                print("\n🔍 Verificações de conteúdo:")
                for check, passed in checks.items():
                    status = "✅" if passed else "⚠️"
                    print(f"   {status} {check}: {'OK' if passed else 'Não encontrado'}")
                
                return True
            else:
                print("⚠️  Resposta não é HTML:")
                try:
                    print(json.dumps(response.json(), indent=2))
                except:
                    print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                return False
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição (mais de 2 minutos)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - verifique se o servidor está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def run_complete_test():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES DA API AI-HUNTER")
    print("=" * 50)
    print(f"🎯 URL alvo: {API_URL}")
    print(f"🕐 Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Teste 1: Health Check
    print("1️⃣  TESTE: Health Check")
    results['health'] = test_health_check()
    print()
    
    # Teste 2: Root Endpoint
    print("2️⃣  TESTE: Root Endpoint")
    results['root'] = test_root_endpoint()
    print()
    
    # Teste 3: Diagnóstico Principal
    print("3️⃣  TESTE: Diagnóstico (Principal)")
    results['diagnostico'] = test_diagnostico_endpoint()
    print()
    
    # Resumo
    print("📋 RESUMO DOS TESTES")
    print("=" * 30)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {test_name.upper()}: {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM! API está funcionando perfeitamente.")
    elif results.get('diagnostico'):
        print("✅ Funcionalidade principal (diagnóstico) está funcionando.")
    else:
        print("⚠️  Problemas detectados - verifique os logs acima.")
    
    return results

if __name__ == "__main__":
    print("🤖 AI-Hunter API Test Script")
    print("Pressione Ctrl+C para cancelar a qualquer momento\n")
    
    try:
        # Opção para escolher URL
        print("Escolha o ambiente:")
        print("1 - Render.com (produção)")
        print("2 - Local (desenvolvimento)")
        
        choice = input("Digite sua escolha (1 ou 2, padrão=1): ").strip()
        
        if choice == "2":
            API_URL = LOCAL_URL
            print(f"🏠 Usando ambiente local: {API_URL}")
        else:
            API_URL = RENDER_URL
            print(f"☁️  Usando Render.com: {API_URL}")
        
        print()
        
        # Executa os testes
        results = run_complete_test()
        
        # Pergunta se quer executar novamente
        while True:
            again = input("\n🔄 Executar testes novamente? (s/N): ").strip().lower()
            if again in ['s', 'sim', 'y', 'yes']:
                print("\n" + "="*60)
                results = run_complete_test()
            else:
                break
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Testes cancelados pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    print("\n👋 Teste finalizado!")