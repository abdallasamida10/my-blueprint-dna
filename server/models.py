from pydantic import BaseModel
from typing import List, Literal, Optional

class RiskFactor(BaseModel):
    label: str
    risk_level: Literal["Low", "Mod", "High"]
    gene: str

class TraitStat(BaseModel):
    category: str
    value: str
    genotype: str

class HealthFlag(BaseModel):
    source: str
    variant: str
    significance: str
    link: str

class FuturePerspective(BaseModel):
    trait: str
    score_id: str
    raw_score: float
    interpretation: str
    citation: str

# NEW: Model for raw file rows
class GenomeRow(BaseModel):
    rsid: str
    chromosome: str
    position: str
    genotype: str

class GeneticReport(BaseModel):
    vitality_score: int
    score_label: Literal["Optimal", "Superior", "Average", "Attention"]
    risk_list: List[RiskFactor]
    trait_stats: List[TraitStat]
    source_filename: str

# NEW: Full Report including raw data
class FullReport(BaseModel):
    health_flags: List[HealthFlag]
    future_perspectives: List[FuturePerspective]
    genome_sample: List[GenomeRow] # <--- ADD THIS