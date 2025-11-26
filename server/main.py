from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from typing import List
from analysis_engine import GenomicAnalysisEngine
from models import FullReport, HealthFlag, FuturePerspective, GenomeRow

app = FastAPI()

# --- CRITICAL: CORS Configuration for React Frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Netlify/Localhost)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze", response_model=FullReport)
async def analyze_genome(file: UploadFile = File(...)):
    """
    Receives a raw DNA file, processes it via the GenomicAnalysisEngine,
    and returns a verified report + raw data sample.
    """
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    try:
        # 1. Save the uploaded file securely
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Initialize the Analysis Engine with the file
        engine = GenomicAnalysisEngine(file_location)
        
        # 3. Run the Full Analysis (Parsing + NCBI ClinVar Check)
        # This function now calls knowledge_fetcher internally
        report = engine.run_full_analysis()
        
        # 4. Check for errors from the engine
        if "error" in report:
             raise HTTPException(status_code=400, detail=report["error"])
             
        # 5. Return the structured report
        return report

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 6. Cleanup: Delete the file immediately after processing for privacy
        if os.path.exists(file_location):
            try:
                os.remove(file_location)
            except:
                pass