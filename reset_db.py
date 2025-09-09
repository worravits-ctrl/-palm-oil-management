from models import db, User, HarvestIncome, FertilizerRecord, Palm, HarvestDetail
from app import create_app
from datetime import date
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # ลบข้อมูลเก่าและสร้างใหม่
    db.drop_all()
    db.create_all()
    
    print("สร้างตารางใหม่เสร็จสิ้น")
    
    # สร้างผู้ใช้ admin
    admin_user = User(
        username='admin',
        email='admin@farm.com',
        password_hash=generate_password_hash('admin123')
    )
    db.session.add(admin_user)
    
    # สร้างข้อมูลต้นปาล์ม
    palm_codes = []
    for row in "ABCDEFGHIJKL":
        for col in range(1, 27):
            code = f"{row}{col}"
            palm = Palm(code=code)
            db.session.add(palm)
            palm_codes.append(code)
    
    # เพิ่มข้อมูลรายได้ตัวอย่าง
    income1 = HarvestIncome(
        date=date(2025, 9, 1),
        total_weight_kg=1000,
        price_per_kg=8.0,
        gross_amount=8000,
        harvesting_wage=500,
        net_amount=7500,
        note='รายได้ตัวอย่าง 1'
    )
    
    income2 = HarvestIncome(
        date=date(2025, 9, 5),
        total_weight_kg=1500,
        price_per_kg=8.5,
        gross_amount=12750,
        harvesting_wage=750,
        net_amount=12000,
        note='รายได้ตัวอย่าง 2'
    )
    
    # เพิ่มข้อมูลค่าใช้จ่ายปุ๋ยตัวอย่าง
    fertilizer1 = FertilizerRecord(
        date=date(2025, 8, 15),
        item='ปุ๋ยเคมี 16-16-16',
        sacks=10,
        unit_price=800,
        spreading_wage=1000,
        total_amount=9000,
        note='ปุ๋ยรอบที่ 1'
    )
    
    fertilizer2 = FertilizerRecord(
        date=date(2025, 8, 20),
        item='ปุ๋ยอินทรีย์',
        sacks=5,
        unit_price=600,
        spreading_wage=500,
        total_amount=3500,
        note='ปุ๋ยรอบที่ 2'
    )
    
    db.session.add(income1)
    db.session.add(income2)
    db.session.add(fertilizer1)
    db.session.add(fertilizer2)
    
    # บันทึกข้อมูลทั้งหมด
    db.session.commit()
    
    print("เพิ่มข้อมูลตัวอย่างเสร็จสิ้น:")
    print(f"- ผู้ใช้: {User.query.count()} คน")
    print(f"- ต้นปาล์ม: {Palm.query.count()} ต้น") 
    print(f"- รายได้: {HarvestIncome.query.count()} รายการ")
    print(f"- ค่าใช้จ่ายปุ๋ย: {FertilizerRecord.query.count()} รายการ")
    
    # ตรวจสอบผลรวม
    total_income = db.session.query(db.func.sum(HarvestIncome.net_amount)).scalar() or 0
    total_expense = db.session.query(db.func.sum(FertilizerRecord.total_amount)).scalar() or 0
    print(f"- รายได้สุทธิรวม: {total_income:,.2f} บาท")
    print(f"- ค่าใช้จ่ายปุ๋ยรวม: {total_expense:,.2f} บาท")
