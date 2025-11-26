import pandas as pd
from typing import List, Dict, Any
import time

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
        print(f"🔍 Checking markers against ClinVar database...")
        
        # If we have data, let's verify it
        if self.user_df is not None and not self.user_df.empty:
            for rsid in target_rsids:
                # Check if user actually has this marker
                user_record = self.user_df[self.user_df['rsid'] == rsid]
                
                if not user_record.empty:
                    user_genotype = user_record.iloc[0]['genotype']
                    
                    # Fetch Verified Data
                    verified_data = fetch_clinvar_data(rsid)
                    
                    if verified_data:
                        self.report['health_flags'].append({
                            "source": "NCBI ClinVar",
                            "variant": f"{verified_data['title']} (Genotype: {user_genotype})",
                            "significance": verified_data['significance'],
                            "link": f"https://www.ncbi.nlm.nih.gov/clinvar/?term={rsid}"
                        })
                        print(f"   ✅ Found verified data for {rsid}")
                    
                    time.sleep(0.5) 

    def run_full_analysis(self):
        self.load_genome()
        
        if self.user_df is None or self.user_df.empty:
            return {"error": "No valid genomic data found in file. Please ensure it has 4 columns."}

        # 1. Populate Genome Sample (Top 100 rows)
        # This ensures the user ALWAYS sees data in the browser
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

        # 2. Check specific markers for risks (The ones in your test file)
        markers_to_check = ["rs4977574", "rs2282679", "rs429358", "rs762551", "rs1815739"] 
        
        self.check_clinvar_live(markers_to_check)
        
        return self.report

if __name__ == "__main__":
    # Test run 
    engine = GenomicAnalysisEngine("sample_genome_for_testing.txt")
    import json
    print(json.dumps(engine.run_full_analysis(), indent=2))