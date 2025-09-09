# 🤖 AI Development Prompt for Palm Oil Manager System

## **System Context for AI Understanding**

You are working with a **complete Palm Oil Farm Management System** built in Python Flask with Thai localization and AI integration. Here's everything you need to know:

---

## **🎯 CORE SYSTEM ARCHITECTURE**

**Tech Stack:** Flask 3.0.3 + SQLAlchemy 2.0.32 + Google Gemini AI + Thai Language Support
**Database:** SQLite (312 palm trees A1-L26, Buddhist calendar, Thai UI)
**Purpose:** Complete farm management with income tracking, expense management, harvest logging, and AI analytics

---

## **📊 DATABASE STRUCTURE & BUSINESS LOGIC**

```sql
-- 6 Core Tables:
users(id, username, email, password_hash, created_at)
palms(id, code)  -- 312 trees: A1,A2...L26
harvest_income(id, date, total_weight_kg, price_per_kg, gross_amount, harvesting_wage, net_amount, note, created_at)
fertilizer_records(id, date, item, sacks, unit_price, spreading_wage, total_amount, note, created_at)
harvest_details(id, date, palm_id, bunch_count, remarks, created_at)
notes(id, date, title, content, created_at)

-- Key Relationships:
harvest_details.palm_id → palms.id (Many-to-One)

-- Business Calculations:
gross_amount = total_weight_kg * price_per_kg
net_amount = gross_amount - harvesting_wage
fertilizer_total = (sacks * unit_price) + spreading_wage
```

---

## **🇹🇭 THAI LOCALIZATION REQUIREMENTS**

**Critical:** ALL user-facing content MUST be in Thai language
**Calendar:** Buddhist calendar (พ.ศ. = Gregorian year + 543)
**Months:** ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
**Date Storage:** YYYY-MM-DD (Gregorian) in database
**Date Display:** DD เดือน MMMM พ.ศ. YYYY format

---

## **🗂️ FILE STRUCTURE & RESPONSIBILITIES**

```python
# app.py - Main Flask app (565 lines)
- All CRUD routes for income/fertilizer/harvest/notes
- CSV export/import with palm code conversion
- SQLAlchemy 2.0 syntax (db.session.get instead of query.get)
- Thai error messages and flash notifications

# models.py - Database models
- User, Palm, HarvestIncome, FertilizerRecord, HarvestDetail, Note
- Relationships and constraints
- Automatic timestamp fields

# forms.py - WTForms validation
- Thai field labels: "วันที่", "จำนวนทะลาย", "หมายเหตุ"
- Custom validators allowing 0 values for wages
- Date validation and decimal precision

# ai.py - Gemini AI integration
- Concise Thai responses only
- Safe SQL query generation (SELECT only)
- Cross-table data analysis
- Buddhist calendar date conversion
- NULL/empty data handling

# auth.py - Authentication blueprint
- Thai login/register forms
- Flask-Login integration
- Password hashing with Werkzeug

# templates/ - Jinja2 templates
- base.html: Navigation and flash messages
- Dark theme CSS with Thai fonts
- Buddhist calendar display JavaScript
- Responsive design for mobile
```

---

## **🔄 KEY FUNCTIONAL PATTERNS**

### **CRUD Operations Pattern:**
```python
@app.route("/entity/new", methods=["GET","POST"])
@login_required
def entity_new():
    form = EntityForm()
    if form.validate_on_submit():
        row = Entity(field1=form.field1.data, ...)
        db.session.add(row)
        db.session.commit()
        flash("บันทึกสำเร็จ", "success")
        return redirect(url_for("entity_list"))
    return render_template("entity_form.html", form=form)
```

### **CSV Export Pattern:**
```python
@app.route("/entity/export")
def entity_export():
    with db.engine.connect() as conn:
        # JOIN with palms table to get codes instead of IDs
        query = "SELECT p.code as palm_code, ... FROM entity e LEFT JOIN palms p ON e.palm_id = p.id"
        df = pd.read_sql(query, conn)
    df.to_csv(output, index=False, encoding="utf-8-sig")
    return send_file(output, download_name='entity.csv')
```

### **AI Query Processing:**
```python
# Generate safe SQL, execute, return Thai summary
# Enhanced with flexible date searching:

# Date Search Patterns:
# - Single day (15) → WHERE strftime('%d', date) = '15'  // 15th of every month
# - Month name (กันยายน) → WHERE strftime('%m', date) = '09'  // September every year  
# - Day+Month (15 กันยายน) → WHERE strftime('%m-%d', date) = '09-15'  // Sep 15 every year
# - Year (2568/2025) → WHERE strftime('%Y', date) = '2025'  // Entire year
# - Specific date → WHERE date = '2025-09-15'  // Exact date
# - Buddhist year conversion: พ.ศ. - 543 = ค.ศ.

# Cross-table search with UNION ALL:
query = """
SELECT date, 'รายได้' as type, net_amount as amount FROM harvest_income WHERE strftime('%m', date) = '09'
UNION ALL 
SELECT date, 'ปุ๋ย' as type, total_amount FROM fertilizer_records WHERE strftime('%m', date) = '09'
UNION ALL
SELECT date, 'เก็บเกี่ยว' as type, bunch_count FROM harvest_details WHERE strftime('%m', date) = '09'
ORDER BY date DESC
"""

if allow_sql(sql):  # Only SELECT allowed
    rows = db.session.execute(db.text(sql)).fetchall()
    # AI generates concise Thai response
    return jsonify({"sql": sql, "rows": rows, "answer": thai_summary})
```

