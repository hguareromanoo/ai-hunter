# Product Requirements Document (PRD)
## Diagnóstico IA Hunter - MVP Hackathon

---

## 📋 Document Overview

**Product Name**: Diagnóstico IA Hunter  
**Version**: MVP 1.0  
**Document Version**: 1.0  
**Last Updated**: July 26, 2025  
**Owner**: Equipe 36 - Hackathon  
**Development Timeline**: 24 horas  

---

## 🎯 Executive Summary

O Diagnóstico IA Hunter é uma ferramenta de qualificação inteligente de leads B2B que automatiza o processo de diagnóstico de prontidão para IA nas empresas. O sistema coleta informações através de um questionário estratégico, processa os dados com agentes de IA especializados e gera relatórios personalizados em PDF, qualificando leads e educando o mercado simultaneamente.

---

## 🔍 Problem Statement

### Current State
- Academia Lendária recebe leads interessados em IA sem direcionamento claro
- Processo de qualificação manual, genérico e demorado
- Prospects com expectativas irreais sobre aplicações de IA
- Alto CAC e baixa taxa de conversão de leads

### Target State
- Qualificação automatizada e inteligente de leads
- Diagnósticos personalizados baseados em perfil empresarial
- Educação consultiva do mercado sobre oportunidades de IA
- Pipeline de vendas otimizado com leads pré-qualificados

---

## 👥 Target Users

### Primary Users

#### 1. CEO/Founder (Tomador de Decisão)
- **Demografia**: 35-55 anos, empresas 50-500 funcionários
- **Pain Points**: Pressão por inovação, incerteza sobre ROI de IA
- **Goals**: Vantagem competitiva, otimização de resultados
- **Usage Context**: Busca por soluções estratégicas de transformação

#### 2. CTO/Diretor de TI (Avaliador Técnico)
- **Demografia**: 30-50 anos, background técnico sólido
- **Pain Points**: Ceticismo sobre promessas de IA, falta de casos práticos
- **Goals**: Implementações viáveis e com ROI comprovado
- **Usage Context**: Validação técnica de oportunidades

#### 3. Diretor de Marketing/Inovação (Explorador)
- **Demographics**: 28-45 anos, foco em diferenciação
- **Pain Points**: Necessidade de inovação constante, pressão por resultados
- **Goals**: Soluções disruptivas, engajamento diferenciado
- **Usage Context**: Busca por novas ferramentas e abordagens

### Secondary Users
- **Academia Lendária Sales Team**: Usuários dos relatórios para follow-up
- **Academia Lendária Marketing**: Análise de leads e otimização de campanhas

---

## 📊 Success Metrics

### Primary KPIs
- **Lead Qualification Rate**: >70% dos formulários completados
- **Conversion to Meeting**: >15% agendamentos pós-diagnóstico
- **Lead Quality Score**: Correlação score vs. fechamento >0.7
- **Time to Qualify**: <5 minutos por diagnóstico

### Secondary KPIs
- **User Engagement**: Tempo médio no relatório >3 minutos
- **Content Quality**: NPS do diagnóstico >70
- **Distribution**: Taxa de compartilhamento do PDF >40%
- **Pipeline Impact**: Aumento de 40% na taxa de conversão comercial

---

## ⚙️ Technical Architecture

### System Overview
```
Frontend (Landing + Form) → Backend (FastAPI) → AI Agents → PDF Generator → Email/Download
                                    ↓
                              Database (SQLite/PostgreSQL)
```

### Technology Stack

#### Frontend
- **Framework**: Vanilla HTML/CSS/JavaScript
- **Styling**: Tailwind CSS via CDN
- **Deployment**: Vercel/Netlify
- **Requirements**: Responsive, mobile-first, <3s load time

#### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **AI Integration**: OpenAI GPT-4 API
- **PDF Generation**: WeasyPrint/ReportLab
- **Deployment**: Railway/Render

#### Infrastructure
- **Hosting**: Cloud-native, auto-scaling
- **Database**: Managed PostgreSQL
- **File Storage**: Local (MVP) → S3-compatible
- **Monitoring**: Basic logging and error tracking

---

## 🎨 User Experience Design

### User Journey
1. **Discovery**: Usuário acessa via link/marketing
2. **Engagement**: Landing page com proposta de valor clara
3. **Input**: Formulário multi-step (8-12 perguntas)
4. **Processing**: Loading com expectativas claras
5. **Output**: Relatório personalizado + CTA
6. **Follow-up**: Opção de agendamento/contato

### UI/UX Requirements

#### Landing Page
- **Hero Section**: Proposta de valor em 5 segundos
- **Social Proof**: Logos, depoimentos, cases
- **CTA Primary**: "Fazer Diagnóstico Gratuito"
- **Trust Elements**: Tempo estimado, gratuito, sem compromisso

