import pandas as pd
from typing import List, Dict, Any
import time

# Import your new fetcher
# (Make sure knowledge_fetcher.py is in the same folder!)
from knowledge_fetcher import fetch_clinvar_data

class GenomicAnalysisEngine:
    def __init__(self, genome_file_path: str):
        self.file_path = genome_file_path
        self.user_df = None
        self.report = {
            "health_flags": [],
            "future_perspectives": []
        }

    def load_genome(self):
        """Parses a 23andMe style raw text file."""
        print(f"Loading genome from {self.file_path}...")
        try:
            self.user_df = pd.read_csv(
                self.file_path, 
                sep='\t', 
                comment='#', 
                header=None, 
                names=['rsid', 'chrom', 'pos', 'genotype'],
                dtype=str
            )
            # Clean up whitespace in RSIDs just in case
            self.user_df['rsid'] = self.user_df['rsid'].str.strip()
            print(f"Successfully loaded {len(self.user_df)} genetic markers.")
        except Exception as e:
            print(f"Error loading genome: {e}")
            self.user_df = pd.DataFrame()

    def check_clinvar_live(self, target_rsids: List[str]):
        """
        Queries NCBI ClinVar LIVE for specific markers found in the user's file.
        """
        print(f"🔍 Checking {len(target_rsids)} markers against ClinVar database...")
        
        for rsid in target_rsids:
            # 1. Check if user actually has this marker in their file
            user_record = self.user_df[self.user_df['rsid'] == rsid]
            
            if not user_record.empty:
                user_genotype = user_record.iloc[0]['genotype']
                
                # 2. Fetch Verified Data from NCBI via your new fetcher script
                verified_data = fetch_clinvar_data(rsid)
                
                if verified_data:
                    # 3. Add to Report
                    self.report['health_flags'].append({
                        "source": "NCBI ClinVar",
                        "variant": f"{verified_data['title']} (Genotype: {user_genotype})",
                        "significance": verified_data['significance'],
                        "link": f"https://www.ncbi.nlm.nih.gov/clinvar/?term={rsid}"
                    })
                    print(f"   ✅ Found verified data for {rsid}")
                
                # Be nice to the government API (prevent rate limiting)
                time.sleep(0.5) 

    def run_full_analysis(self):
        self.load_genome()
        
        if self.user_df.empty:
            return {"error": "No data loaded"}

        # Define the specific markers we want to verify from the sample file
        # In a real app, you'd iterate through thousands, but for this demo we check 3 specific ones
        # These match the RSIDs in your 'sample_genome_for_testing.txt'
        markers_to_check = ["rs4977574", "rs2282679", "rs429358"] 
        
        self.check_clinvar_live(markers_to_check)
        
        # Note: Future Perspectives (PGS) logic can be re-added here similarly
        
        return self.report

if __name__ == "__main__":
    # Test run (assumes you have sample_genome_for_testing.txt in the folder)
    engine = GenomicAnalysisEngine("sample_genome_for_testing.txt")
    import json
    print(json.dumps(engine.run_full_analysis(), indent=2))