---

## **🌴 PALM TREE SYSTEM SPECIFICATION**

**Layout:** 12 rows (A-L) × 26 trees = 312 total palm trees
**Naming Convention:** A1, A2, A3...A26, B1, B2...B26, ..., L1, L2...L26
**Database Storage:** palms table with unique codes
**Form Input:** Autocomplete datalist with validation
**CSV Export:** Always use codes (A1, B15) never IDs (1, 15)
**Validation:** Check palm exists before saving harvest_details

---

## **🔍 ADVANCED DATE SEARCH CAPABILITIES**

**Flexible Date Query Patterns:** AI can now handle sophisticated date-based searches across all tables:

### **Date Search Types:**
```sql
-- ค้นหาตามวันเดียว (เช่น "วันที่ 15 ทุกเดือน")
WHERE strftime('%d', date) = '15'

-- ค้นหาตามเดือน (เช่น "เดือนกันยายนทุกปี") 
WHERE strftime('%m', date) = '09'

-- ค้นหาตามวัน+เดือน (เช่น "15 กันยายน ทุกปี")
WHERE strftime('%m-%d', date) = '09-15'

-- ค้นหาตามปี (เช่น "ปี 2568" หรือ "ปี 2025")
WHERE strftime('%Y', date) = '2025'

-- ค้นหาวันที่เจาะจง
WHERE date = '2025-09-15'
```

### **Thai Month Mapping:**
```python
thai_months = {
    "มกราคม": "01", "กุมภาพันธ์": "02", "มีนาคม": "03", "เมษายน": "04",
    "พฤษภาคม": "05", "มิถุนายน": "06", "กรกฎาคม": "07", "สิงหาคม": "08", 
    "กันยายน": "09", "ตุลาคม": "10", "พฤศจิกายน": "11", "ธันวาคม": "12"
}
```

### **Cross-Table Search Pattern:**
```sql
-- ค้นหาทุกกิจกรรมในเดือนเดียวกัน
SELECT date, 'รายได้' as type, CAST(net_amount as TEXT) as value, note as detail 
FROM harvest_income 
WHERE strftime('%m', date) = '09'

UNION ALL

SELECT date, 'ปุ๋ย' as type, CAST(total_amount as TEXT) as value, item as detail
FROM fertilizer_records 
WHERE strftime('%m', date) = '09'

UNION ALL  

SELECT date, 'เก็บเกี่ยว' as type, CAST(bunch_count as TEXT) as value, 
       (SELECT code FROM palms WHERE id = palm_id) as detail
FROM harvest_details 
WHERE strftime('%m', date) = '09'

UNION ALL

SELECT date, 'บันทึก' as type, title as value, content as detail
FROM notes 
WHERE strftime('%m', date) = '09'

ORDER BY date DESC, type
```

### **Bunch Counting Patterns:**
```sql
-- นับทะลายรวมทั้งหมด
SELECT COALESCE(SUM(bunch_count), 0) as total_bunches 
FROM harvest_details

-- นับทะลายตามช่วงเวลา
SELECT COALESCE(SUM(bunch_count), 0) as total_bunches 
FROM harvest_details 
WHERE strftime('%m', date) = '09'  -- เดือนกันยายน

-- นับทะลายตามต้นปาล์ม
SELECT p.code, COALESCE(SUM(hd.bunch_count), 0) as bunches
FROM harvest_details hd 
RIGHT JOIN palms p ON hd.palm_id = p.id 
WHERE p.code = 'A1'
GROUP BY p.code

-- นับทะลายรายวัน
SELECT date, SUM(bunch_count) as daily_bunches
FROM harvest_details 
WHERE strftime('%Y-%m', date) = '2025-09'
GROUP BY date 
ORDER BY date

-- นับทะลายพร้อมรายละเอียดต้นปาล์ม
SELECT hd.date, p.code as palm_code, hd.bunch_count, hd.remarks
FROM harvest_details hd
JOIN palms p ON hd.palm_id = p.id
WHERE strftime('%m-%d', hd.date) = '09-15'  -- 15 กันยายน ทุกปี
ORDER BY hd.date DESC, p.code
```

