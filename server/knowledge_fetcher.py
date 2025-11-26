import requests
import time

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def fetch_clinvar_data(rsid):
    """
    Queries NCBI ClinVar with robust error handling and prefix management.
    """
    # 1. Try searching with the "rs" prefix
    print(f"🔬 Querying NCBI ClinVar for {rsid}...")
    search_term = rsid
    
    # First Attempt
    result = _perform_search(search_term)
    
    # Second Attempt: Try stripping "rs" if no result (e.g., '762551')
    if not result and rsid.startswith("rs"):
        print(f"   ⚠️ No result for {rsid}, trying without 'rs' prefix...")
        search_term = rsid[2:]
        result = _perform_search(search_term)

    return result

def _perform_search(term):
    search_url = f"{BASE_URL}/esearch.fcgi?db=clinvar&term={term}&retmode=json"
    try:
        response = requests.get(search_url)
        data = response.json()
        
        id_list = data.get('esearchresult', {}).get('idlist', [])
        if not id_list:
            return None
        
        clinvar_id = id_list[0]
        
        # Fetch Summary
        summary_url = f"{BASE_URL}/esummary.fcgi?db=clinvar&id={clinvar_id}&retmode=json"
        summary_resp = requests.get(summary_url)
        summary_data = summary_resp.json()
        
        # Check if result exists in the dictionary (sometimes keys are strings)
        if str(clinvar_id) not in summary_data['result']:
             return None

        result = summary_data['result'][str(clinvar_id)]
        
        return {
            "rsid": term if term.startswith("rs") else f"rs{term}",
            "title": result.get('title', 'Unknown Title'),
            "significance": result.get('clinical_significance', {}).get('description', 'Unknown'),
            "gene": result.get('gene_sort', 'Unknown'),
            "last_updated": result.get('last_updated', 'Unknown')
        }
        
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        return None

if __name__ == "__main__":
    # Test with a known pathogenic marker (BRCA1) just to prove the connection works
    # rs80357906 is a known pathogenic BRCA1 variant
    test_rsid = "rs80357906" 
    print(f"--- TEST RUN: Checking {test_rsid} ---")
    data = fetch_clinvar_data(test_rsid)
    if data:
        print(f"✅ SUCCESS: {data['title']} ({data['significance']})")
    else:
        print("❌ FAILURE: No data found even for known marker.")