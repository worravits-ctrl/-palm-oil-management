# Palm Oil Manager + Gemini AI - Complete Project Documentation

## 🌴 **Project Overview**
A complete web-based palm oil farm management system built with Flask, featuring Thai localization, Buddhist calendar, and AI-powered analytics using Google Gemini.

**Key Technologies:** Flask 3.0.3, SQLAlchemy 2.0.32, Google Gemini AI 0.8.3, Python 3.11, SQLite, Thai language support

---

## 📁 **Project Structure**
```
palm_gemini_app/
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy database models
├── forms.py                # WTForms for input validation
├── ai.py                   # Gemini AI integration blueprint
├── auth.py                 # Authentication blueprint
├── config.py               # Configuration settings
├── db_init.py              # Database initialization
├── create_palms.py         # Utility to populate palm trees
├── requirements.txt        # Python dependencies
├── run.bat                 # Windows startup script
├── .env                    # Environment variables (API keys)
├── static/
│   └── style.css          # Dark theme CSS styling
├── templates/
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Dashboard overview
│   ├── login.html         # User authentication
│   ├── register.html      # User registration
│   ├── income_*.html      # Income management templates
│   ├── fertilizer_*.html  # Fertilizer management templates
│   ├── harvest_*.html     # Harvest management templates
│   ├── notes.html         # Notes management
│   └── chat.html          # AI chatbot interface
└── palm_farm.db           # SQLite database
```

---

## 🗄️ **Database Schema**

### **Core Tables:**
```sql
-- User Management
users(id, username, email, password_hash, created_at)

-- Palm Tree Registry (312 trees: A1-L26)
palms(id, code)  -- code format: A1, A2, ..., L26

-- Income from Palm Sales
harvest_income(
    id, date, total_weight_kg, price_per_kg, 
    gross_amount, harvesting_wage, net_amount, 
    note, created_at
)

-- Fertilizer Expenses
fertilizer_records(
    id, date, item, sacks, unit_price, 
    spreading_wage, total_amount, note, created_at
)

-- Individual Tree Harvest Details
harvest_details(
    id, date, palm_id, bunch_count, remarks, created_at
)

-- Event Notes
notes(id, date, title, content, created_at)
```

### **Relationships:**
- `harvest_details.palm_id` → `palms.id` (Many-to-One)
- All tables include `created_at` timestamp
- Date fields use YYYY-MM-DD format (Gregorian) but display in Buddhist calendar (พ.ศ.)

---

## 🎯 **Core Features**

### **1. Income Management (รายได้การตัดปาล์ม)**
**Routes:** `/income`, `/income/new`, `/income/edit/<id>`, `/income/delete/<id>`
**Functions:**
- Record palm oil sales with automatic net amount calculation
- Edit existing income records with validation
- Delete records with confirmation
- CSV export/import functionality
- Display in Buddhist calendar format

**Business Logic:**
```python
net_amount = gross_amount - harvesting_wage
gross_amount = total_weight_kg * price_per_kg
```

### **2. Fertilizer Management (การใส่ปุ๋ย)**
**Routes:** `/fertilizer`, `/fertilizer/new`, `/fertilizer/edit/<id>`, `/fertilizer/delete/<id>`
**Functions:**
- Track fertilizer purchases and application costs
- Support zero wages (self-application)
- Automatic total cost calculation
- CSV export/import with error handling

**Business Logic:**
```python
total_amount = (sacks * unit_price) + spreading_wage
spreading_wage = 0 if self_applied else wage_amount
```

### **3. Harvest Tracking (เก็บเกี่ยวรายต้น)**
**Routes:** `/harvest`, `/harvest/new`, `/harvest/edit/<id>`, `/harvest/delete/<id>`
**Functions:**
- Track individual palm tree harvest details
- 312 palm trees (A1-L26) with autocomplete selection
- Bunch count recording with remarks
- CSV export with palm codes (not IDs)

