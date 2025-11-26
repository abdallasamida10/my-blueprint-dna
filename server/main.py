from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from typing import List

# Import your new engine
from analysis_engine import GenomicAnalysisEngine

# Import models (ensure models.py matches the engine output structure)
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Update Models to match Engine Output
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

class FullReport(BaseModel):
    health_flags: List[HealthFlag]
    future_perspectives: List[FuturePerspective]

@app.post("/api/analyze", response_model=FullReport)
async def analyze_genome(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    try:
        # 1. Save File
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Run Analysis Engine
        engine = GenomicAnalysisEngine(file_location)
        report = engine.run_full_analysis()
        
        if "error" in report:
             raise HTTPException(status_code=400, detail=report["error"])
             
        return report

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)