#### Formulário
- **Format**: Multi-step com progress bar
- **Validation**: Real-time, mensagens claras
- **UX**: Uma pergunta por tela (mobile), 2-3 (desktop)
- **Completion Time**: 3-5 minutos máximo

#### Relatório
- **Layout**: Visual, scannable, profissional
- **Hierarchy**: Score → Oportunidades → Próximos Passos
- **Branding**: Academia Lendária prominente
- **Actions**: Download PDF, Agendar Reunião, Compartilhar

---

## 📋 Functional Requirements

### FR-01: Formulário de Diagnóstico

#### Description
Sistema de coleta de dados sobre perfil empresarial, dores, objetivos e maturidade digital.

#### Acceptance Criteria
- [ ] Formulário multi-step com 10 perguntas obrigatórias
- [ ] Progress bar visual do preenchimento
- [ ] Validação em tempo real dos campos
- [ ] Responsivo (mobile-first)
- [ ] Tempo de preenchimento <5 minutos
- [ ] Salvamento automático de progresso
- [ ] Envio via API REST para backend

#### Technical Specifications
```javascript
// Estrutura do payload
{
  "empresa": {
    "nome": "string",
    "email": "string", 
    "setor": "string",
    "funcionarios": "string",
    "faturamento": "string (optional)"
  },
  "diagnostico": {
    "dor_principal": "string",
    "objetivo_ia": "string", 
    "urgencia": "integer (1-5)",
    "ferramentas_atuais": ["array"],
    "qualidade_dados": "integer (1-5)",
    "orcamento": "string"
  },
  "timestamp": "datetime"
}
```

### FR-02: Agente Classificador de IA

#### Description
Agente que analisa o perfil da empresa e gera score de prontidão para IA com classificação por tiers.

#### Acceptance Criteria
- [ ] Recebe JSON do formulário como input
- [ ] Retorna score 0-100 de prontidão para IA
- [ ] Classifica em tiers: Ouro (8-10), Prata (6-7.9), Bronze (<6)
- [ ] Gera justificativa textual do score
- [ ] Tempo de processamento <30 segundos
- [ ] Taxa de erro <5%

#### Technical Specifications
```python
# Input
formulario_data = {dict do formulário}

# Prompt Template
classification_prompt = """
Você é um especialista em diagnóstico de prontidão para IA empresarial.

Analise o perfil da empresa baseado nos dados:
{formulario_data}

Retorne um JSON com:
- score_prontidao: integer (0-100)
- tier: string ("ouro"/"prata"/"bronze") 
- pontuacao_icp: integer (0-10)
- pontuacao_intencao: integer (0-10)
- pontuacao_maturidade: integer (0-10)
- justificativa: string (max 200 chars)

Critérios de scoring:
- ICP: fit setor, porte, orçamento
- Intenção: urgência, objetivo claro
- Maturidade: ferramentas, dados, processos
"""

# Output
{
  "score_prontidao": 75,
  "tier": "prata",
  "pontuacao_icp": 8,
  "pontuacao_intencao": 7, 
  "pontuacao_maturidade": 6,
  "justificativa": "Empresa com bom fit e intenção clara, mas maturidade digital limitada"
}
```

### FR-03: Agente Gerador de Conteúdo

#### Description
Agente que cria conteúdo personalizado para o relatório baseado no perfil classificado.

#### Acceptance Criteria
- [ ] Recebe dados do formulário + classificação como input
- [ ] Gera top 3 oportunidades de IA específicas
- [ ] Cria case sintético de empresa similar
- [ ] Lista recomendações do que evitar
- [ ] Define próximos passos com timeline
- [ ] Conteúdo personalizado por setor/perfil
- [ ] Tempo de processamento <45 segundos

#### Technical Specifications
```python
# Input
{
  "formulario_data": {dict},
  "classificacao": {dict do agente classificador}
}

# Prompt Template  
content_prompt = """
Você é um consultor sênior de IA especializado em implementações empresariais.

Baseado no perfil da empresa:
{formulario_data}

E na classificação:
{classificacao}

Gere conteúdo para relatório executivo:

1. top_3_oportunidades: [
   {
     "titulo": "string",
     "descricao": "string (max 150 chars)", 
     "roi_estimado": "string",
     "timeline": "string",
     "investimento": "string"
   }
]

2. case_sintetico: {
   "empresa_exemplo": "string",
   "situacao_inicial": "string (max 200 chars)",
   "solucao_implementada": "string (max 200 chars)", 
   "resultados": "string (max 150 chars)"
}

3. recomendacoes_evitar: ["string", "string", "string"]

4. proximos_passos: [
   {
     "etapa": "string",
     "prazo": "string", 
     "descricao": "string (max 100 chars)"
   }
]
"""
```