**Palm Tree System:**
- **Layout:** 12 rows (A-L) × 26 trees per row = 312 total trees
- **Naming:** A1, A2, ..., A26, B1, B2, ..., L26
- **Database:** Stored as relationships, exported as codes

### **4. Notes Management (บันทึกเหตุการณ์)**
**Routes:** `/notes`, `/notes/edit/<id>`, `/notes/delete/<id>`
**Functions:**
- Record important farm events and observations
- Date-based organization
- Edit and delete capabilities
- CSV export for record keeping

### **5. AI Analytics (Gemini Chatbot)**
**Routes:** `/chat`, `/api/chat`
**Functions:**
- Natural language queries about farm data
- Cross-table data analysis
- Buddhist calendar date conversion
- Concise, factual responses without recommendations
- Safe SQL query generation and execution

---

## 🇹🇭 **Thai Localization Features**

### **Buddhist Calendar System:**
```python
thai_year = gregorian_year + 543
thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", ...]
display_format = "วันที่ DD เดือน MMMM พ.ศ. YYYY"
```

### **Language Elements:**
- All UI text in Thai
- Form labels and validation messages in Thai
- AI responses exclusively in Thai
- Error messages in Thai
- CSV headers can be Thai or English

---

## 🔧 **Technical Implementation**

### **Flask Application Structure:**
```python
# app.py - Main application
app = Flask(__name__)
app.config.from_object(Config)

# Database initialization
db.init_app(app)
login_manager.init_app(app)

# Blueprint registration
app.register_blueprint(auth_bp)
app.register_blueprint(ai_bp)
```

### **Form Validation (forms.py):**
```python
class HarvestIncomeForm(FlaskForm):
    date = DateField('วันที่', validators=[DataRequired()])
    total_weight_kg = DecimalField('น้ำหนักรวม (กก.)', validators=[DataRequired()])
    # Custom validators for Thai context
```

### **AI Integration (ai.py):**
```python
# Gemini AI configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# System prompt for Thai palm farm context
SYSTEM_PROMPT = """
Thai palm oil farm assistant with SQLite database access.
Responds in Thai, uses Buddhist calendar, concise answers only.
Tables: harvest_income, fertilizer_records, harvest_details, notes, palms, users
Safety: SELECT queries only, no data modification
"""
```

### **Database Models (models.py):**
```python
class HarvestIncome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    net_amount = db.Column(db.Numeric(10, 2), nullable=False)
    # Automatic timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Palm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    # Relationship to harvest details
    harvest_details = db.relationship('HarvestDetail', backref='palm')
```

---

## 📊 **Data Flow & Business Logic**

### **Income Recording Flow:**
1. User inputs sale data (weight, price, wage)
2. System calculates gross_amount = weight × price
3. System calculates net_amount = gross - wage
4. Data validated and stored with timestamp
5. Dashboard updated with new totals

### **CSV Export/Import:**
```python
# Export with palm codes instead of IDs
def harvest_export():
    query = """
    SELECT hd.date, p.code as palm_code, hd.bunch_count, hd.remarks
    FROM harvest_details hd
    LEFT JOIN palms p ON hd.palm_id = p.id
    """
    # Convert to CSV with proper Thai encoding (utf-8-sig)

# Import with palm code lookup
def harvest_import():
    palm = Palm.query.filter_by(code=palm_code).first()
    if palm:
        record.palm_id = palm.id
```

### **AI Query Processing:**
1. User question in Thai → Gemini AI
2. AI generates safe SQL query
3. Execute query on SQLite database
4. Return results to AI for Thai summary
5. Display concise answer with data

---

## 🔒 **Security & Error Handling**

### **SQL Injection Prevention:**
```python
def allow_sql(sql: str) -> bool:
    sql_lc = sql.lower()
    if not sql_lc.strip().startswith("select"):
        return False
    forbidden = ["insert", "update", "delete", "drop", "alter", "create"]
    return not any(w in sql_lc for w in forbidden)
```

### **Authentication:**
- Flask-Login for session management
- Password hashing with Werkzeug
- Login required decorators on sensitive routes
- Secure user registration and login forms

