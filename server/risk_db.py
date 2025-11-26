
# A simulated "Database" of known high-impact pathogenic variants.
# In a real SaaS, this would be a Redis/Postgres DB or a large VCF file.
# We use this to "scan" the user's 50,000 markers instantly without API calls.

RISK_MARKERS_DB = {
    "rs4977574": {
        "gene": "CDKN2A/B",
        "variant": "Heart Disease Risk",
        "significance": "Pathogenic (High Risk)",
        "description": "Associated with increased risk of coronary artery disease."
    },
    "rs2282679": {
        "gene": "GC",
        "variant": "Vitamin D Deficiency",
        "significance": "Risk Factor",
        "description": "Lower conversion of Vitamin D. Supplementation recommended."
    },
    "rs429358": {
        "gene": "APOE",
        "variant": "Alzheimer's Risk (e4)",
        "significance": "High Risk",
        "description": "APOE e4 allele associated with increased risk of Alzheimer's."
    },
    "rs7412": {
        "gene": "APOE",
        "variant": "Alzheimer's Risk (e2)",
        "significance": "Protective/Risk",
        "description": "APOE e2 is generally protective, but e4 is risk."
    },
    "rs762551": {
        "gene": "CYP1A2",
        "variant": "Caffeine Sensitivity",
        "significance": "Metabolic",
        "description": "Slow metabolizer of caffeine."
    },
    "rs1815739": {
        "gene": "ACTN3",
        "variant": "Muscle Performance",
        "significance": "Trait",
        "description": "R577X variant. Associated with sprinter vs endurance athlete muscle type."
    },
    "rs6025": {
        "gene": "F5",
        "variant": "Factor V Leiden",
        "significance": "Pathogenic",
        "description": "Increased risk of blood clots (thrombophilia)."
    },
    "rs1801133": {
        "gene": "MTHFR",
        "variant": "MTHFR C677T",
        "significance": "Risk Factor",
        "description": "Reduced folate metabolism. Homocysteine levels may be high."
    },
    "rs1801131": {
        "gene": "MTHFR",
        "variant": "MTHFR A1298C",
        "significance": "Risk Factor",
        "description": "Reduced folate metabolism."
    },
    "rs1800497": {
        "gene": "DRD2",
        "variant": "Dopamine Receptor",
        "significance": "Trait",
        "description": "Associated with reward deficiency syndrome."
    },
    "rs4680": {
        "gene": "COMT",
        "variant": "Worrier vs Warrior",
        "significance": "Trait",
        "description": "Val158Met. Affects dopamine breakdown in prefrontal cortex."
    },
    "rs1799971": {
        "gene": "OPRM1",
        "variant": "Opioid Sensitivity",
        "significance": "Pharmacogenomic",
        "description": "Altered response to opioids and alcohol."
    },
    "rs3934834": {
        "gene": "BRCA1",
        "variant": "Breast Cancer Risk",
        "significance": "Pathogenic",
        "description": "Known pathogenic variant for breast/ovarian cancer."
    },
    "rs80357906": {
        "gene": "BRCA1",
        "variant": "Breast Cancer Risk",
        "significance": "Pathogenic",
        "description": "Pathogenic variant."
    }
}