### FR-04: Gerador de Relatório PDF

#### Description
Sistema que compila os dados e gera relatório visual em PDF usando template Jinja2.

#### Acceptance Criteria
- [ ] Recebe dados compilados (formulário + IA outputs)
- [ ] Gera PDF usando template HTML/CSS
- [ ] Layout profissional e visual
- [ ] Branding Academia Lendária
- [ ] Tamanho <2MB, formato A4
- [ ] Tempo de geração <20 segundos
- [ ] PDF acessível e searchable

#### Technical Specifications
```python
# Template Structure
template_data = {
  "empresa": {empresa_info},
  "score": {classification_data}, 
  "oportunidades": {opportunities_list},
  "case": {synthetic_case},
  "evitar": {avoid_recommendations},
  "passos": {next_steps},
  "metadata": {
    "data_geracao": "datetime",
    "versao": "string"
  }
}

# Template Jinja2
relatorio_template = """
<!DOCTYPE html>
<html>
<head>
  <style>
    /* CSS para PDF styling */
  </style>
</head>
<body>
  <div class="header">
    <img src="logo.png" alt="Academia Lendária">
    <h1>Diagnóstico IA - {{empresa.nome}}</h1>
  </div>
  
  <div class="score-dashboard">
    <!-- Score visual components -->
  </div>
  
  <!-- Mais seções do template -->
</body>
</html>
"""
```

### FR-05: Sistema de Persistência

#### Description
Banco de dados para armazenar formulários, classificações, conteúdo gerado e metadados.

#### Acceptance Criteria
- [ ] Armazena todos os dados do fluxo completo
- [ ] Backup automático dos dados
- [ ] Queries rápidas (<100ms para dashboards)
- [ ] Suporte a analytics básicos
- [ ] LGPD compliance (dados anonimizáveis)

#### Technical Specifications
```sql
-- Tabela Principal
CREATE TABLE diagnosticos (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Dados da Empresa
    empresa_nome VARCHAR(255) NOT NULL,
    empresa_email VARCHAR(255) NOT NULL,
    setor VARCHAR(100),
    funcionarios VARCHAR(50),
    faturamento VARCHAR(50),
    
    -- Diagnóstico Input
    dor_principal TEXT,
    objetivo_ia TEXT,
    urgencia INTEGER CHECK (urgencia BETWEEN 1 AND 5),
    ferramentas_atuais JSONB,
    qualidade_dados INTEGER CHECK (qualidade_dados BETWEEN 1 AND 5),
    orcamento VARCHAR(50),
    
    -- IA Outputs
    score_prontidao INTEGER CHECK (score_prontidao BETWEEN 0 AND 100),
    tier VARCHAR(20) CHECK (tier IN ('ouro', 'prata', 'bronze')),
    pontuacao_icp INTEGER CHECK (pontuacao_icp BETWEEN 0 AND 10),
    pontuacao_intencao INTEGER CHECK (pontuacao_intencao BETWEEN 0 AND 10),
    pontuacao_maturidade INTEGER CHECK (pontuacao_maturidade BETWEEN 0 AND 10),
    justificativa TEXT,
    
    -- Conteúdo Gerado
    oportunidades JSONB,
    case_sintetico JSONB,
    recomendacoes_evitar JSONB,
    proximos_passos JSONB,
    
    -- Metadados
    pdf_path VARCHAR(500),
    processing_time_seconds INTEGER,
    ip_address INET,
    user_agent TEXT
);

-- Índices para Performance
CREATE INDEX idx_diagnosticos_created_at ON diagnosticos(created_at);
CREATE INDEX idx_diagnosticos_tier ON diagnosticos(tier);
CREATE INDEX idx_diagnosticos_setor ON diagnosticos(setor);
```

---

## 🔒 Non-Functional Requirements

### Performance
- **Response Time**: API endpoints <2s, PDF generation <20s
- **Throughput**: Support 100 concurrent users
- **Availability**: 99.9% uptime durante demonstração

### Security
- **Data Protection**: Input sanitization, SQL injection prevention
- **Privacy**: LGPD compliance, dados anonimizáveis
- **API Security**: Rate limiting, basic authentication

### Scalability
- **Horizontal Scaling**: Stateless backend architecture
- **Database**: Connection pooling, query optimization
- **CDN**: Static assets delivery

### Usability
- **Accessibility**: WCAG 2.1 AA compliance básico
- **Mobile**: Responsive design, touch-friendly
- **Internationalization**: Preparado para PT-BR (MVP)

---

## 🧪 Testing Requirements

### Unit Tests
- [ ] Agentes de IA (mock OpenAI responses)
- [ ] PDF generation logic
- [ ] Data validation functions
- [ ] Database operations

