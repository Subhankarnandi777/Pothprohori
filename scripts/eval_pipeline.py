import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
from rag.retrieve import Retriever

def run_local_eval():
    print("Initializing FAISS Retriever for local Evaluation...")
    retriever = Retriever()
    
    test_cases_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/eval/test_cases.json"))
    with open(test_cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    print(f"Loaded {len(cases)} test cases.\n")
    
    total_hit = 0
    
    for idx, case in enumerate(cases):
        print(f"[{idx+1}/{len(cases)}] Query: {case['query'][:50]}...")
        
        # 1. Embed query and search FAISS locally (No LLM calls!)
        query_vector = retriever.embedder.embed(case["query"])
        docs = retriever.search(query_vector, state=case["state"], k=3)
        
        # 2. Check if Expected Section is in retrieved docs text
        hit = False
        retrieved_sections = []
        for d in docs:
            txt = str(d.get("text", ""))
            if case["expected_section"] in txt:
                hit = True
            # Also extract section roughly for debugging display
            import re
            sec_match = re.search(r"Section:\s*([A-Za-z0-9]+)", txt)
            if sec_match:
                retrieved_sections.append(sec_match.group(1))
                
        if hit:
            total_hit += 1
            print(f"   [PASS] Found section {case['expected_section']}")
        else:
            print(f"   [FAIL] Expected {case['expected_section']}, but retrieved {retrieved_sections}")
            
    hit_rate = (total_hit / len(cases)) * 100
    
    print("\n" + "="*40)
    print("       FAISS RETRIEVAL ACCURACY")
    print("="*40)
    print(f"Total Test Cases   : {len(cases)}")
    print(f"Model Hit Rate     : {hit_rate:.1f}%")
    print(f"Status             : {'EXCELLENT' if hit_rate >= 80 else 'NEEDS TUNING'}")

if __name__ == "__main__":
    run_local_eval()
