import re
from flask import Blueprint, render_template, request, jsonify, current_app
from models import db
import google.generativeai as genai
from datetime import datetime

ai_bp = Blueprint("ai", __name__)

# ฟังก์ชันแปลงวันที่เป็นพุทธศักราช
def get_current_thai_date():
    now = datetime.now()
    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    thai_year = now.year + 543
    thai_month = thai_months[now.month - 1]
    return f"{now.day} {thai_month} {thai_year}"

# ข้อมูลวันที่ปัจจุบันในรูปแบบไทย
current_thai_date = get_current_thai_date()

SYSTEM_PROMPT = (
    f"คุณเป็นผู้ช่วยสำหรับสวนปาล์มน้ำมัน วันที่ปัจจุบัน: {current_thai_date} "
    "ตอบเป็นภาษาไทย สั้น กระชับ ตรงคำถาม ไม่ต้องวิเคราะห์หรือแนะนำเพิ่มเติม "
    "ใช้วันที่รูปแบบ พ.ศ. และเดือนภาษาไทย "
    "มีข้อมูลในฐานข้อมูล SQLite:\n\n"
    
    "**ตาราง:**\n"
    "• harvest_income: รายได้การขายปาล์ม (date, total_weight_kg, price_per_kg, gross_amount, harvesting_wage, net_amount)\n"
    "• fertilizer_records: ค่าใช้จ่ายปุ๋ย (date, item, sacks, unit_price, spreading_wage, total_amount)\n"
    "• harvest_details: การเก็บเกี่ยวรายต้น (date, palm_id, bunch_count, remarks)\n"
    "• notes: บันทึกเหตุการณ์ (date, title, content)\n"
    "• palms: ต้นปาล์ม A1-L26 (312 ต้น)\n"
    "• users: ผู้ใช้งานระบบ\n\n"
    
    "**การค้นหาข้อมูลตามวันที่:**\n"
    "• หากระบุ วัน เดียว (เช่น 15) → ค้นหาวันที่ 15 ทุกเดือนทุกปี: WHERE strftime('%d', date) = '15'\n"
    "• หากระบุ เดือน (เช่น กันยายน) → ค้นหาเดือนกันยายนทุกปี: WHERE strftime('%m', date) = '09'\n"
    "• หากระบุ วัน+เดือน (เช่น 15 กันยายน) → ค้นหาวันเดือนนั้นทุกปี: WHERE strftime('%m-%d', date) = '09-15'\n"
    "• หากระบุ ปี (เช่น 2568, 2025) → ค้นหาทั้งปีนั้น: WHERE strftime('%Y', date) = '2025'\n"
    "• หากระบุ วัน/เดือน/ปี แบบเจาะจง → ค้นหาวันที่เดียวกัน: WHERE date = '2025-09-15'\n"
    "• ชื่อเดือนไทย: มกราคม=01, กุมภาพันธ์=02, มีนาคม=03, เมษายน=04, พฤษภาคม=05, มิถุนายน=06, กรกฎาคม=07, สิงหาคม=08, กันยายน=09, ตุลาคม=10, พฤศจิกายน=11, ธันวาคม=12\n"
    "• ปี พ.ศ. → ค.ศ.: พ.ศ. - 543 (เช่น 2568 → 2025)\n\n"
    
    "**การนับจำนวนทะลายที่ตัด (harvest_details):**\n"
    "• นับทะลายรวม: SELECT COALESCE(SUM(bunch_count), 0) as total_bunches FROM harvest_details WHERE ...\n"
    "• นับทะลายตามต้น: SELECT p.code, SUM(hd.bunch_count) FROM harvest_details hd JOIN palms p ON hd.palm_id = p.id WHERE ... GROUP BY p.code\n"
    "• นับทะลายตามวันที่: SELECT date, SUM(bunch_count) FROM harvest_details WHERE ... GROUP BY date ORDER BY date\n"
    "• หากไม่ระบุเงื่อนไข → รวมทะลายทั้งหมดที่เคยตัด: SELECT COALESCE(SUM(bunch_count), 0) FROM harvest_details\n"
    "• แสดงรายละเอียด: ต้นปาล์มไหน วันไหน ตัดกี่ทะลาย\n\n"
    
    "**การคำนวณวันตัดปาล์มครั้งต่อไป:**\n"
    "• หากถาม 'ตัดปาล์มครั้งต่อไปเมื่อไหร่' ให้หาวันขายล่าสุด + 15 วัน\n"
    "• SQL: SELECT DATE(MAX(date), '+15 days') as next_harvest_date FROM harvest_income\n"
    "• หากมีข้อมูลการขาย ให้คำนวณและแสดงวันที่ครั้งต่อไป\n"
    "• แปลงเป็นปฏิทินไทย พ.ศ. พร้อมชื่อเดือนภาษาไทย\n"
    "• แสดงทั้งวันขายล่าสุดและวันตัดครั้งต่อไป\n\n"
    
    "**การค้นหาข้ามตาราง:**\n"
    "• ใช้ UNION ALL เพื่อค้นหาจากหลายตาราง พร้อมระบุประเภทข้อมูล\n"
    "• ตัวอย่าง: SELECT date, 'รายได้' as type, net_amount as amount FROM harvest_income WHERE ... UNION ALL SELECT date, 'ปุ๋ย' as type, total_amount FROM fertilizer_records WHERE ...\n"
    "• หาก SUM หรือ COUNT เป็น NULL ให้แสดง 0\n"
    "• ใช้ COALESCE(SUM(...), 0) สำหรับยอดรวม\n"
    "• หากไม่มีข้อมูลในช่วงที่ถาม ให้แสดงข้อมูลใกล้เคียง\n\n"
    
    "**คำสั่ง:** ใช้เฉพาะ SELECT ห้าม INSERT/UPDATE/DELETE\n"
    "**รูปแบบคำตอบ:** ตอบตรงคำถาม แสดงตัวเลขที่สำคัญ หากไม่มีข้อมูลให้บอกชัดเจน"
)