### **Data Validation:**
- WTForms validators for all inputs
- Custom validation for Thai context
- CSV import error handling
- Graceful API error handling for Gemini AI

---

## 🚀 **Deployment & Configuration**

### **Environment Setup:**
```bash
# requirements.txt key dependencies
Flask==3.0.3
SQLAlchemy==2.0.32
google-generativeai==0.8.3
pandas==2.2.2
WTForms==3.1.1
Flask-Login==0.6.3

# .env configuration
GOOGLE_API_KEY=your_gemini_api_key
SECRET_KEY=your_flask_secret_key
```

### **Database Initialization:**
```python
# db_init.py
def create_database():
    db.create_all()
    # Create palm trees A1-L26 (312 total)
    for row in 'ABCDEFGHIJKL':
        for num in range(1, 27):
            palm = Palm(code=f'{row}{num}')
            db.session.add(palm)
```

### **Production Considerations:**
- Use PostgreSQL instead of SQLite for production
- Configure proper WSGI server (Gunicorn)
- Set up proper logging and monitoring
- Secure API key management
- Regular database backups

---

## 🎨 **UI/UX Features**

### **Dark Theme Styling:**
- Custom CSS with Thai-friendly fonts
- Responsive design for mobile/desktop
- Color scheme: Dark blue/green theme
- Status indicators and animations
- Thai date display formatting

### **User Experience:**
- Autocomplete for palm tree selection
- Buddhist calendar display alongside input
- Flash messages in Thai
- CSV upload with progress indication
- Real-time AI chat interface

---

## 🔄 **API Endpoints**

### **Web Routes:**
```python
GET  /                     # Dashboard
GET  /login               # Authentication
POST /login               # Process login
GET  /income              # Income list
POST /income/new          # Create income
GET  /income/edit/<id>    # Edit form
POST /income/edit/<id>    # Update income
POST /income/delete/<id>  # Delete income
GET  /income/export       # Download CSV
POST /income/import       # Upload CSV
# Similar patterns for fertilizer, harvest, notes
```

### **AI API:**
```python
GET  /chat               # Chat interface
POST /api/chat           # Process AI queries
# Request: {"message": "รายได้เดือนนี้เท่าไหร่?"}
# Response: {"sql": "SELECT...", "rows": [...], "answer": "15,000 บาท"}
```

---

## 🧪 **Testing & Development**

### **Development Workflow:**
1. Start with `python app.py` or `run.bat`
2. Access at `http://127.0.0.1:8000`
3. Create admin user via registration
4. Initialize palm trees with `create_palms.py`
5. Test all CRUD operations
6. Verify AI chat functionality

### **Sample Data Structure:**
```json
{
  "income_record": {
    "date": "2025-09-09",
    "total_weight_kg": 150.5,
    "price_per_kg": 8.50,
    "gross_amount": 1279.25,
    "harvesting_wage": 200.00,
    "net_amount": 1079.25
  },
  "harvest_detail": {
    "date": "2025-09-09",
    "palm_code": "A15",
    "bunch_count": 3,
    "remarks": "ผลดี"
  }
}
```

---

## 📝 **Usage Instructions for AI Development**

When extending this project, focus on:

1. **Maintain Thai Language Consistency**: All new features should support Thai input/output
2. **Follow Buddhist Calendar Pattern**: Convert Gregorian dates for display
3. **Preserve Data Relationships**: Maintain palm tree code system (A1-L26)
4. **Security First**: Always validate inputs, especially in AI queries
5. **CSV Compatibility**: Ensure export/import features remain functional
6. **Mobile Responsive**: Test new UI elements on mobile devices
7. **AI Query Safety**: Never allow data modification through AI interface

**Key Extension Points:**
- Add new farm metrics in dashboard
- Extend AI capabilities with new query types
- Add reporting and analytics features
- Implement data visualization charts
- Add notification/reminder systems
- Integrate with external APIs (weather, prices)

This system provides a solid foundation for comprehensive palm oil farm management with modern AI integration.
