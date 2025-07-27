import os
import json
import datetime
import jinja2
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

    # Renderiza o template com os dados
    return template.render(dados_completos)

if __name__ == "__main__":
    # Dados Mock para teste do relatório
    # Simula o output que viria do diagnóstico
    mock_data = {
        "empresa": {
            "nome": "Nexus Corp",
            "setor": "Tecnologia",
            "tamanho": "50-200 funcionários"
        },
        "scores_radar": {
            "poder_de_decisao": 8.8,
            "cultura_e_talentos": 6.5,
            "processos_e_automacao": 9.2,
            "inovacao_de_produtos": 7.1,
            "inteligencia_de_mercado": 5.5
        },
        "score_final": 7.4, # Altere este valor para testar os diferentes CTAs
        "relatorio_oportunidades": [
            {
                "titulo": "Inteligência de Mercado Preditiva",
                "description": "Implementar um sistema de IA para análise preditiva de tendências pode antecipar movimentos de concorrentes e identificar novas oportunidades de receita antes que se tornem óbvias.",
                "roi": "Potencial de +15% de market share em 2 anos.",
                "priority": "alta",
                "case": "A Empresa 'AlfaTech' usou uma abordagem similar e conseguiu prever uma mudança de mercado, capturando 50.000 novos clientes antes dos concorrentes."
            },
            {
                "titulo": "Capacitação Contínua em IA para Equipes",
                "description": "Para elevar o score de Cultura e Talentos, invista em programas de formação contínua. Workshops práticos sobre ferramentas de IA generativa podem aumentar a eficiência e a inovação em todos os departamentos.",
                "roi": "Aumento de 25% na produtividade interna.",
                "priority": "media",
                "case": "A 'InovaCorp' implementou workshops de IA e viu uma redução de 40% no tempo de execução de tarefas administrativas, além de um aumento no engajamento dos funcionários."
            },
            {
                "titulo": "Otimização da Experiência do Cliente com Chatbots",
                "description": "Aproveite seu alto score em Processos para implementar um chatbot avançado no atendimento ao cliente. Isso pode reduzir o tempo de resposta e aumentar a satisfação.",
                "roi": "Redução de 30% nos custos de suporte ao cliente.",
                "priority": "baixa",
                "case": "A 'Soluções Rápidas Ltda' integrou um chatbot inteligente e conseguiu resolver 70% das solicitações de clientes sem intervenção humana, melhorando o NPS em 10 pontos."
            }
        ],
        "relatorio_riscos": [
            {
                "titulo": "Dependência de Processos Manuais em Análise de Dados",
                "descricao": "A falta de automação na coleta e análise de dados de mercado pode levar a decisões baseadas em informações desatualizadas, colocando a empresa em desvantagem competitiva."
            },
            {
                "titulo": "Risco de Obsolescência Tecnológica",
                "descricao": "O ritmo acelerado da IA significa que as ferramentas e técnicas de hoje podem estar desatualizadas amanhã. É crucial criar um processo para avaliar e adotar novas tecnologias de forma ágil."
            }
        ]
    }

    # Testando diferentes cenários de score_final
    # Descomente uma das linhas abaixo para gerar um relatório com um CTA diferente
    # mock_data['score_final'] = 9.0  # Mentor[IA]
    # mock_data['score_final'] = 8.0  # Founders Lendários
    mock_data['score_final'] = 6.8  # Formação Lendária
    # mock_data['score_final'] = 4.5  # Agentes Lendários
    # mock_data['score_final'] = 1.5  # Ebook Melhores Prompts

    # Renderiza o relatório com os dados mock
    html_output = renderizar_relatorio(mock_data)

    # Salva o resultado no mesmo diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, 'relatorio_final.html')
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"Relatório gerado com sucesso!")
    print(f"Abra o arquivo '{output_filename}' em seu navegador para visualizar.")
