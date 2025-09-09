from app import create_app
from models import db, HarvestIncome
from datetime import date

app = create_app()
with app.app_context():
    # เพิ่มข้อมูลทดสอบ
    test_data = HarvestIncome(
        date=date.today(),
        total_weight_kg=100.0,
        price_per_kg=6.5,
        gross_amount=650.0,
        harvesting_wage=50.0,
        net_amount=600.0,
        note='ข้อมูลทดสอบ'
    )
    db.session.add(test_data)
    db.session.commit()
    print('เพิ่มข้อมูลทดสอบแล้ว')
