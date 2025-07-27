import os
import json
import datetime
import jinja2
import logging

logger = logging.getLogger(__name__)

def renderizar_relatorio(dados_diagnostico: dict) -> str:
    """
    Renderiza o template HTML do relatório com os dados fornecidos.

    Args:
        dados_diagnostico: Um dicionário contendo todos os dados para o template.

    Returns:
        O conteúdo HTML do relatório renderizado como uma string.
    """
    
    logger.info("🎨 INICIANDO RENDERIZAÇÃO DO RELATÓRIO")
    logger.info(f"📋 Dados recebidos: {json.dumps(dados_diagnostico, indent=2, ensure_ascii=False)}")
    
    try:
        # O searchpath agora aponta para o diretório onde o script está localizado.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_loader = jinja2.FileSystemLoader(searchpath=script_dir)
        template_env = jinja2.Environment(loader=template_loader)
        
        logger.info(f"📂 Procurando template em: {script_dir}")
        
        # Verificar se o template existe
        template_path = os.path.join(script_dir, 'relatorio_template.html')
        if not os.path.exists(template_path):
            logger.error(f"❌ Template não encontrado: {template_path}")
            raise FileNotFoundError(f"Template não encontrado: {template_path}")
        
        template = template_env.get_template('relatorio_template.html')
        logger.info("✅ Template carregado com sucesso")

        # Adiciona a data de geração e o ano atual aos dados do template
        dados_completos = dados_diagnostico.copy()
        dados_completos['data_geracao'] = datetime.datetime.now().strftime("%d/%m/%Y")
        dados_completos['ano_atual'] = datetime.datetime.now().year

        # Log dos dados que serão enviados para o template
        logger.info("📊 DADOS PARA O TEMPLATE:")
        logger.info(f"  📈 Score Final: {dados_completos.get('score_final', 'MISSING')}")
        
        scores_radar = dados_completos.get('scores_radar', {})
        if scores_radar:
            logger.info("  📊 Scores Radar:")
            for key, value in scores_radar.items():
                logger.info(f"    {key}: {value}")
        else:
            logger.error("❌ scores_radar está vazio ou ausente!")
        
        empresa = dados_completos.get('empresa', {})
        logger.info(f"  🏢 Empresa: {empresa}")
        
        oportunidades = dados_completos.get('relatorio_oportunidades', [])
        logger.info(f"  💡 Oportunidades: {len(oportunidades)} encontradas")
        
        # Renderiza o template com os dados
        logger.info("🔄 Renderizando template...")
        html_content = template.render(dados_completos)
        
        logger.info(f"✅ Template renderizado com sucesso! Tamanho: {len(html_content)} caracteres")
        
        # Verificar se os scores aparecem no HTML gerado
        if f"score_final" in html_content:
            logger.info("✅ score_final encontrado no HTML gerado")
        else:
            logger.warning("⚠️ score_final NÃO encontrado no HTML gerado")
            
        if "scores_radar.poder_de_decisao" in html_content:
            logger.info("✅ scores_radar encontrado no HTML gerado")
        else:
            logger.warning("⚠️ scores_radar NÃO encontrado no HTML gerado")
        
        return html_content
        
    except jinja2.TemplateNotFound as e:
        logger.error(f"❌ Template não encontrado: {e}")
        raise
    except jinja2.TemplateSyntaxError as e:
        logger.error(f"❌ Erro de sintaxe no template: {e}")
        logger.error(f"   Linha {e.lineno}: {e.message}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao renderizar relatório: {str(e)}")
        logger.error(f"   Tipo do erro: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        raise

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
        "introduction": "Esta é uma introdução de teste para o setor de tecnologia. A implementação de IA neste setor oferece oportunidades significativas para empresas que buscam inovação e eficiência operacional.",
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

    print("🧪 TESTANDO RENDERIZAÇÃO COM DADOS MOCK")
    print("=" * 50)
    
    # Renderiza o relatório com os dados mock
    try:
        html_output = renderizar_relatorio(mock_data)

        # Salva o resultado no mesmo diretório do script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_filename = os.path.join(script_dir, 'relatorio_final.html')
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_output)

        print(f"✅ Relatório gerado com sucesso!")
        print(f"📄 Arquivo salvo: {output_filename}")
        print(f"📊 Tamanho: {len(html_output)} caracteres")
        print(f"🌐 Abra o arquivo em seu navegador para visualizar.")
        
        # Verificar se os dados estão no HTML
        if str(mock_data['score_final']) in html_output:
            print("✅ Score final encontrado no HTML")
        else:
            print("❌ Score final NÃO encontrado no HTML")
            
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()
