import os
import json
import re
from sqlalchemy.orm import Session
from app.models.traffic import VehicleType, Violation, LawSection, FineByState

# Exact mapping for subsequent/repeat offenses based on MV Act 2019 rules
REPEAT_FINE_MAPS = {
    "no_helmet": (1000, 1000),
    "no_seatbelt": (1000, 1000),
    "child_safety": (1000, 1000),
    "overspeeding": (2000, 4000),
    "drunk_driving": (15000, 15000),
    "no_insurance": (4000, 4000),
    "no_dl": (5000, 5000),
    "use_of_phone": (10000, 10000),
    "triple_riding": (1000, 1000),
    "emergency_obstruction": (10000, 10000),
    "juvenile_offense": (25000, 25000),
    "passenger_overload": (200, 200),
    "goods_overload": (20000, 40000),
    "no_rc": (10000, 10000),
    "no_puc": (10000, 10000),
    "racing": (10000, 10000),
}

def clean_section_code(section_str: str) -> str:
    # Match "Section 194D" or "Section 194B(1)"
    m = re.search(r"Section\s+([0-9A-Z\(\)]+)", section_str, re.IGNORECASE)
    if m:
        return m.group(1)
    return section_str.split(",")[0].replace("Section", "").strip()

def seed_database(db: Session):
    # 1. Seed Vehicle Types if empty
    if db.query(VehicleType).count() == 0:
        vehicle_types_data = [
            {"code": "2W", "label": "2-wheeler"},
            {"code": "4W", "label": "4-wheeler / LMV"},
            {"code": "HV", "label": "Heavy Vehicle"},
            {"code": "all", "label": "All Vehicles"}
        ]
        for vt in vehicle_types_data:
            db.add(VehicleType(**vt))
        db.commit()

    # 2. Seed Violations and Fines
    if db.query(Violation).count() == 0:
        data_path = os.path.join(os.path.dirname(__file__), "../../../ai-services/data/violation_fines.json")
        if not os.path.exists(data_path):
            print(f"[Seeder Warning] JSON data path not found at {data_path}")
            return
        
        with open(data_path, "r", encoding="utf-8") as f:
            laws = json.load(f)

        for item in laws:
            category = item.get("category", "")
            violation_name = item.get("violation", "")
            vehicle_type = item.get("vehicle_type", "all")
            state = item.get("state", "")  # Empty string represents central/national law
            fine_min = item.get("fine_min", 0)
            fine_max = item.get("fine_max", 0)
            section_str = item.get("section", "")
            penalty_details = item.get("penalty_details", "")

            # Get or create violation record
            violation = db.query(Violation).filter(Violation.category == category).first()
            if not violation:
                violation = Violation(
                    category=category,
                    name=violation_name,
                    default_vehicle_type=vehicle_type
                )
                db.add(violation)
                db.flush()  # populate violation.id

            # Add law section if not exists
            sect_code = clean_section_code(section_str)
            existing_section = db.query(LawSection).filter(
                LawSection.violation_id == violation.id,
                LawSection.section_code == sect_code
            ).first()
            
            if not existing_section:
                law_sec = LawSection(
                    violation_id=violation.id,
                    section_code=sect_code,
                    act_name=section_str,  # Keep the full string as the legal source citation
                    penalty_details=penalty_details
                )
                db.add(law_sec)

            # Determine repeat fine range
            repeat_min, repeat_max = REPEAT_FINE_MAPS.get(category, (fine_min, fine_max))

            # Add fine by state entry
            fine_entry = FineByState(
                violation_id=violation.id,
                state=state,
                vehicle_type=vehicle_type,
                fine_min=fine_min,
                fine_max=fine_max,
                fine_repeat_min=repeat_min,
                fine_repeat_max=repeat_max,
                details=penalty_details
            )
            db.add(fine_entry)

        db.commit()
        print(f"[Seeder] Database successfully seeded with {db.query(Violation).count()} violations.")
