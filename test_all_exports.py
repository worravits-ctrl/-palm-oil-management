from models import db, HarvestIncome, FertilizerRecord, HarvestDetail, Note
from app import app
import pandas as pd
from io import BytesIO

with app.app_context():
    
    tables_to_test = [
        ('harvest_income', 'harvest_income.csv'),
        ('fertilizer_records', 'fertilizer_records.csv'),
        ('harvest_details', 'harvest_details.csv'),
        ('notes', 'notes.csv')
    ]
    
    for table_name, filename in tables_to_test:
        try:
            print(f"\nTesting {table_name} export...")
            
            with db.engine.connect() as conn:
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql(query, conn)
            
            print(f"Found {len(df)} records")
            
            if len(df) > 0:
                print("Columns:", df.columns.tolist())
                
                # สร้าง CSV ใน memory
                output = BytesIO()
                df.to_csv(output, index=False, encoding="utf-8-sig")
                output.seek(0)
                
                # บันทึกเป็นไฟล์ทดสอบ
                with open(f'test_{filename}', 'wb') as f:
                    f.write(output.getvalue())
                
                print(f"✅ {table_name} export successful")
            else:
                print(f"⚠️  No data in {table_name}")
                
        except Exception as e:
            print(f"❌ Error with {table_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== Export Test Complete ===")