### Integration Tests
- [ ] API endpoint complete flows
- [ ] Database CRUD operations
- [ ] External service integrations (OpenAI)

### User Acceptance Tests
- [ ] Complete user journey (happy path)
- [ ] Form validation edge cases
- [ ] PDF output quality verification
- [ ] Cross-browser compatibility (Chrome, Safari, Firefox)

### Performance Tests
- [ ] Load testing with 50 concurrent users
- [ ] Database query performance
- [ ] PDF generation under load

---

## 📋 API Specification

### POST /api/diagnostico
**Description**: Recebe formulário e processa diagnóstico completo

**Request**:
```json
{
  "empresa": {
    "nome": "TechCorp LTDA",
    "email": "ceo@techcorp.com",
    "setor": "tecnologia",
    "funcionarios": "100-200",
    "faturamento": "10-50M"
  },
  "diagnostico": {
    "dor_principal": "atendimento_manual",
    "objetivo_ia": "reduzir_custos",
    "urgencia": 4,
    "ferramentas_atuais": ["crm_basico", "email_marketing"],
    "qualidade_dados": 3,
    "orcamento": "50-100k"
  }
}
```

**Response**:
```json
{
  "id": "uuid",
  "status": "success",
  "processamento": {
    "tempo_segundos": 45,
    "timestamp": "2025-07-26T10:30:00Z"
  },
  "resultado": {
    "score_prontidao": 75,
    "tier": "prata",
    "pontuacoes": {
      "icp": 8,
      "intencao": 7,
      "maturidade": 6
    },
    "justificativa": "Empresa com bom fit...",
    "oportunidades": [...],
    "case_sintetico": {...},
    "recomendacoes_evitar": [...],
    "proximos_passos": [...]
  },
  "relatorio": {
    "pdf_url": "/api/relatorio/uuid.pdf",
    "download_expires": "2025-07-27T10:30:00Z"
  }
}
```

### GET /api/relatorio/{id}.pdf
**Description**: Download do relatório em PDF

**Response**: PDF file (application/pdf)

### GET /api/analytics/dashboard
**Description**: Métricas básicas para demonstração

**Response**:
```json
{
  "total_diagnosticos": 156,
  "distribuicao_tiers": {
    "ouro": 23,
    "prata": 67, 
    "bronze": 66
  },
  "setores_top": [
    {"nome": "tecnologia", "count": 45},
    {"nome": "varejo", "count": 32}
  ],
  "score_medio": 6.4,
  "tempo_medio_processamento": 38
}
```

---

## 🚀 Deployment Guide

### Environment Setup

#### Development
```bash
# Backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend  
python -m http.server 3000

# Database
sqlite3 database.db < schema.sql
```

#### Production
```bash
# Railway deployment
railway link [project]
railway up

# Environment Variables
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
ENVIRONMENT=production
```

### Configuration Management
```python
# config.py
import os

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    PDF_STORAGE_PATH = os.getenv("PDF_STORAGE_PATH", "./pdfs/")
    
    # Rate Limiting
    REQUESTS_PER_MINUTE = 60
    
    # AI Configuration
    OPENAI_MODEL = "gpt-4"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.3
```

---

## 📈 Success Criteria

### MVP Success Definition
✅ **Technical**: Sistema completo funcionando end-to-end  
✅ **User Experience**: Fluxo intuitivo, <5min completion  
✅ **Business Value**: Demonstração clara de qualificação de leads  
✅ **Quality**: Relatórios personalizados e profissionais  

### Demo Readiness Checklist
- [ ] Landing page responsiva deployed
- [ ] Formulário multi-step funcionando
- [ ] Backend API processingformulários
- [ ] Agentes IA gerando conteúdo consistente
- [ ] PDFs sendo gerados e servidos
- [ ] 5+ diagnósticos de exemplo completados
- [ ] Analytics básico funcionando
- [ ] Error handling graceful
- [ ] Loading states implementados
- [ ] Mobile experience testado

---

## 🔄 Future Roadmap (Pós-Hackathon)

### Phase 2: Enhancement (1-2 semanas)
- A/B testing do formulário
- Melhorias nos prompts de IA
- Dashboard analytics avançado
- Integração CRM (HubSpot/Pipedrive)

### Phase 3: Scale (1 mês)
- Auto-ML para otimização dos scores
- Segmentação avançada por vertical
- White-label version
- API pública para parceiros

### Phase 4: Intelligence (3 meses)
- Learning loop baseado em conversões reais
- Benchmarking dinâmico por setor
- Simulador de ROI interativo
- Expansão internacional

---

**Document Status**: Ready for Development  
**Next Review**: Post-Hackathon  
**Questions/Clarifications**: [Team Slack Channel]