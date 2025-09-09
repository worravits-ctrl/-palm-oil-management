import sqlite3
import pandas as pd
from io import BytesIO

# เชื่อมต่อ database โดยตรง
conn = sqlite3.connect('palm_farm.db')

tables_to_test = [
    ('harvest_income', 'harvest_income.csv'),
    ('fertilizer_record', 'fertilizer_records.csv'),
    ('harvest_detail', 'harvest_details.csv'),
    ('note', 'notes.csv')
]

for table_name, filename in tables_to_test:
    try:
        print(f"\nTesting {table_name} export...")
        
        # ตรวจสอบว่าตารางมีอยู่จริง
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"❌ Table {table_name} does not exist")
            continue
        
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        
        print(f"Found {len(df)} records")
        
        if len(df) > 0:
            print("Columns:", df.columns.tolist())
            print("Sample data:")
            print(df.head(2))
            
            # สร้าง CSV ใน memory
            output = BytesIO()
            df.to_csv(output, index=False, encoding="utf-8-sig")
            output.seek(0)
            
            # บันทึกเป็นไฟล์ทดสอบ
            with open(f'test_{filename}', 'wb') as f:
                f.write(output.getvalue())
            
            print(f"✅ {table_name} export successful - saved as test_{filename}")
        else:
            print(f"⚠️  No data in {table_name}")
            
    except Exception as e:
        print(f"❌ Error with {table_name}: {e}")

conn.close()
print("\n=== Export Test Complete ===")
