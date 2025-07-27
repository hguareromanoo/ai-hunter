import jinja2
import os
import datetime

def renderizar_relatorio(dados_diagnostico: dict) -> str:
    """
    Renderiza o template HTML do relatório com os dados fornecidos.

    Args:
        dados_diagnostico: Um dicionário contendo todos os dados para o template.

    Returns:
        O conteúdo HTML do relatório renderizado como uma string.
    """
    # O searchpath agora aponta para o diretório onde o script está localizado.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_loader = jinja2.FileSystemLoader(searchpath=script_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('relatorio_template.html')

    # Adiciona a data de geração e o ano atual aos dados do template
    dados_completos = dados_diagnostico.copy()
    dados_completos['data_geracao'] = datetime.datetime.now().strftime("%d/%m/%Y")
    dados_completos['ano_atual'] = datetime.datetime.now().year

    # Garante que scores_radar existe e tem a estrutura correta
    if 'scores_radar' not in dados_completos or not isinstance(dados_completos['scores_radar'], dict):
        print("⚠️  WARNING: scores_radar não encontrado ou inválido, usando valores padrão")
        dados_completos['scores_radar'] = {
            'automation_readiness': 0,
            'digital_maturity': 0,
            'investment_capacity': 0,
            'urgency_level': 0,
            'pain_intensity': 0
        }

    # DEBUG: Log dos dados que estão sendo passados para o template
    print(f"DEBUG - Score final para template: {dados_completos.get('score_final', 'NÃO ENCONTRADO')}")
    print(f"DEBUG - Introduction: {dados_completos.get('introduction', 'NÃO ENCONTRADO')[:100] if dados_completos.get('introduction') else 'VAZIO'}...")
    print(f"DEBUG - Scores radar: {dados_completos.get('scores_radar', 'NÃO ENCONTRADO')}")
    print(f"DEBUG - Empresa: {dados_completos.get('empresa', 'NÃO ENCONTRADO')}")
    print(f"DEBUG - Oportunidades: {len(dados_completos.get('relatorio_oportunidades', []))} encontradas")
    
    # Renderiza o template com os dados
    return template.render(dados_completos)

if __name__ == "__main__":
    # Exemplo de uso standalone para testes
    dados_teste = {
        "empresa": {"nome": "Empresa Teste"},
        "introduction": "Esta é uma introdução de teste para verificar se o template está funcionando corretamente.",
        "score_final": 7.5,
        "scores_radar": {
            "automation_readiness": 80,
            "digital_maturity": 65,
            "investment_capacity": 70,
            "urgency_level": 85,
            "pain_intensity": 75
        },
        "relatorio_oportunidades": [
            {
                "titulo": "Automação de Processos",
                "description": "Implementar RPA para automatizar tarefas repetitivas",
                "roi": "200%",
                "priority": "alta",
                "case": "Empresa X reduziu 40% do tempo em processos manuais"
            }
        ],
        "relatorio_riscos": [
            {
                "titulo": "Segurança de Dados",
                "descricao": "Necessidade de implementar medidas de segurança adequadas"
            }
        ]
    }
    
    html_output = renderizar_relatorio(dados_teste)
    
    # Salva o resultado em um arquivo para visualização
    with open('teste_template.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print("✅ Template de teste gerado: teste_template.html")