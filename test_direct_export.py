from models import db, HarvestIncome
from app import create_app
import pandas as pd
from io import BytesIO

app = create_app()
with app.app_context():
    try:
        # ทดสอบ export function โดยตรง
        print("Testing CSV export...")
        
        # ใช้ SQLAlchemy connection แทน
        with db.engine.connect() as conn:
            query = "SELECT * FROM harvest_income"
            df = pd.read_sql(query, conn)
        
        print(f"Found {len(df)} records")
        print("Columns:", df.columns.tolist())
        
        if len(df) > 0:
            print("Sample data:")
            print(df.head())
            
            # สร้าง CSV ใน memory
            output = BytesIO()
            df.to_csv(output, index=False, encoding="utf-8-sig")
            output.seek(0)
            
            # บันทึกเป็นไฟล์ทดสอบ
            with open('direct_export_test.csv', 'wb') as f:
                f.write(output.getvalue())
            
            print("CSV export successful - saved as direct_export_test.csv")
        else:
            print("No data found in harvest_income table")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
