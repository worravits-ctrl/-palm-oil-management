from models import *
from app import create_app

app = create_app()
with app.app_context():
    print(f"✅ จำนวนต้นปาล์ม: {Palm.query.count()} ต้น")
    print(f"✅ จำนวนผู้ใช้: {User.query.count()} คน")
    print(f"✅ จำนวนรายการรายได้: {HarvestIncome.query.count()} รายการ")
    print(f"✅ จำนวนรายการปุ๋ย: {FertilizerRecord.query.count()} รายการ")
    print(f"✅ จำนวนรายการเก็บเกี่ยว: {HarvestDetail.query.count()} รายการ")
    print(f"✅ จำนวนบันทึกเหตุการณ์: {Note.query.count()} รายการ")
    
    print("\n🌴 ตัวอย่างโค้ดต้นปาล์ม 10 ต้นแรก:")
    for palm in Palm.query.limit(10):
        print(f"   - {palm.code}")
