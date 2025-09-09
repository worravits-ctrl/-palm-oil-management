from models import db, User
from app import create_app

app = create_app()
with app.app_context():
    # ทดสอบการตรวจสอบรหัสผ่าน
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f'พบผู้ใช้: {user.username}')
        print(f'Email: {user.email}')
        
        # ทดสอบรหัสผ่าน
        test_password = 'admin123'
        result = user.check_password(test_password)
        print(f'ทดสอบรหัสผ่าน "{test_password}": {result}')
        
        if not result:
            print('รหัสผ่านไม่ถูกต้อง - สร้างรหัสผ่านใหม่')
            user.set_password('admin123')
            db.session.commit()
            print('อัปเดตรหัสผ่านเสร็จสิ้น')
    else:
        print('ไม่พบผู้ใช้ admin')
