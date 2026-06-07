import re
from typing import List, Dict, Tuple, Optional

STATE_MAP = {
    "west bengal": "West Bengal", "wb": "West Bengal",
    "delhi": "Delhi", "dl": "Delhi", "nct": "Delhi",
    "maharashtra": "Maharashtra", "mh": "Maharashtra",
    "karnataka": "Karnataka", "ka": "Karnataka",
    "tamil nadu": "Tamil Nadu", "tn": "Tamil Nadu",
    "kerala": "Kerala", "kl": "Kerala",
    "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh",
    "bihar": "Bihar", "br": "Bihar",
    "gujarat": "Gujarat", "gj": "Gujarat",
    "rajasthan": "Rajasthan", "rj": "Rajasthan",
    "punjab": "Punjab", "pb": "Punjab",
    "haryana": "Haryana", "hr": "Haryana",
    "telangana": "Telangana", "tg": "Telangana", "ts": "Telangana",
    "andhra pradesh": "Andhra Pradesh", "ap": "Andhra Pradesh",
    "madhya pradesh": "Madhya Pradesh", "mp": "Madhya Pradesh",
}

VIOLATION_KEYWORDS = {
    "no_helmet": ["helmet", "helmets", "headgear"],
    "no_seatbelt": ["seatbelt", "seatbelts", "seat belt", "seat belts"],
    "child_safety": ["child safety", "harness", " restraint", "kids safety", "child belt"],
    "overspeeding": ["overspeed", "overspeeding", "speeding", "speed limit", "fast driving", "velocity"],
    "drunk_driving": ["drunk", "drink", "alcohol", "drinking", "liquor", "intoxicated", "bac", "dui"],
    "no_insurance": ["insurance", "third party", "insure"],
    "no_dl": ["license", "dl", "licence", "driving license", "driving licence", "no license", "no licence"],
    "use_of_phone": ["phone", "mobile", "calling", "cellphone", "talking", "handheld"],
    "triple_riding": ["triple", "tripling", "triple riding", "three riders", "3 riders", "3 riding"],
    "emergency_obstruction": ["ambulance", "fire brigade", "emergency vehicle", "obstructing"],
    "juvenile_offense": ["minor driving", "juvenile", "underage", "teenager driving", "guardian penalty"],
    "passenger_overload": ["passenger overload", "extra passenger", "passenger capacity", "overload passenger"],
    "goods_overload": ["goods overload", "cargo overload", "tonne", "weight limit", "payload", "overloading cargo"],
    "no_rc": ["registration", "rc", "registration certificate"],
    "no_puc": ["pollution", "puc", "pucc", "smoke test", "emission"],
    "racing": ["racing", "race", "speed trial"],
}

def detect_states(query: str) -> List[str]:
    detected = []
    cleaned_query = re.sub(r"[^\w\s]", " ", query.lower())
    words = cleaned_query.split()
    
    query_lower = query.lower()
    for state_key, state_name in STATE_MAP.items():
        if " " in state_key:
            if state_key in query_lower:
                if state_name not in detected:
                    detected.append(state_name)
                    
    for word in words:
        if word in STATE_MAP:
            state_name = STATE_MAP[word]
            if state_name not in detected:
                detected.append(state_name)
                
    return detected

def detect_violations(query: str) -> List[str]:
    detected = []
    query_lower = query.lower()
    
    for category, keywords in VIOLATION_KEYWORDS.items():
        for keyword in keywords:
            if len(keyword) <= 3:
                pattern = rf"\b{re.escape(keyword)}\b"
            else:
                pattern = re.escape(keyword)
                
            if re.search(pattern, query_lower):
                if category not in detected:
                    detected.append(category)
                break
                
    return detected

def parse_query_intent(query: str, location_state: Optional[str] = None) -> Dict:
    states = detect_states(query)
    violations = detect_violations(query)
    
    if not states and location_state:
        normalized = STATE_MAP.get(location_state.lower(), location_state)
        states = [normalized]
        
    query_lower = query.lower()
    
    # Check if this is a complex evaluation block, numbered list, or test prompt
    is_list = bool(re.search(r"\b\d+\s*[\.\)]\s+", query)) or bool(re.search(r"^\s*[\-\*\+]\s+", query, re.MULTILINE))
    has_multiple_questions = query.count("?") > 1
    is_complex = is_list or has_multiple_questions or len(query) > 200
    
    # Identify conditional, conversational, or situational questions
    is_conditional = any(w in query_lower for w in [
        "is it legal", "can i", "do i", "should i", "is it okay", "is it allowed", 
        "sunday", "sundays", "night", "weekend", "weekends", "holiday", "holidays",
        "happen if", "happens if", "if i get caught", "what if"
    ])
    
    # Determine intent type
    is_compare = any(w in query_lower for w in ["vs", "versus", "compare", "comparison", "difference", "delhi or", "wb or", "west bengal or"])
    is_educational = any(w in query_lower for w in ["why", "reason", "motivation", "safety benefit", "explain why", "need for", "explain"])
    is_procedural = any(w in query_lower for w in ["how to pay", "where to pay", "pay online", "echallan", "parivahan", "website"])
    
    # A query is a fine inquiry if it explicitly requests numbers/limits and is NOT purely conversational/educational
    is_fine_inq = any(w in query_lower for w in ["fine", "penalty", "charge", "cost", "how much", "amount", "rupee", "rs", "₹"])
    
    # Direct DB search matches simple violations that are not conditional, educational, procedural, or complex
    is_direct = (len(violations) > 0) and not is_educational and not is_procedural and not is_conditional and not is_complex
    
    return {
        "states": states,
        "violations": violations,
        "is_comparison": is_compare and len(states) >= 1,
        "is_multi_violation": len(violations) > 1,
        "is_educational": is_educational,
        "is_procedural": is_procedural,
        "is_fine_inquiry": is_fine_inq or is_direct,
        "is_direct_eligible": is_direct
    }
