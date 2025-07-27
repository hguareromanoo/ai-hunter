from models import calculate_scores, get_points
from schemas import LeadProfileInput
import logging

# Configurar logging para ver os detalhes
logging.basicConfig(level=logging.INFO)

# Dados de teste exatos do seu teste.py
test_data = LeadProfileInput(
    name="Joao Silva",
    email="joao.silva@empresa.com",
    phone="11987654321",
    sector="Tecnologia e Software",
    company_size="11-50 funcionários",
    role="CEO/Founder",
    main_pain="Falta de automação nos processos internos da empresa",
    critical_area="Vendas/Marketing",
    pain_quantification="Perdemos cerca de 20 horas semanais em tarefas manuais que poderiam ser automatizadas.",
    digital_maturity="Usamos ferramentas básicas de produtividade (CRM simples, e-mail)",
    investment_capacity="R$ 30.001 - R$ 100.000 (investimento estruturado)",
    urgency="Média - Gostaríamos de implementar nos próximos 6 meses"
)

print("🧪 TESTE DE SCORING DETALHADO")
print("=" * 40)

print(f"📋 Dados de entrada:")
print(f"   Role: {test_data.p3_role}")
print(f"   Pain: {test_data.p4_main_pain}")
print(f"   Pain Quantification: {test_data.p6_pain_quant}")
print(f"   Digital Maturity: {test_data.p7_digital_maturity}")
print(f"   Investment: {test_data.p8_investment}")
print(f"   Urgency: {test_data.p9_urgency}")
print()

print("🔍 Testando pontuação individual:")
print(f"   Role: {get_points('role', test_data.p3_role)}")
print(f"   Pain: {get_points('pain', test_data.p4_main_pain)}")
print(f"   QuantifyPain: {get_points('quantifyPain', test_data.p6_pain_quant)}")
print(f"   Maturity: {get_points('maturity', test_data.p7_digital_maturity)}")
print(f"   Investment: {get_points('investment', test_data.p8_investment)}")
print(f"   Urgency: {get_points('urgency', test_data.p9_urgency)}")
print()

print("📊 Calculando scores completos...")
radar_scores, final_score = calculate_scores(test_data)

print(f"✅ RESULTADO FINAL:")
print(f"   Score Final: {final_score}")
print(f"   Radar Scores: {radar_scores.dict()}")