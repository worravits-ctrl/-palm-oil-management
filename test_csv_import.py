#!/usr/bin/env python3
"""
Test script สำหรับทดสอบ CSV import functionality
"""

import csv
from io import StringIO
from datetime import datetime
from app import create_app
from models import db, FertilizerRecord

def test_fertilizer_csv_parsing():
    """ทดสอบการ parse CSV สำหรับ fertilizer"""
    
    # อ่านไฟล์ CSV ทดสอบ
    with open('test_fertilizer.csv', 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    print("CSV Content:")
    print(content)
    print("-" * 50)
    
    # Parse CSV
    stream = StringIO(content)
    reader = csv.DictReader(stream)
    
    print("Headers:", reader.fieldnames)
    print("-" * 50)
    
    count = 0
    for i, row in enumerate(reader, 1):
        print(f"Row {i}: {row}")
        
        # Test field extraction
        date_val = row.get("date") or row.get("Date") or row.get("วันที่")
        item_val = row.get("item") or row.get("Item") or row.get("รายการ")
        
        print(f"  Extracted - date: {date_val}, item: {item_val}")
        
        if not date_val or not item_val:
            print("  ⚠️  Missing required fields")
            continue
            
        # Test date parsing
        parsed_date = None
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_val).strip(), fmt).date()
                print(f"  ✅ Date parsed with format {fmt}: {parsed_date}")
                break
            except:
                continue
        
        if not parsed_date:
            print(f"  ❌ Date parsing failed for: {date_val}")
            continue
        
        # Test other fields
        try:
            sacks = float(row.get("sacks", 0) or row.get("Sacks", 0) or row.get("ถุง", 0))
            unit_price = float(row.get("unit_price", 0) or row.get("Unit Price", 0) or row.get("ราคาต่อหน่วย", 0))
            spreading_wage = float(row.get("spreading_wage", 0) or row.get("Spreading Wage", 0) or row.get("ค่าแรง", 0))
            note = row.get("note") or row.get("Note") or row.get("หมายเหตุ") or ""
            
            total_amount = sacks * unit_price + spreading_wage
            
            print(f"  ✅ Numbers parsed - sacks: {sacks}, unit_price: {unit_price}, spreading_wage: {spreading_wage}")
            print(f"  ✅ Total amount calculated: {total_amount}")
            
            count += 1
            
        except Exception as e:
            print(f"  ❌ Number parsing error: {e}")
            continue
    
    print(f"\nTotal processable rows: {count}")

def test_with_app_context():
    """ทดสอบใน app context จริง"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*50)
        print("Testing with Flask app context")
        print("="*50)
        
        # ตรวจสอบว่ามี FertilizerRecord อยู่แล้วหรือไม่
        existing_count = FertilizerRecord.query.count()
        print(f"Existing fertilizer records: {existing_count}")
        
        # ทดสอบการสร้าง record ใหม่
        test_record = FertilizerRecord(
            date=datetime(2024, 1, 15).date(),
            item="ทดสอบ",
            sacks=10.0,
            unit_price=450.0,
            spreading_wage=100.0,
            total_amount=4600.0,
            note="ทดสอบจากสคริปต์"
        )
        
        try:
            db.session.add(test_record)
            db.session.commit()
            print("✅ Test record created successfully")
            
            # ลบ test record
            db.session.delete(test_record)
            db.session.commit()
            print("✅ Test record deleted successfully")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_fertilizer_csv_parsing()
    test_with_app_context()