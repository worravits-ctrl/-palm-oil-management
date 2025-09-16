# 🌴 Palm Oil Farm Management System

ระบบจัดการสวนปาล์มน้ำมันแบบครบถ้วน พร้อม AI Chatbot ด้วย Google Gemini และรองรับ Turso Database

## ✨ ฟีเจอร์หลัก

### 🏠 หน้าหลัก
- แดชบอร์ดภาพรวมสวนปาล์ม
- สถิติรายได้และค่าใช้จ่าย
- ข้อมูลต้นปาล์ม 312 ต้น (A1-L26)

### 💰 จัดการรายได้
- บันทึกรายได้จากการขายทะลายปาล์ม
- ระบุน้ำหนัก ราคา ค่าแรงเก็## 📚 ไฟล์สำคัญในโปรเจค

- `app.py` - แอปหลัก Flask
- `models.py` - โมเดลฐานข้อมูล
- `config.py` - การตั้งค่า
- `requirements.txt` - Dependencies
- `turso_guide.md` - คู่มือ Turso ฉบับเต็ม
- `setup_turso.bat` - สคริปต์ตั้งค่า Turso สำหรับ Windows
- `test_db.py` - ทดสอบการเชื่อมต่อฐานข้อมูล
- `migrate_db.py` - Migrate ข้อมูลจาก SQLite ไป Turso
- `.env.example` - Template สำหรับ environment variablesรายได้สุทธิอัตโนมัติ
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

### 4. ตั้งค่า Turso Database (แนะนำ)
```bash
# รัน setup script
# Windows
setup_turso.bat

# หรือทำด้วยตนเอง:
# ติดตั้ง Turso CLI
npm install -g @tursodatabase/turso-cli

# เข้าสู่ระบบ
turso auth login

# สร้างฐานข้อมูล
turso db create palm-oil-management

# ดูข้อมูลการเชื่อมต่อ
turso db show palm-oil-management
```

### 5. ตั้งค่า Environment Variables
สร้างไฟล์ `.env` จาก `.env.example`:
```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env` ด้วยข้อมูลจาก Turso:
```
TURSO_DATABASE_URL=libsql://your-database-url
TURSO_AUTH_TOKEN=your-auth-token
SECRET_KEY=your-secret-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

### 6. รันแอปพลิเคชัน
```bash
# Development
python app.py

# หรือ Production
python server.py
```

เปิดเบราว์เซอร์ไปที่: http://localhost:5000

## 🐳 การ Deploy ด้วย Docker

### ใช้ Docker Compose (แนะนำ)
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
# วิธีที่ 1: ใช้ Setup Script (แนะนำ)
# Windows
setup_turso.bat

# วิธีที่ 2: ทำด้วยตนเอง
# ติดตั้ง Turso CLI
npm install -g @tursodatabase/turso-cli

# เข้าสู่ระบบ
turso auth login

# สร้าง database
turso db create palm-oil-management

# ดู database URL และ token
turso db show palm-oil-management
```

### 2. เลือก Cloud Platform ที่ต้องการ Deploy

#### **🚂 Railway (แนะนำสำหรับผู้เริ่มต้น)**
```bash
# ติดตั้ง Railway CLI
npm install -g @railway/cli

# เข้าสู่ระบบ
railway login

# Deploy โดยอัตโนมัติ
railway deploy

# หรือ link โปรเจคที่มีอยู่
railway link
railway up
```

**ตั้งค่า Environment Variables ใน Railway:**
- TURSO_DATABASE_URL
- TURSO_AUTH_TOKEN
- SECRET_KEY
- GOOGLE_API_KEY

#### **⚡ Vercel (สำหรับ Static + Serverless)**
```bash
# ติดตั้ง Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# ตั้งค่า environment variables ใน Vercel dashboard
# หรือใช้ vercel.json
```

#### **🔧 Render (แนะนำ - รองรับ Docker และ Python อย่างสมบูรณ์)**

**ทำไมถึงแนะนำ Render:**
- ✅ รองรับ Docker และ Python web apps ได้ดี
- ✅ Free tier เพียงพอสำหรับเริ่มต้น
- ✅ Auto-scaling และ managed database
- ✅ ง่ายต่อการตั้งค่าและ deploy
- ✅ รองรับ custom domains

**ขั้นตอนการ Deploy:**

1. **สร้างบัญชี Render:**
   - ไปที่ https://render.com
   - สมัครบัญชีฟรี

2. **เชื่อมต่อ GitHub:**
   - ใน Dashboard คลิก "New" → "Web Service"
   - เลือก "Connect GitHub" และ authorize
   - ค้นหา repository: `worravits-ctrl/-palm-oil-management`

3. **ตั้งค่า Web Service:**
   ```
   Name: palm-oil-management
   Environment: Docker
   Branch: main
   Dockerfile Path: render.Dockerfile
   ```

