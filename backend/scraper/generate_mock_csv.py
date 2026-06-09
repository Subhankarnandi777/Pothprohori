import csv
import os
import random
from datetime import datetime, timedelta

def generate_mock_csv():
    print("Generating mock dataset for Indian_Traffic_Violations.csv...")
    
    num_records = 500
    random.seed(42)
    start_date = datetime(2025, 1, 1)
    
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Indian_Traffic_Violations.csv")
    
    categories = ['Speeding', 'No Helmet', 'No Seatbelt', 'Drunk Driving', 'Red Light Jump']
    fines = {'Speeding': 1000, 'No Helmet': 1000, 'No Seatbelt': 1000, 'Drunk Driving': 10000, 'Red Light Jump': 5000}
    weights = [0.4, 0.25, 0.15, 0.05, 0.15]
    states = ['DL', 'WB', 'MH', 'KA', 'UP', 'TN']
    comment_opts = ["No Comment", "Caught on camera", "Refused to pay", "First time offender"]
    comment_weights = [0.7, 0.1, 0.1, 0.1]
    
    with open(out_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Time', 'Violation_ID', 'Violation_Category', 'Fine_Amount', 'Helmet_Worn', 'Seatbelt_Worn', 'Registration_State', 'Vehicle_Age', 'Comments'])
        
        for _ in range(num_records):
            days_offset = random.randint(0, 365)
            d = start_date + timedelta(days=days_offset)
            date_str = d.strftime("%Y-%m-%d")
            time_str = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
            
            violation_id = random.randint(1000, 9999)
            cat = random.choices(categories, weights=weights, k=1)[0]
            fine = fines[cat] + random.randint(-100, 200)
            
            helmet = 'Yes' if cat != 'No Helmet' else 'No'
            seatbelt = 'Yes' if cat != 'No Seatbelt' else 'No'
            state = random.choice(states)
            age = random.randint(1, 15)
            
            comment = random.choices(comment_opts, weights=comment_weights, k=1)[0]
            
            writer.writerow([date_str, time_str, violation_id, cat, fine, helmet, seatbelt, state, age, comment])
            
    print(f"Successfully generated mock dataset with {num_records} rows at {out_path}")

if __name__ == "__main__":
    generate_mock_csv()
