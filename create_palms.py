from models import db, Palm

# Import Flask app
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create a basic app context
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# สร้างข้อมูลต้นปาล์ม A1-L26 จำนวน 312 ต้น
with app.app_context():
    # ตรวจสอบว่ามีข้อมูลแล้วไหม
    existing_count = Palm.query.count()
    print(f"ต้นปาล์มในฐานข้อมูล: {existing_count} ต้น")
    
    if existing_count == 0:
        print("กำลังสร้างข้อมูลต้นปาล์ม...")
        
        rows = 'ABCDEFGHIJKL'  # 12 แถว
        palm_codes = []
        
        for row in rows:
            for col in range(1, 27):  # 1-26
                code = f"{row}{col}"
                palm_codes.append(code)
        
        # สร้างข้อมูลต้นปาล์ม
        for code in palm_codes:
            palm = Palm(code=code)
            db.session.add(palm)
        
        db.session.commit()
        print(f"สร้างต้นปาล์มสำเร็จ: {len(palm_codes)} ต้น")
        
        # แสดงตัวอย่าง
        print("ตัวอย่างรหัสต้นปาล์ม:")
        print(f"แถว A: A1, A2, ..., A26")
        print(f"แถว L: L1, L2, ..., L26")
        print(f"รหัสแรก: {palm_codes[0]}")
        print(f"รหัสสุดท้าย: {palm_codes[-1]}")
    else:
        print("ข้อมูลต้นปาล์มมีอยู่แล้ว")
        
        # แสดงตัวอย่างข้อมูล
        first_palm = Palm.query.first()
        last_palm = Palm.query.order_by(Palm.id.desc()).first()
        print(f"ต้นแรก: {first_palm.code if first_palm else 'ไม่มี'}")
        print(f"ต้นสุดท้าย: {last_palm.code if last_palm else 'ไม่มี'}")
