from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

# --- Input Schema from Frontend ---

class LeadProfileInput(BaseModel):
    """
    Represents the raw data structure sent from the frontend form.
    """
    name: str
    p0_email: EmailStr = Field(..., alias="email")
    p_phone: Optional[str] = Field(None, alias="phone")
    p1_sector: str = Field(..., alias="sector")
    p2_company_size: str = Field(..., alias="company_size")
    p3_role: str = Field(..., alias="role")
    p4_main_pain: str = Field(..., alias="main_pain")
    p5_critical_area: Optional[str] = Field(None, alias="critical_area")
    p6_pain_quant: Optional[str] = Field(None, alias="pain_quantification")
    p7_digital_maturity: str = Field(..., alias="digital_maturity")
    p8_investment: str = Field(..., alias="investment_capacity")
    p9_urgency: str = Field(..., alias="urgency")

    class Config:
        orm_mode = True


# --- Schemas for AI Agent Outputs ---

class Opportunity(BaseModel):
    titulo: str = Field(..., description="Title of the opportunity.")
    description: str = Field(..., description="Detailed description of the opportunity personalized for the user profile.")
    roi: str = Field(..., description="Estimated Return on Investment.")
    priority: str = Field(..., description="Priority of the opportunity (alta, media, baixa).")
    case: str = Field(..., description="A success case for a similar company.")

class OpportunitiesOutput(BaseModel):
    opportunities: List[Opportunity]

class Scores(BaseModel):
    """
    Represents the calculated scores for different dimensions.
    """
    poder_de_decisao: float
    cultura_e_talentos: float
    processos_e_automacao: float
    inovacao_de_produtos: float
    inteligencia_de_mercado: float

class FinalReportData(BaseModel):
    """
    Consolidated data structure for generating the final HTML report.
    This will be stored in the `ai_full_report_json` column.
    """
    empresa: Dict[str, Any]
    scores_radar: Scores
    score_final: float
    relatorio_oportunidades: List[Opportunity]
    relatorio_riscos: List[Dict[str, str]]


# --- Database Model Schema ---

class LeadProfile(BaseModel):
    """
    Represents the data structure of the 'lead_profiles' table in the database.
    """
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    lead_email: str
    lead_phone: Optional[str] = None
    status: str = "PENDING_ANALYSIS"
    
    # Raw answers
    raw_p1_sector: str
    raw_p2_company_size: str
    raw_p3_role: str
    raw_p4_main_pain: str
    raw_p5_critical_area: Optional[str] = None
    raw_p6_pain_quant: Optional[str] = None
    raw_p7_digital_maturity: str
    raw_p8_investment: str
    raw_p9_urgency: str
    name: Optional[str] = None

    # AI-generated fields
    ai_score_final: Optional[float] = None
    ai_tier: Optional[str] = None
    ai_scores_json: Optional[Dict[str, Any]] = None
    ai_persona_tag: Optional[str] = None
    ai_pain_category: Optional[str] = None
    ai_pain_is_quantified: Optional[bool] = None
    ai_pain_sentiment: Optional[str] = None
    ai_sales_objections: Optional[List[str]] = None
    ai_sales_pitch_angle: Optional[str] = None
    ai_full_report_json: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
