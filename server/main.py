from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import shutil
import time
from typing import Dict, Any

# CORRECTED IMPORT: Removed the dot (.) to fix relative import error
from models import GeneticReport, RiskFactor, TraitStat 

app = FastAPI(
    title="MyBlueprint Genetic Analysis API",
    description="Backend service for processing raw genomic data.",
    version="1.0.0"
)

# --- CRITICAL: CORS Configuration for React Frontend ---
# Allows React (running on a different port/domain) to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development ease
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mock Knowledge Base (Replace with PostgreSQL/Redis in production) ---
# Maps a risk name to a set of genotypes and results
KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "Caffeine Metabolism": {"rs762551": {"AA": "Fast", "AC": "Normal", "CC": "Slow"}},
    "Muscle Type": {"rs1815739": {"CC": "Power", "CT": "Normal", "TT": "Endurance"}},
    "Heart Risk (9p21)": {"rs4977574": {"GG": "Low Risk", "GA": "Mod Risk", "AA": "High Risk"}},
    "Vitamin D Deficiency": {"rs2282679": {"GG": "High Risk", "GT": "Mod Risk", "TT": "Low Risk"}},
    "Alzheimer Risk (APOE)": {"rs429358": {"TT": "Low Risk", "CT": "Mod Risk", "CC": "High Risk"}},
}

@app.post("/api/analyze", response_model=GeneticReport)
async def analyze_genome(file: UploadFile = File(...)):
    """Accepts a raw DNA file, processes it, and returns the structured GeneticReport."""
    
    # 1. Setup paths and check file type
    # Relaxed check to allow common text types during testing
    if not file.filename.lower().endswith(('.txt', '.csv', '.vcf', '.tsv')):
         raise HTTPException(status_code=400, detail="Invalid file format. Must be VCF, CSV, or TXT.")

    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    # 2. Save the uploaded file temporarily
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File saving failed: {e}")
    
    # 3. Simulate heavy, time-consuming data parsing (2 seconds delay)
    time.sleep(2) 
    
    # --- CORE PANDAS LOGIC (Simulation for now) ---
    try:
        # Load the file into a Pandas DataFrame. Using a simple TSV read for compatibility.
        # We add error_bad_lines=False to skip malformed rows in random text files
        try:
            df = pd.read_csv(file_location, sep='\t', comment='#', dtype=str, on_bad_lines='skip')
        except:
            # Fallback for comma separated
            df = pd.read_csv(file_location, sep=',', comment='#', dtype=str, on_bad_lines='skip')
            
        df.columns = [c.lower().strip() for c in df.columns]

        # --- Data Generation Placeholder ---
        # In a real app, this logic would calculate a score based on hundreds of rows in 'df'.
        
        # We simulate finding specific genotypes for the report:
        simulated_results = {
            "rs762551": "AA",  # Fast Metabolizer
            "rs1815739": "CC", # Power Muscle
            "rs4977574": "GA", # Moderate Heart Risk
            "rs2282679": "GT", # Moderate Vitamin D Def. Risk
            "rs429358": "TT",  # Low Alzheimer Risk
        }
        
        # --- Build the response structure based on the simulation ---
        
        # A. Calculate Vitality Score (Simulated)
        vitality_score = 92
        score_label = "Superior"

        # B. Build Trait Stats (Quick Widgets)
        trait_stats = [
            TraitStat(category="Metabolism", value=KNOWLEDGE_BASE["Caffeine Metabolism"]["rs762551"][simulated_results["rs762551"]], genotype=f"rs762551 ({simulated_results['rs762551']})"),
            TraitStat(category="Muscle Type", value=KNOWLEDGE_BASE["Muscle Type"]["rs1815739"][simulated_results["rs1815739"]], genotype=f"rs1815739 ({simulated_results['rs1815739']})"),
        ]

        # C. Build Risk List (Attention Widget)
        risk_list = [
            RiskFactor(label="Heart Health", risk_level=KNOWLEDGE_BASE["Heart Risk (9p21)"]["rs4977574"][simulated_results["rs4977574"]], gene="9p21"),
            RiskFactor(label="Vitamin D Def.", risk_level=KNOWLEDGE_BASE["Vitamin D Deficiency"]["rs2282679"][simulated_results["rs2282679"]], gene="VDR"),
            RiskFactor(label="Alzheimer's", risk_level=KNOWLEDGE_BASE["Alzheimer Risk (APOE)"]["rs429358"][simulated_results["rs429358"]], gene="APOE"),
        ]
        
        # 4. Return the response model (guaranteed to match the Pydantic schema)
        return GeneticReport(
            vitality_score=vitality_score,
            score_label=score_label,
            risk_list=risk_list,
            trait_stats=trait_stats,
            source_filename=file.filename
        )

    except Exception as e:
        print(f"Analysis Error: {e}")
        # Still return a success mock for testing purposes if the file is junk
        # This prevents the frontend from breaking during your demo
        return GeneticReport(
            vitality_score=88,
            score_label="Optimal",
            risk_list=[RiskFactor(label="Demo Risk", risk_level="Low", gene="TEST")],
            trait_stats=[TraitStat(category="Demo Mode", value="Active", genotype="N/A")],
            source_filename="demo_file.txt"
        )
    
    finally:
        # 5. Cleanup: Delete the file immediately after processing for privacy
        if os.path.exists(file_location):
            try:
                os.remove(file_location)
            except:
                pass