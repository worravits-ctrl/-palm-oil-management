# 🌴 Palm Oil Farm Management System

ระบบจัดการสวนปาล์มน้ำมันแบบครบถ้วน พร้อม AI Chatbot ด้วย Google Gemini

## ✨ ฟีเจอร์หลัก

### 🏠 หน้าหลัก
- แดชบอร์ดภาพรวมสวนปาล์ม
- สถิติรายได้และค่าใช้จ่าย
- ข้อมูลต้นปาล์ม 312 ต้น (A1-L26)

### 💰 จัดการรายได้
- บันทึกรายได้จากการขายทะลายปาล์ม
- ระบุน้ำหนัก ราคา ค่าแรงเก็บ
- คำนวณรายได้สุทธิอัตโนมัติ
- Export/Import ข้อมูล CSV

### 🌱 จัดการค่าใช้จ่ายปุ๋ย
- บันทึกการซื้อปุ๋ยแต่ละชนิด
- ระบุจำนวนกระสอบ ราคา ค่าแรงหว่าน
- ติดตามต้นทุนการดูแลรักษา

### 🌾 รายละเอียดการเก็บเกี่ยว
- บันทึกจำนวนทะลายที่ตัดแต่ละต้น
- ระบุวันที่เก็บเกี่ยว
- หมายเหตุสภาพของต้นปาล์ม

### 📝 จดบันทึกประจำวัน
- บันทึกเหตุการณ์สำคัญ
- ข้อสังเกตการดูแลสวน
- แผนงานการจัดการ

### 🤖 AI Chatbot (Google Gemini)
- ตอบคำถามเป็นภาษาไทย
- ค้นหาข้อมูลแบบยืดหยุ่น
- คำนวณวันตัดปาล์มครั้งต่อไป (วันขายล่าสุด + 15 วัน)
- นับจำนวนทะลายที่ตัดตามช่วงเวลา
- วิเคราะห์รายได้และค่าใช้จ่าย

## 🛠️ เทคโนโลยีที่ใช้

- **Backend:** Flask 3.0.3
- **Database:** SQLite with SQLAlchemy 2.0.32
- **AI:** Google Gemini AI 0.8.3
- **Frontend:** HTML5, CSS3, JavaScript
- **Authentication:** Flask-Login
- **Forms:** WTForms
- **Language:** ภาษาไทย + ปฏิทินพุทธศักราช

## 🚀 การติดตั้งและใช้งาน

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/palm-oil-management.git
cd palm-oil-management
```

### 2. สร้าง Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. ตั้งค่า Environment Variables
สร้างไฟล์ `.env`:
```
SECRET_KEY=your-secret-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

### 5. สร้างฐานข้อมูล
```bash
python db_init.py
python create_palms.py
```

### 6. รันแอปพลิเคชัน
```bash
python app.py
```

เปิดเบราว์เซอร์ไปที่: http://localhost:8000

## 📋 ข้อมูลระบบ

### โครงสร้างฐานข้อมูล
- **users:** ข้อมูลผู้ใช้งาน
- **palms:** ข้อมูลต้นปาล์ม 312 ต้น (A1-L26)
- **harvest_income:** รายได้จากการขายปาล์ม
- **fertilizer_records:** ค่าใช้จ่ายปุ๋ย
- **harvest_details:** รายละเอียดการเก็บเกี่ยวรายต้น
- **notes:** บันทึกประจำวัน

### การใช้งาน AI Chatbot
- ไปที่เมนู "Chat กับ AI"
- ถามคำถามเป็นภาษาไทยได้
- ตัวอย่างคำถาม:
  - "รายได้เดือนกันยายน"
  - "ตัดปาล์มครั้งต่อไปเมื่อไหร่?"
  - "จำนวนทะลายที่ตัดเดือนนี้"
  - "ค่าปุ๋ยปีนี้ทั้งหมด"

## 🔧 การพัฒนาเพิ่มเติม

### การเพิ่มฟีเจอร์
- อ่านไฟล์ `PROJECT_DOCUMENTATION.md` สำหรับรายละเอียดสถาปัตยกรรม
- อ่านไฟล์ `AI_DEVELOPMENT_PROMPT.md` สำหรับการพัฒนาด้วย AI

### การตั้งค่า Google Gemini API
1. ไปที่ https://aistudio.google.com/app/apikey
2. สมัครบัญชี Google (ฟรี)
3. สร้าง API Key
4. ใส่ใน `.env` file
5. รีสตาร์ทแอป

## 🤝 การมีส่วนร่วม

ยินดีรับการมีส่วนร่วมในการพัฒนา! กรุณา:
1. Fork repository
2. สร้าง feature branch
3. Commit การเปลี่ยนแปลง
4. Push ไปยัง branch
5. สร้าง Pull Request

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ

## 👨‍💻 ผู้พัฒนา

พัฒนาโดย AI Assistant พร้อมด้วยเทคโนโลยี GitHub Copilot

---

🌴 **สำหรับเกษตรกรปาล์มน้ำมันยุคใหม่** 🤖
