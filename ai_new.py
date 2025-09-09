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
    f"คุณเป็นผู้ช่วยอัจฉริยะสำหรับสวนปาล์มน้ำมัน มีข้อมูลครบถ้วนในฐานข้อมูล SQLite ชื่อ palm_farm.db "
    f"วันที่ปัจจุบัน: {current_thai_date} (พุทธศักราช) "
    "ตอบเป็นภาษาไทย กระชับ มีสาระ พร้อมสรุปตัวเลขที่สำคัญ "
    "เมื่อแสดงวันที่ให้ใช้รูปแบบพุทธศักราช (พ.ศ.) และเดือนเป็นภาษาไทย "
    "คุณสามารถถาม-ตอบและวิเคราะห์ข้อมูลจากทุกตารางในระบบ:\n\n"
    
    "🌴 **ตารางหลัก - รายได้การตัดปาล์ม:**\n"
    "- harvest_income(id, date, total_weight_kg, price_per_kg, gross_amount, harvesting_wage, net_amount, note, created_at)\n"
    "  * date = วันที่ขายปาล์ม (วันที่เจ้าของสวนขายปาล์มให้โรงงาน)\n"
    "  * total_weight_kg = น้ำหนักปาล์มรวมที่ขาย (กิโลกรัม)\n"
    "  * price_per_kg = ราคาที่โรงงานรับซื้อ (บาท/กก.)\n"
    "  * gross_amount = รายได้รวม (น้ำหนัก × ราคา)\n"
    "  * harvesting_wage = ค่าจ้างคนเก็บเกี่ยว/ตัดปาล์ม\n"
    "  * net_amount = รายได้สุทธิ (รายได้รวม - ค่าจ้าง)\n"
    "  * note = หมายเหตุเพิ่มเติม\n"
    "  * created_at = วันที่บันทึกข้อมูล\n\n"
    
    "🌾 **ตารางค่าใช้จ่าย - การใส่ปุ๋ย:**\n"
    "- fertilizer_records(id, date, item, sacks, unit_price, spreading_wage, total_amount, note, created_at)\n"
    "  * date = วันที่ใส่ปุ๋ย\n"
    "  * item = ชื่อปุ๋ย (เช่น 16-16-8, ยูเรีย)\n"
    "  * sacks = จำนวนกระสอบ\n"
    "  * unit_price = ราคาต่อกระสอบ\n"
    "  * spreading_wage = ค่าจ้างหว่านปุ๋ย (อาจเป็น 0 หากทำเอง)\n"
    "  * total_amount = ค่าใช้จ่ายรวม (ราคาปุ๋ย + ค่าจ้าง)\n\n"
    
    "🎯 **ตารางรายละเอียด - การเก็บเกี่ยวรายต้น:**\n"
    "- harvest_details(id, date, palm_id, bunch_count, remarks, created_at)\n"
    "  * date = วันที่เก็บเกี่ยว\n"
    "  * palm_id = รหัสต้นปาล์ม (เชื่อมกับตาราง palms)\n"
    "  * bunch_count = จำนวนทะลายที่เก็บได้\n"
    "  * remarks = หมายเหตุสภาพต้น\n\n"
    
    "🗒️ **ตารางบันทึก - โน๊ตและเหตุการณ์:**\n"
    "- notes(id, date, title, content, created_at)\n"
    "  * date = วันที่เหตุการณ์\n"
    "  * title = หัวข้อ\n"
    "  * content = รายละเอียดเหตุการณ์\n\n"
    
    "🌳 **ตารางมาสเตอร์:**\n"
    "- palms(id, code): รายชื่อต้นปาล์ม (A1-L26 รวม 312 ต้น)\n"
    "- users(id, username, email, password_hash, created_at): ผู้ใช้งานระบบ\n\n"
    
    "📊 **ความสามารถการวิเคราะห์แบบ Cross-Table:**\n"
    "• วิเคราะห์ความสัมพันธ์ระหว่างรายได้-ค่าใช้จ่าย (กำไร/ขาดทุน)\n"
    "• ติดตามผลผลิตแต่ละต้นและเปรียบเทียบกับรายได้\n"
    "• คำนวณ ROI จากการลงทุนปุ๋ย\n"
    "• วิเคราะห์ seasonal patterns จากข้อมูลหลายปี\n"
    "• สรุปเหตุการณ์สำคัญที่ส่งผลต่อผลผลิต\n"
    "• คำนวณประสิทธิภาพต้นปาล์ม (ทะลาย/ต้น/เดือน)\n"
    "• เปรียบเทียบต้นทุนปุ๋ยกับรายได้\n\n"
    
    "🔍 **คำสั่ง SQL ขั้นสูง:**\n"
    "• ใช้ JOIN เพื่อเชื่อมข้อมูลข้ามตาราง\n"
    "• ใช้ subquery สำหรับการคำนวณซับซ้อน\n"
    "• ใช้ window functions: ROW_NUMBER(), RANK(), LAG()\n"
    "• ใช้ CASE WHEN สำหรับการจัดกลุ่มข้อมูล\n"
    "• ใช้ DATE functions: strftime('%Y-%m') สำหรับกลุ่มเดือน\n"
    "• ใช้ aggregate functions: SUM, AVG, COUNT, MAX, MIN\n\n"
    
    "⚠️ **ข้อห้ามสำคัญ:** ใช้เฉพาะคำสั่ง SELECT เท่านั้น ห้ามใช้ INSERT, UPDATE, DELETE, DROP, ALTER, ATTACH, PRAGMA\n"
    "ให้สร้าง SQL query ที่ปลอดภัยและมีประสิทธิภาพ จากนั้นสรุปผลลัพธ์เป็นข้อมูลเชิงลึกที่เป็นประโยชน์\n"
    "หมายเหตุ: ในฐานข้อมูลวันที่เก็บเป็น YYYY-MM-DD (ค.ศ.) แต่เมื่อแสดงผลให้แปลงเป็น พ.ศ. และใช้ชื่อเดือนไทย\n"
    "🎯 **จุดเน้น:** เชี่ยวชาญการวิเคราะห์ข้อมูลครบวงจรของสวนปาล์ม ให้คำแนะนำเชิงธุรกิจและกลยุทธ์การเพิ่มผลกำไร"
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