def allow_sql(sql: str) -> bool:
    sql_lc = sql.lower()
    # allow only select queries, no semicolons chaining
    if not sql_lc.strip().startswith("select"):
        return False
    forbidden = ["insert", "update", "delete", "drop", "alter", "attach", "pragma", "create", "replace"]
    return not any(w in sql_lc for w in forbidden)

@ai_bp.route("/chat")
def chat_page():
    return render_template("chat.html")

@ai_bp.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json(force=True)
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "ข้อความว่าง"}), 400

    api_key = current_app.config.get("GOOGLE_API_KEY", "")
    if not api_key or api_key == "your-google-api-key-here":
        return jsonify({
            "answer": "⚠️ ยังไม่ได้ตั้งค่า Google API Key\n\n" +
                     "📝 วิธีการตั้งค่า:\n" +
                     "1. ไปที่ https://aistudio.google.com/app/apikey\n" +
                     "2. สมัครบัญชี Google (ฟรี)\n" +
                     "3. กดปุ่ม 'Create API Key'\n" +
                     "4. คัดลอก API Key ที่ได้\n" +
                     "5. แก้ไขไฟล์ .env ใส่ API Key ใหม่\n" +
                     "6. รีสตาร์ทแอป\n\n" +
                     "💡 API Key ฟรีใช้ได้ 15 requests/minute"
        }), 200

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "not valid" in error_msg:
            return jsonify({
                "answer": "❌ Google API Key ไม่ถูกต้อง\n\n" +
                         "🔧 แก้ไขได้โดย:\n" +
                         "1. ตรวจสอบ API Key ใน .env ว่าถูกต้อง\n" +
                         "2. สร้าง API Key ใหม่ที่ https://aistudio.google.com/app/apikey\n" +
                         "3. อัปเดตไฟล์ .env ด้วย API Key ใหม่\n" +
                         "4. รีสตาร์ทแอป (Ctrl+C แล้วรันใหม่)\n\n" +
                         f"🔍 ข้อผิดพลาด: {error_msg[:100]}..."
            }), 200
        else:
            return jsonify({"answer": f"เกิดข้อผิดพลาดจากโมเดล: {error_msg[:200]}..."}), 200

    # Ask model to propose a single safe SELECT query
    prompt = f"""
{SYSTEM_PROMPT}

คำถามผู้ใช้: {message}

กรุณาวิเคราะห์คำถามและให้ข้อมูลตามรูปแบบ JSON:
{{
  "sql": "คำสั่ง SELECT ที่เหมาะสมที่สุด (1 บรรทัด) หรือ \" \" หากไม่ต้องการ SQL",
  "summary_hint": "แนวทางสรุปผลข้อมูลเป็นภาษาไทย พร้อมคำแนะนำเชิงธุรกิจ"
}}

เคล็ดลับการสร้าง SQL:
- ใช้ JOIN กับ palms เมื่อต้องการชื่อต้นปาล์ม: "JOIN palms p ON hd.palm_id = p.id"
- ใช้ strftime('%Y-%m') สำหรับการจัดกลุ่มตามเดือน
- ใช้ DATE('now') หรือ DATE('now', 'start of month') สำหรับวันที่ปัจจุบัน
- ใช้ subquery สำหรับการเปรียบเทียบข้อมูลข้ามตาราง
- ใช้ CASE WHEN สำหรับการจัดหมวดหมู่ข้อมูล
- สำหรับคำนวณวันตัดครั้งต่อไป: "SELECT MAX(date) as last_sale, DATE(MAX(date), '+15 days') as next_harvest FROM harvest_income"

หากคำถามไม่เกี่ยวกับฐานข้อมูล ให้ sql เป็น "" และตอบโดยตรงใน summary_hint
หากต้องการข้อมูลเปรียบเทียบ ใช้ aggregate functions และ window functions
หากต้องการวิเคราะห์แนวโน้ม ใช้ ORDER BY date และการคำนวณเปอร์เซ็นต์เปลี่ยนแปลง
หากถามเรื่องวันตัดปาล์มครั้งต่อไป ให้ใช้การคำนวณ date arithmetic ด้วย DATE(date, '+15 days')
"""
    try:
        resp = model.generate_content(prompt)
        text = resp.text or ""
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "not valid" in error_msg:
            return jsonify({
                "answer": "❌ Google API Key หมดอายุหรือไม่ถูกต้อง\n\n" +
                         "🔄 แก้ไขได้โดย:\n" +
                         "1. ไปที่ https://aistudio.google.com/app/apikey\n" +
                         "2. ลบ API Key เก่า (ถ้ามี)\n" +
                         "3. สร้าง API Key ใหม่\n" +
                         "4. อัปเดตไฟล์ .env\n" +
                         "5. รีสตาร์ทแอป\n\n" +
                         "💡 บางครั้ง API Key ใหม่อาจใช้เวลาสักครู่ในการเริ่มทำงาน"
            }), 200
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return jsonify({
                "answer": "⏰ เกินขีดจำกัดการใช้งาน API\n\n" +
                         "🔍 สาเหตุที่เป็นไปได้:\n" +
                         "• ใช้งานเกิน 15 requests/minute (ฟรี)\n" +
                         "• เกินโควต้ารายวัน\n" +
                         "• ใช้งานบ่อยเกินไป\n\n" +
                         "⏳ รอสักครู่แล้วลองใหม่ หรือตรวจสอบโควต้าที่ Google AI Studio"
            }), 200
        else:
            return jsonify({"answer": f"เกิดข้อผิดพลาดจากโมเดล: {error_msg[:200]}..."}), 200

    # best-effort JSON extraction
    import json, re
    match = re.search(r"\{[\s\S]*\}", text)
    sql = ""
    summary_hint = ""
    if match:
        try:
            obj = json.loads(match.group(0))
            sql = (obj.get("sql") or "").strip()
            summary_hint = (obj.get("summary_hint") or "").strip()
        except Exception:
            pass

    rows = []
    columns = []
    final_answer = ""
    
    if sql and allow_sql(sql):
        try:
            res = db.session.execute(db.text(sql))
            columns = list(res.keys())
            rows = [list(r) for r in res.fetchall()]
            
            # Generate final summary with AI
            if rows and any(any(cell is not None for cell in row) for row in rows):
                # มีข้อมูลจริง
                summary_prompt = f"""
คำถาม: {message}
ข้อมูล: {columns} ({len(rows)} แถว)
ตัวอย่าง: {rows[:3]}

ตอบสั้นๆ ตรงคำถาม แสดงตัวเลขสำคัญ ไม่ต้องวิเคราะห์หรือแนะนำเพิ่มเติม
ใช้ภาษาไทย รูปแบบ พ.ศ. หาก NULL ให้แสดงเป็น 0
"""
                try:
                    summary_resp = model.generate_content(summary_prompt)
                    final_answer = summary_resp.text or summary_hint
                except Exception as summary_error:
                    final_answer = summary_hint + f"\n\n(หมายเหตุ: ไม่สามารถสร้างสรุปอัตโนมัติได้)"
            else:
                # ไม่มีข้อมูลหรือเป็น NULL ทั้งหมด
                if "รายได้" in message.lower() or "เงิน" in message.lower() or "บาท" in message.lower():
                    final_answer = "0 บาท (ไม่มีข้อมูลในช่วงที่ระบุ)"
                elif "จำนวน" in message.lower() or "กี่" in message.lower():
                    final_answer = "0 รายการ (ไม่มีข้อมูลในช่วงที่ระบุ)"  
                else:
                    final_answer = "ไม่พบข้อมูลในช่วงเวลาที่ระบุ"
                
        except Exception as e:
            return jsonify({"answer": f"SQL ผิดพลาด: {str(e)[:200]}..."}), 200
    else:
        if sql:
            return jsonify({"answer": "SQL ไม่ปลอดภัย หรือไม่ได้เริ่มต้นด้วย SELECT"}), 200
        else:
            # Direct answer without SQL
            final_answer = summary_hint

    return jsonify({
        "sql": sql,
        "columns": columns,
        "rows": rows,
        "answer": final_answer
    })
