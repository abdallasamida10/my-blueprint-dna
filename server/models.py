from pydantic import BaseModel, Field
from typing import List, Literal

# --- Sub-models defining the core data elements ---

class RiskFactor(BaseModel):
    """Defines the structure for a single health risk."""
    label: str = Field(..., description="E.g., 'Alzheimer\'s Risk'")
    risk_level: Literal["Low", "Mod", "High"] = Field(..., description="Severity level for the trait.")
    gene: str = Field(..., description="Associated gene or marker (e.g., 'APOE4').")

class TraitStat(BaseModel):
    """Defines a single quick stat card for the dashboard."""
    category: str = Field(..., description="E.g., 'Metabolism', 'Recovery'")
    value: str = Field(..., description="E.g., 'Fast', 'Elite'")
    genotype: str = Field(..., description="E.g., 'AA', 'CC'")

# --- Main Report Model (The entire API response structure) ---

class GeneticReport(BaseModel):
    """The complete response structure for the MyBlueprint dashboard."""
    vitality_score: int = Field(..., description="The calculated overall health score (0-100).")
    score_label: Literal["Optimal", "Superior", "Average", "Attention"] = Field(..., description="Text description for the score.")
    
    # Widgets that correspond to the Bento Grid
    risk_list: List[RiskFactor] = Field(..., description="List of top risk factors for the attention widget.")
    trait_stats: List[TraitStat] = Field(..., description="List of quick-stat widgets.")

    # A field to track the file that generated the report
    source_filename: str = Field(..., description="Name of the file that was analyzed.")