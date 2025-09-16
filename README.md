# 🌴 Palm Oil Farm Management System

ระบบจัดการสวนปาล์มน้ำมันแบบครบถ้วน พร้อม AI Chatbot ด้วย Google Gemini และรองรับ Turso Database

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
- **Database:** Turso (SQLite distributed) / SQLite local
- **AI:** Google Gemini AI 0.8.3
- **Frontend:** HTML5, CSS3, JavaScript
- **Authentication:** Flask-Login
- **Forms:** WTForms
- **Language:** ภาษาไทย + ปฏิทินพุทธศักราช

## 🚀 การติดตั้งและใช้งาน

### 1. Clone Repository
```bash
git clone https://github.com/worravits-ctrl/-palm-oil-management.git
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
สร้างไฟล์ `.env` จาก `.env.example`:
```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env`:
```
SECRET_KEY=your-secret-key-here
GOOGLE_API_KEY=your-google-api-key-here

# สำหรับ Turso (Production)
TURSO_DATABASE_URL=your-turso-database-url
TURSO_AUTH_TOKEN=your-turso-auth-token

# หรือสำหรับ Local Development
# DATABASE_URL=sqlite:///palm_farm.db
```

### 5. รันแอปพลิเคชัน
```bash
# Development
python app.py

# หรือ Production
python server.py
```

เปิดเบราว์เซอร์ไปที่: http://localhost:5000

## 🐳 การ Deploy ด้วย Docker

### ใช้ Docker Compose
```bash
# สร้างไฟล์ .env ก่อน
cp .env.example .env
# แก้ไข .env ตามต้องการ

# รันด้วย Docker Compose
docker-compose up -d

# หยุดการทำงาน
docker-compose down
```

### ใช้ Docker เฉยๆ
```bash
# Build image
docker build -t palm-oil-app .

# รัน container
docker run -p 5000:5000 --env-file .env palm-oil-app
```

## ☁️ การ Deploy ไป Turso + Cloud Platform

### 1. สร้าง Turso Database
```bash
# ติดตั้ง Turso CLI
npm install -g @tursodatabase/turso-cli

# เข้าสู่ระบบ
turso auth login

# สร้าง database
turso db create palm-oil-db

# ดู database URL และ token
turso db show palm-oil-db
```

### 2. ตั้งค่า Environment Variables
```bash
# ใน .env หรือ environment variables ของ cloud platform
TURSO_DATABASE_URL=your-turso-url
TURSO_AUTH_TOKEN=your-turso-token
SECRET_KEY=your-secret-key
GOOGLE_API_KEY=your-google-api-key
```

### 3. Deploy ไป Cloud Platform

#### **Railway**
```bash
# ติดตั้ง Railway CLI
npm install -g @railway/cli

# เข้าสู่ระบบ
railway login

# Deploy
railway deploy
```

#### **Render**
```yaml
# render.yaml
services:
  - type: web
    name: palm-oil-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python server.py
    envVars:
      - key: TURSO_DATABASE_URL
        value: your-turso-url
      - key: TURSO_AUTH_TOKEN
        value: your-turso-token
      - key: SECRET_KEY
        value: your-secret-key
      - key: GOOGLE_API_KEY
        value: your-google-api-key
```

#### **Vercel**
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server.py"
    }
  ]
}
```

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
