# 🔑 วิธีแก้ไขปัญหา Google API Key

## ❌ ปัญหาที่พบ
```
API key not valid. Please pass a valid API key.
```

## ✅ วิธีแก้ไขทีละขั้นตอน

### ขั้นตอนที่ 1: ตรวจสอบ API Key ปัจจุบัน
1. เปิดไฟล์ `.env`
2. ดูที่บรรทัด `GOOGLE_API_KEY=...`
3. ตรวจสอบว่า API Key มีความยาวประมาณ 39 ตัวอักษร

### ขั้นตอนที่ 2: สร้าง API Key ใหม่
1. ไปที่ https://aistudio.google.com/app/apikey
2. ล็อกอินด้วย Google Account
3. กดปุ่ม **"Create API Key"**
4. เลือก **"Create API key in new project"** (แนะนำ)
5. คัดลอก API Key ใหม่ที่ได้

### ขั้นตอนที่ 3: อัปเดต API Key
1. เปิดไฟล์ `.env` ใน VS Code
2. แก้ไขบรรทัด:
   ```
   GOOGLE_API_KEY=ใส่-api-key-ใหม่-ตรงนี้
   ```
3. **ห้าม** ใส่เครื่องหมาย " หรือ ' ครอบ API Key
4. บันทึกไฟล์ (Ctrl+S)

### ขั้นตอนที่ 4: รีสตาร์ทแอป
1. กดปุ่ม **Ctrl+C** ในเทอร์มินัล เพื่อหยุดแอป
2. รันคำสั่ง `python app.py` ใหม่
3. ทดสอบ Chatbot ที่ http://127.0.0.1:8000/ai/chat

## 💡 เคล็ดลับ

### API Key ที่ถูกต้อง:
```
GOOGLE_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### API Key ที่ผิด:
```
GOOGLE_API_KEY="AIzaSyBxxxxxxx"  ❌ (มีเครื่องหมาย ")
GOOGLE_API_KEY=your-api-key-here ❌ (ไม่ใช่ API จริง)
```

## 🚨 หากยังใช้ไม่ได้

1. **ตรวจสอบโควต้า**: ไปที่ https://aistudio.google.com/app/apikey ดูการใช้งาน
2. **รอสักครู่**: API Key ใหม่อาจใช้เวลา 1-2 นาทีในการเริ่มทำงาน
3. **ลองสร้างใหม่**: ลบ API Key เก่าและสร้างใหม่
4. **ตรวจสอบการเชื่อมต่อ**: ต้องมีอินเทอร์เน็ต

## 📊 ข้อจำกัดของ API ฟรี

- **15 requests/minute**
- **ไม่จำกัดรายวัน** (สำหรับ Gemini 1.5 Flash)
- **ไม่ต้องใส่บัตรเครดิต**

หากทำตามขั้นตอนแล้วยังไม่ได้ ให้ลองสร้าง Google Account ใหม่และทำใหม่ทั้งหมด
