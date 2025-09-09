from models import db, Palm, HarvestDetail
from app import create_app
from datetime import date

app = create_app()
with app.app_context():
    # เพิ่มข้อมูลการเก็บเกี่ยวรายต้นตัวอย่าง
    palms = Palm.query.limit(10).all()  # เอาต้นปาล์ม 10 ต้นแรก
    
    total_bunches = 0
    for i, palm in enumerate(palms):
        # เพิ่มข้อมูลการเก็บเกี่ยวหลายครั้ง
        harvest1 = HarvestDetail(
            date=date(2025, 9, 1),
            palm_id=palm.id,
            bunch_count=3 + (i % 3),  # 3-5 ทะลาย
            remarks=f'เก็บเกี่ยวครั้งที่ 1 ต้น {palm.code}'
        )
        
        harvest2 = HarvestDetail(
            date=date(2025, 9, 5),
            palm_id=palm.id,
            bunch_count=2 + (i % 4),  # 2-5 ทะลาย
            remarks=f'เก็บเกี่ยวครั้งที่ 2 ต้น {palm.code}'
        )
        
        db.session.add(harvest1)
        db.session.add(harvest2)
        total_bunches += harvest1.bunch_count + harvest2.bunch_count
    
    db.session.commit()
    
    print(f"เพิ่มข้อมูลการเก็บเกี่ยวรายต้นเสร็จสิ้น:")
    print(f"- จำนวนรายการ: {HarvestDetail.query.count()} รายการ")
    print(f"- จำนวนทะลายรวม: {total_bunches} ทะลาย")
    
    # ตรวจสอบข้อมูลในฐานข้อมูล
    total_bunches_db = db.session.query(db.func.sum(HarvestDetail.bunch_count)).scalar() or 0
    print(f"- จำนวนทะลายรวมจากฐานข้อมูล: {total_bunches_db} ทะลาย")