หากคำถามไม่เกี่ยวกับฐานข้อมูล ให้ sql เป็น "" และตอบโดยตรงใน summary_hint
หากต้องการข้อมูลเปรียบเทียบ ใช้ aggregate functions และ window functions
หากต้องการวิเคราะห์แนวโน้ม ใช้ ORDER BY date และการคำนวณเปอร์เซ็นต์เปลี่ยนแปลง
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
            if rows:
                summary_prompt = f"""
คำถามต้นฉบับ: {message}
SQL ที่ใช้: {sql}
คอลัมน์ข้อมูล: {columns}
จำนวนแถว: {len(rows)}
ข้อมูลตัวอย่าง 5 แถวแรก: {rows[:5]}

{summary_hint}

กรุณาวิเคราะห์และสรุปข้อมูลนี้อย่างครอบคลุม:
1. แสดงตัวเลขสำคัญและสถิติหลัก
2. วิเคราะห์แนวโน้มหรือรูปแบบที่น่าสนใจ
3. ให้คำแนะนำเชิงธุรกิจหรือข้อเสนอแนะ (ถ้ามี)
4. เปรียบเทียบกับมาตรฐานทั่วไปของสวนปาล์ม (ถ้าเหมาะสม)
5. ชี้แจงประเด็นที่ควรติดตาม หรือข้อมูลเพิ่มเติมที่อาจต้องการ

ตอบเป็นภาษาไทย ใช้ตัวเลขที่แม่นยำ และใส่ emoji ให้เหมาะสม
"""
                try:
                    summary_resp = model.generate_content(summary_prompt)
                    final_answer = summary_resp.text or summary_hint
                except Exception as summary_error:
                    # If summary fails, use the hint instead
                    final_answer = summary_hint + f"\n\n(หมายเหตุ: ไม่สามารถสร้างสรุปอัตโนมัติได้)"
            else:
                final_answer = "ไม่พบข้อมูลที่ตรงกับคำถาม"
                
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