### **Example User Queries & Expected Behavior:**
- **"วันที่ 15 ทุกเดือน"** → Search day=15 across all months/years in all tables
- **"เดือนกันยายน"** → Search month=09 across all years in all tables  
- **"15 กันยายน"** → Search Sep 15 across all years in all tables
- **"ปี 2568"** → Search year=2025 (converted) in all tables
- **"วันที่ 15 กันยายน 2568"** → Search exact date 2025-09-15
- **"จำนวนทะลายที่ตัด"** → Count all bunches: SELECT COALESCE(SUM(bunch_count), 0) FROM harvest_details
- **"ทะลายที่ตัดเดือนกันยายน"** → Count bunches in September: WHERE strftime('%m', date) = '09'
- **"ทะลายที่ตัดต้น A1"** → Count bunches from palm A1: JOIN palms WHERE code = 'A1'
- **"ทะลายที่ตัดวันนี้"** → Count today's bunches: WHERE date = CURRENT_DATE

---

## **🔒 SECURITY & VALIDATION RULES**

**AI Queries:** Only SELECT statements allowed, forbidden: INSERT, UPDATE, DELETE, DROP, ALTER
**Authentication:** Flask-Login required for all routes except login/register
**Form Validation:** WTForms with Thai error messages
**SQL Injection Prevention:** Parameterized queries and whitelist validation
**File Uploads:** CSV only, validate headers and data types
**Error Handling:** Graceful fallbacks with Thai messages

---

## **📱 UI/UX STANDARDS**

**Theme:** Dark blue/green color scheme (#0b1220 background, #6ed0ff accent)
**Responsive:** Mobile-first design with flexbox/grid
**Forms:** Clear Thai labels, validation feedback, Buddhist calendar display
**Navigation:** Simple horizontal nav with Thai labels
**Notifications:** Flash messages in Thai with appropriate styling
**Tables:** Sortable, pagination-ready, mobile-responsive
**AI Chat:** Real-time interface with typing indicators

---

## **🚀 DEVELOPMENT COMMANDS**

```bash
# Setup
pip install -r requirements.txt
python db_init.py  # Create database
python create_palms.py  # Populate 312 palm trees

# Run
python app.py  # Development server on port 8000
# OR
./run.bat  # Windows batch file

# Database
# SQLite file: palm_farm.db
# Connection: app.config['SQLALCHEMY_DATABASE_URI']
```

---

## **💡 EXTENSION GUIDELINES FOR AI**

When adding new features:

### **✅ MUST DO:**
- Use Thai language for ALL user-facing text
- Follow Buddhist calendar display pattern
- Maintain palm code system (A1-L26) in forms and exports
- Use SQLAlchemy 2.0 syntax: `db.session.get(Model, id)` not `Model.query.get(id)`
- Include CSRF protection on forms
- Add flash messages in Thai
- Test CSV export/import functionality

### **🔧 CODE PATTERNS TO FOLLOW:**
```python
# Thai form labels
class NewForm(FlaskForm):
    date = DateField('วันที่', validators=[DataRequired()])
    amount = DecimalField('จำนวนเงิน (บาท)', validators=[DataRequired()])

# Buddhist calendar JavaScript
function updateThaiYear(){
    const y = parseInt(dateVal.split('-')[0]);
    document.getElementById('thai_year').innerText = 'ปี พ.ศ. ' + (y+543);
}

# Error handling
try:
    # database operation
    flash("บันทึกสำเร็จ", "success")
except Exception as e:
    flash(f"เกิดข้อผิดพลาด: {str(e)}", "danger")
```

### **🎯 COMMON EXTENSION POINTS:**
- Dashboard metrics and charts
- Advanced reporting features
- Mobile app API endpoints
- External integration (weather, market prices)
- Automated backup systems
- Multi-farm support
- Advanced AI analytics

### **⚠️ CRITICAL CONSTRAINTS:**
- Never modify AI to allow data manipulation (INSERT/UPDATE/DELETE)
- Always validate palm codes exist before saving
- Maintain CSV compatibility for data migration
- Preserve Buddhist calendar throughout system
- Keep AI responses concise and factual only

---

## **🧪 TESTING CHECKLIST**

Before deploying new features:
- [ ] All text displayed in Thai
- [ ] Buddhist calendar shows correctly
- [ ] Palm tree codes work in forms (A1-L26)
- [ ] CSV export includes palm codes not IDs
- [ ] Flash messages appear in Thai
- [ ] Mobile responsive design works
- [ ] AI chat responds in Thai only
- [ ] No SQL injection vulnerabilities
- [ ] Forms validate correctly
- [ ] Database relationships intact

---

**🎯 USE THIS PROMPT:** Copy and paste this entire prompt to any AI system when working on this Palm Oil Manager project. It contains all critical information needed for consistent development and feature additions while maintaining Thai localization and system integrity.