4. **ตั้งค่า Environment Variables:**
   ```
   TURSO_DATABASE_URL → your-turso-database-url
   TURSO_AUTH_TOKEN → your-turso-auth-token
   SECRET_KEY → your-secret-key-here
   GOOGLE_API_KEY → your-google-api-key-here
   FLASK_ENV → production
   ```

5. **Deploy:**
   - คลิก "Create Web Service"
   - รอการ build และ deploy (ประมาณ 5-10 นาที)
   - เมื่อเสร็จจะได้ URL: `https://your-app-name.onrender.com`

**หรือใช้ render.yaml (วิธีอัตโนมัติ):**
```bash
# ใน Render Dashboard
# เลือก "New" → "Blueprint"
# Upload หรือ paste render.yaml จาก repository
```

**การตรวจสอบและแก้ปัญหา:**
```bash
# ดู logs ใน Render Dashboard
# หรือใช้ Health Check endpoint
curl https://your-app-name.onrender.com/health
```

#### **🐳 Docker (สำหรับ Self-hosted)**
```bash
# ใช้ Docker Compose
docker-compose up -d

# หรือใช้ Docker ธรรมดา
docker build -f render.Dockerfile -t palm-oil-app .
docker run -p 5000:5000 --env-file .env palm-oil-app
```

### 3. ตรวจสอบการทำงาน
```bash
# ทดสอบ database connection
python test_db.py

# ทดสอบ local ก่อน
python server.py
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

## 🔧 การแก้ปัญหา (Troubleshooting)

### ปัญหาที่พบบ่อย

#### ❌ Database Connection Error
```bash
# ตรวจสอบ Turso CLI
turso auth status

# ทดสอบการเชื่อมต่อ
turso db shell palm-oil-management "SELECT 1;"

# ตรวจสอบ environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('URL:', os.getenv('TURSO_DATABASE_URL')); print('Token:', '***' + os.getenv('TURSO_AUTH_TOKEN')[-4:] if os.getenv('TURSO_AUTH_TOKEN') else 'None')"
```

#### 🔄 Migrate ข้อมูลจาก SQLite ไป Turso
```bash
# ทดสอบ connection ก่อน
python test_db.py

# Migrate ข้อมูล (จะสร้าง backup อัตโนมัติ)
python migrate_db.py palm_farm.db

# หรือ migrate จากไฟล์อื่น
python migrate_db.py path/to/your/database.db
```

#### ❌ Google API Key Error
- ตรวจสอบ API key ที่ https://makersuite.google.com/app/apikey
- ตรวจสอบว่าเปิดใช้งาน Google AI Studio API แล้วหรือไม่
- ตรวจสอบ quota และ billing

#### ❌ Import CSV ไม่ได้
- ตรวจสอบ encoding ของไฟล์ CSV (UTF-8, UTF-8-SIG, TIS-620)
- ตรวจสอบ format ของวันที่ (DD/MM/YYYY)
- ตรวจสอบ header columns ให้ตรงกับระบบ

#### ❌ แอปไม่รันหลัง deploy
```bash
# ตรวจสอบ logs
# Railway: railway logs
# Render: ดูใน dashboard
# Vercel: vercel logs

# ทดสอบ local ก่อน
python server.py
```

### คำสั่งที่มีประโยชน์

```bash
# ดูรายการฐานข้อมูลทั้งหมด
turso db list

# ดูรายละเอียดฐานข้อมูล
turso db show palm-oil-management

# เข้า shell ของฐานข้อมูล
turso db shell palm-oil-management

# Backup ข้อมูล
turso db shell palm-oil-management ".backup backup.db"

# ดู logs ของฐานข้อมูล
turso db logs palm-oil-management
```

## 📋 คำถามที่พบบ่อย (FAQ)

### Q: Turso ฟรีหรือเปล่า?
A: มี Free tier ที่เพียงพอสำหรับการใช้งานส่วนตัวและธุรกิจขนาดเล็ก

### Q: สามารถใช้ SQLite แทน Turso ได้ไหม?
A: ได้ครับ ระบบรองรับทั้ง Turso และ SQLite local โดยอัตโนมัติ

### Q: ข้อมูลใน Turso ปลอดภัยไหม?
A: Turso ใช้ encryption และมีระบบ backup อัตโนมัติ

### Q: สามารถ migrate ข้อมูลจาก SQLite ไป Turso ได้ไหม?
A: ได้ครับ โดยใช้คำสั่ง SQL dump และ import

### Q: แอปนี้รองรับหลายภาษาหรือเปล่า?
A: ปัจจุบันรองรับภาษาไทยเป็นหลัก แต่สามารถขยายได้

## � ไฟล์สำคัญในโปรเจค

- `app.py` - แอปหลัก Flask
- `models.py` - โมเดลฐานข้อมูล
- `config.py` - การตั้งค่า
- `requirements.txt` - Dependencies
- `turso_guide.md` - คู่มือ Turso ฉบับเต็ม
- `setup_turso.bat` - สคริปต์ตั้งค่า Turso สำหรับ Windows
- `.env.example` - Template สำหรับ environment variables
