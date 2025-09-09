from app import create_app
from models import db
import pandas as pd

app = create_app()
with app.app_context():
    # ทดสอบ query ต่างๆ
    print("=== ทดสอบ Export Queries ===")
    
    try:
        # Test harvest_income
        query1 = "SELECT * FROM harvest_income"
        df1 = pd.read_sql(query1, db.session.bind)
        print(f"✅ harvest_income: {len(df1)} rows")
        
        # Test fertilizer_records  
        query2 = "SELECT * FROM fertilizer_records"
        df2 = pd.read_sql(query2, db.session.bind)
        print(f"✅ fertilizer_records: {len(df2)} rows")
        
        # Test harvest_details with join
        query3 = """
        SELECT hd.date, p.code as palm_code, hd.bunch_count, hd.remarks
        FROM harvest_details hd
        JOIN palms p ON p.id = hd.palm_id
        ORDER BY hd.date DESC
        """
        df3 = pd.read_sql(query3, db.session.bind)
        print(f"✅ harvest_details: {len(df3)} rows")
        
        # Test notes
        query4 = "SELECT * FROM notes ORDER BY date DESC"
        df4 = pd.read_sql(query4, db.session.bind)
        print(f"✅ notes: {len(df4)} rows")
        
        print("\n🎉 ทุก Query ทำงานได้ปกติ!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
