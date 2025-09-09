from models import db, HarvestIncome
from app import app
from datetime import date, timedelta

with app.app_context():
    # เพิ่มข้อมูลรายได้การตัดปาล์มตัวอย่าง
    sample_data = [
        {
            'date': date.today() - timedelta(days=30),
            'total_weight_kg': 1500.0,
            'price_per_kg': 8.50,
            'gross_amount': 12750.0,
            'harvesting_wage': 1500.0,
            'net_amount': 11250.0,
            'note': 'ขายให้โรงงานน้ำมันปาล์ม ABC'
        },
        {
            'date': date.today() - timedelta(days=25),
            'total_weight_kg': 1200.0,
            'price_per_kg': 9.00,
            'gross_amount': 10800.0,
            'harvesting_wage': 1200.0,
            'net_amount': 9600.0,
            'note': 'ราคาปาล์มขึ้น'
        },
        {
            'date': date.today() - timedelta(days=20),
            'total_weight_kg': 1800.0,
            'price_per_kg': 8.75,
            'gross_amount': 15750.0,
            'harvesting_wage': 1800.0,
            'net_amount': 13950.0,
            'note': 'ผลผลิตดีมาก'
        },
        {
            'date': date.today() - timedelta(days=15),
            'total_weight_kg': 1100.0,
            'price_per_kg': 9.25,
            'gross_amount': 10175.0,
            'harvesting_wage': 1000.0,
            'net_amount': 9175.0,
            'note': 'หว่านปุ๋ยแล้วเริ่มออกผล'
        },
        {
            'date': date.today() - timedelta(days=10),
            'total_weight_kg': 1650.0,
            'price_per_kg': 9.50,
            'gross_amount': 15675.0,
            'harvesting_wage': 1650.0,
            'net_amount': 14025.0,
            'note': 'ราคาสูงสุดในเดือนนี้'
        }
    ]
    
    for data in sample_data:
        income = HarvestIncome(**data)
        db.session.add(income)
    
    db.session.commit()
    print(f"✅ เพิ่มข้อมูลรายได้การตัดปาล์ม {len(sample_data)} รายการ")
    
    # แสดงสรุปข้อมูล
    total_income = sum(d['net_amount'] for d in sample_data)
    total_weight = sum(d['total_weight_kg'] for d in sample_data)
    avg_price = sum(d['price_per_kg'] for d in sample_data) / len(sample_data)
    
    print(f"📊 สรุป:")
    print(f"   - รายได้รวม: {total_income:,.2f} บาท")
    print(f"   - น้ำหนักรวม: {total_weight:,.2f} กก.")
    print(f"   - ราคาเฉลี่ย: {avg_price:.2f} บาท/กก.")
