"""
LLM function-calling tool: compute challan fine for a violation.
"""
import os
import sys

def calculate_challan(violation: str, state: str, vehicle_type: str, repeat: bool, db = None) -> dict:
    close_db = False
    if db is None:
        try:
            # Dynamically import SessionLocal to query database
            from app.core.database import SessionLocal
            db = SessionLocal()
            close_db = True
        except Exception:
            db = None
            close_db = False
            
    if db:
        try:
            from app.models.traffic import Violation, FineByState, LawSection
            v_rec = db.query(Violation).filter(
                (Violation.category == violation.lower()) | 
                (Violation.name.ilike(violation))
            ).first()
            if v_rec:
                state_str = state or ""
                if state_str.lower() in ["national", "central"]:
                    state_str = ""
                fine_entry = db.query(FineByState).filter(
                    FineByState.violation_id == v_rec.id,
                    FineByState.state.ilike(state_str)
                ).first()
                if not fine_entry and state_str != "":
                    fine_entry = db.query(FineByState).filter(
                        FineByState.violation_id == v_rec.id,
                        FineByState.state == ""
                    ).first()
                if fine_entry:
                    amount = fine_entry.fine_repeat_max if repeat else fine_entry.fine_max
                    amount = amount or fine_entry.fine_max or 0
                    
                    sec_rec = db.query(LawSection).filter(LawSection.violation_id == v_rec.id).first()
                    section = sec_rec.section_code if sec_rec else "N/A"
                    act_name = sec_rec.act_name if sec_rec else "Motor Vehicles Act 2019"
                    
                    return {
                        "violation": v_rec.name,
                        "state": state or "National",
                        "fine_inr": amount,
                        "repeat": repeat,
                        "section": section,
                        "act_name": act_name,
                        "details": fine_entry.details
                    }
        except Exception as e:
            print(f"[calculate_challan] DB query failed: {e}")
        finally:
            if close_db and db:
                db.close()

    # Hardcoded fallback mapping
    base_fines = {
        "no_helmet":    {"first": 1000, "repeat": 1000},
        "no_seatbelt":  {"first": 1000, "repeat": 1000},
        "overspeeding": {"first": 2000, "repeat": 4000},
        "drunk_driving":{"first": 10000,"repeat": 15000},
        "no_insurance": {"first": 2000, "repeat": 4000},
        "use_of_phone": {"first": 1000, "repeat": 10000},
    }
    fine_data = base_fines.get(violation.lower(), {"first": 500, "repeat": 1000})
    amount = fine_data["repeat"] if repeat else fine_data["first"]
    return {
        "violation": violation,
        "state": state or "National",
        "fine_inr": amount,
        "repeat": repeat,
        "section": "N/A",
        "act_name": "Motor Vehicles Act 2019",
        "details": ""
    }

