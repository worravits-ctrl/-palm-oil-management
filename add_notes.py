from models import db, Note
from app import create_app
from datetime import date

app = create_app()
with app.app_context():
    # เพิ่มข้อมูล Notes ตัวอย่าง
    note1 = Note(
        date=date(2025, 9, 1),
        title='การใส่ปุ๋ยครั้งที่ 1',
        content='ใส่ปุ๋ยเคมี 16-16-16 จำนวน 10 กระสอบ ในพื้นที่แปลงที่ 1-5 สภาพอากาศดี ไม่มีฝนตก'
    )
    
    note2 = Note(
        date=date(2025, 9, 3),
        title='ตรวจสอบการเจริญเติบโต',
        content='ตรวจสอบต้นปาล์มในแปลง A-C พบว่าใบใหม่งามดี มีการออกดอกปกติ ไม่พบศัตรูพืช'
    )
    
    note3 = Note(
        date=date(2025, 9, 5),
        title='แผนการเก็บเกี่ยวสัปดาหน์หน้า',
        content='วางแผนเก็บเกี่ยวในแปลง D-F ประมาณ 200-250 ทะลาย คาดหวังน้ำหนักรวม 1,500 กก.'
    )
    
    note4 = Note(
        date=date(2025, 9, 7),
        title='บำรุงรักษาอุปกรณ์',
        content='ตรวจสอบและซ่อมแซมเครื่องมือเก็บเกี่ยว เปลี่ยนใบมีดตัดทะลาย เติมน้ำมันเครื่องยนต์'
    )
    
    note5 = Note(
        date=date(2025, 9, 9),
        title='รายงานสรุปสัปดาห์',
        content='สัปดาห์นี้เก็บเกี่ยวได้ 2,500 กก. รายได้ 19,500 บาท ค่าใช้จ่าย 12,500 บาท กำไรสุทธิ 7,000 บาท'
    )
    
    db.session.add(note1)
    db.session.add(note2)
    db.session.add(note3)
    db.session.add(note4)
    db.session.add(note5)
    
    db.session.commit()
    
    print("เพิ่มข้อมูล Notes ตัวอย่างเสร็จสิ้น:")
    print(f"- จำนวนรายการ: {Note.query.count()} รายการ")
    
    # แสดงรายการ Notes
    notes = Note.query.order_by(Note.date.desc()).all()
    for note in notes:
        print(f"- {note.date}: {note.title}")
