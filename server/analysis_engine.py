import pandas as pd
import pandas as pd
from typing import List, Dict, Any
import time
import concurrent.futures # Added for parallel processing
from risk_db import RISK_MARKERS_DB # Added for local DB lookup

# Import your fetcher
from knowledge_fetcher import fetch_clinvar_data

class GenomicAnalysisEngine:
    def __init__(self, genome_file_path: str):
        self.file_path = genome_file_path
        self.user_df = None
        self.report = {
            "health_flags": [],
            "future_perspectives": [],
            "genome_sample": [] 
        }

    def load_genome(self):
        """Parses a 23andMe style raw text file with ROBUST separator detection."""
        print(f"Loading genome from {self.file_path}...")
        try:
            # CRITICAL FIX: sep=None allows Pandas to sniff Comma, Tab, or Space automatically
            # Chunking strategy: For 50k lines, read_csv is fast enough. 
            # If we had 1GB files, we would use chunksize=10000.
            self.user_df = pd.read_csv(
                self.file_path, 
                sep=None,  
                engine='python',
                comment='#', 
                header=None, 
                names=['rsid', 'chrom', 'pos', 'genotype'],
                dtype=str,
                on_bad_lines='skip'
            )
            
            # Clean up data
            self.user_df['rsid'] = self.user_df['rsid'].str.strip()
            self.user_df['genotype'] = self.user_df['genotype'].str.strip()
            
            print(f"Successfully loaded {len(self.user_df)} genetic markers.")
            
        except Exception as e:
            print(f"Error loading genome: {e}")
            self.user_df = pd.DataFrame()

    def check_clinvar_live(self, target_rsids: List[str]):
        """
        Parallelized ClinVar checking.
        """
        print(f"🔍 Checking {len(target_rsids)} markers against ClinVar database...")
        
        if not target_rsids:
            return

        # Helper function for parallel execution
        def fetch_and_process(rsid):
            # Check if user actually has this marker
            user_record = self.user_df[self.user_df['rsid'] == rsid]
            if not user_record.empty:
                user_genotype = user_record.iloc[0]['genotype']
                # Fetch Verified Data
                verified_data = fetch_clinvar_data(rsid)
                if verified_data:
                    return {
                        "source": "NCBI ClinVar (Live)",
                        "variant": f"{verified_data['title']} (Genotype: {user_genotype})",
                        "significance": verified_data['significance'],
                        "link": f"https://www.ncbi.nlm.nih.gov/clinvar/?term={rsid}"
                    }
            return None

        # Use ThreadPoolExecutor for parallel API calls (IO-bound)
        # Limit to 5 workers to avoid hitting API rate limits too hard
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_rsid = {executor.submit(fetch_and_process, rsid): rsid for rsid in target_rsids}
            for future in concurrent.futures.as_completed(future_to_rsid):
                try:
                    result = future.result()
                    if result:
                        self.report['health_flags'].append(result)
                        print(f"   ✅ Found verified data for {future_to_rsid[future]}")
                except Exception as exc:
                    print(f"   ❌ Exception checking marker: {exc}")

    def run_full_analysis(self):
        self.load_genome()
        
        if self.user_df is None or self.user_df.empty:
            return {"error": "No valid genomic data found in file. Please ensure it has 4 columns."}

        # 1. Populate Genome Sample (Top 100 rows)
        sample = []
        subset = self.user_df.head(100) 
        for _, row in subset.iterrows():
            sample.append({
                "rsid": str(row['rsid']),
                "chromosome": str(row['chrom']),
                "position": str(row['pos']),
                "genotype": str(row['genotype'])
            })
        self.report['genome_sample'] = sample

        # 2. DEEP ANALYSIS STRATEGY: "Triage & Verify"
        # Instead of checking random markers, we scan the ENTIRE user genome 
        # against our local high-impact database first.
        
        # Find intersection between User Genome and Risk DB
        # This is extremely fast (vectorized) even for 50k+ rows
        user_rsids = set(self.user_df['rsid'].values)
        db_rsids = set(RISK_MARKERS_DB.keys())
        
        # Matches found in our local DB
        matches = list(user_rsids.intersection(db_rsids))
        
        print(f"Found {len(matches)} potential risk markers in local DB.")
        
        # 3. Add Local DB Hits immediately (Fast)
        for rsid in matches:
            info = RISK_MARKERS_DB[rsid]
            user_genotype = self.user_df[self.user_df['rsid'] == rsid].iloc[0]['genotype']
            self.report['health_flags'].append({
                "source": "MyBlueprint KnowledgeBase",
                "variant": f"{info['variant']} (Genotype: {user_genotype})",
                "significance": info['significance'],
                "link": f"https://www.ncbi.nlm.nih.gov/clinvar/?term={rsid}"
            })

        # 4. Live Verification (Optional / Hybrid)
        # We can also check a few specific "Always Check" markers if they weren't in the DB
        # or if we want to double-check the DB hits against live ClinVar.
        # For now, let's just check the matches against ClinVar to get "Live" status if we want,
        # or check a separate list of "New/Trending" variants.
        
        # Let's verify the matches LIVE to ensure data is up to date (demonstrating "Live API" capability)
        # Only verify if we have matches, and limit to top 5 to save time
        if matches:
             self.check_clinvar_live(matches[:5])
        
        return self.report

if __name__ == "__main__":
    # Test run 
    engine = GenomicAnalysisEngine("sample_genome_for_testing.txt")
    import json
    print(json.dumps(engine.run_full_analysis(), indent=2))