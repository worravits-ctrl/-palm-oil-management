import csv
import io
from io import BytesIO, StringIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Palm, HarvestIncome, FertilizerRecord, HarvestDetail, Note
from forms import (LoginForm, RegisterForm, HarvestIncomeForm, FertilizerRecordForm, 
                   HarvestDetailForm, NoteForm)
from auth import auth_bp
from ai import ai_bp
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///palm_farm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-google-api-key-here')

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'กรุณาเข้าสู่ระบบก่อนใช้งาน'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(ai_bp, url_prefix='/ai')

# Helper function for CSV export without pandas
def create_csv_response(data, headers, filename):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# Helper function for CSV import without pandas
def process_csv_file(file, required_columns):
    stream = StringIO(file.stream.read().decode("utf8"))
    reader = csv.DictReader(stream)
    data = []
    
    # Check if required columns exist
    if not all(col in reader.fieldnames for col in required_columns):
        return None, f"ไฟล์ CSV ต้องมีคอลัมน์: {', '.join(required_columns)}"
    
    for row in reader:
        data.append(row)
    
    return data, None

# Routes
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Get summary statistics
    total_income = db.session.query(db.func.sum(HarvestIncome.net_amount)).scalar() or 0
    total_fertilizer_cost = db.session.query(db.func.sum(FertilizerRecord.total_amount)).scalar() or 0
    total_harvest_count = db.session.query(db.func.sum(HarvestDetail.bunch_count)).scalar() or 0
    total_palms = db.session.query(Palm).count()
    
    # Get recent activities
    recent_income = db.session.query(HarvestIncome).order_by(HarvestIncome.sale_date.desc()).limit(5).all()
    recent_fertilizer = db.session.query(FertilizerRecord).order_by(FertilizerRecord.date.desc()).limit(5).all()
    recent_harvest = db.session.query(HarvestDetail).join(Palm).order_by(HarvestDetail.date.desc()).limit(5).all()
    recent_notes = db.session.query(Note).order_by(Note.date.desc()).limit(5).all()
    
    return render_template('index.html',
                         total_income=total_income,
                         total_fertilizer_cost=total_fertilizer_cost,
                         total_harvest_count=total_harvest_count,
                         total_palms=total_palms,
                         recent_income=recent_income,
                         recent_fertilizer=recent_fertilizer,
                         recent_harvest=recent_harvest,
                         recent_notes=recent_notes)

# Income routes
@app.route('/income')
@login_required
def income_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = db.session.query(HarvestIncome).order_by(HarvestIncome.sale_date.desc())
    
    # Search functionality
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            db.or_(
                HarvestIncome.note.contains(search),
                HarvestIncome.sale_date.contains(search)
            )
        )
    
    income_records = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Calculate totals
    total_gross = db.session.query(db.func.sum(HarvestIncome.gross_amount)).scalar() or 0
    total_wage = db.session.query(db.func.sum(HarvestIncome.harvesting_wage)).scalar() or 0
    total_net = db.session.query(db.func.sum(HarvestIncome.net_amount)).scalar() or 0
    
    return render_template('income_list.html', 
                         income_records=income_records,
                         total_gross=total_gross,
                         total_wage=total_wage,
                         total_net=total_net,
                         search=search)

@app.route('/income/new', methods=['GET', 'POST'])
@app.route('/income/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def income_form(id=None):
    form = HarvestIncomeForm()
    income_record = None
    
    if id:
        income_record = db.session.get(HarvestIncome, id)
        if not income_record:
            flash('ไม่พบข้อมูลรายได้', 'error')
            return redirect(url_for('income_list'))
    
    if form.validate_on_submit():
        if income_record:
            # Update existing record
            income_record.sale_date = form.sale_date.data
            income_record.palm_id = form.palm_id.data if form.palm_id.data else None
            income_record.total_weight_kg = form.total_weight_kg.data
            income_record.price_per_kg = form.price_per_kg.data
            income_record.harvesting_wage = form.harvesting_wage.data or 0
            income_record.note = form.note.data
        else:
            # Create new record
            income_record = HarvestIncome(
                sale_date=form.sale_date.data,
                palm_id=form.palm_id.data if form.palm_id.data else None,
                total_weight_kg=form.total_weight_kg.data,
                price_per_kg=form.price_per_kg.data,
                harvesting_wage=form.harvesting_wage.data or 0,
                note=form.note.data
            )
            db.session.add(income_record)
        
        # Calculate amounts
        income_record.gross_amount = income_record.total_weight_kg * income_record.price_per_kg
        income_record.net_amount = income_record.gross_amount - income_record.harvesting_wage
        
        try:
            db.session.commit()
            flash('บันทึกข้อมูลรายได้เรียบร้อย', 'success')
            return redirect(url_for('income_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    if income_record and request.method == 'GET':
        form.sale_date.data = income_record.sale_date
        form.palm_id.data = income_record.palm_id
        form.total_weight_kg.data = income_record.total_weight_kg
        form.price_per_kg.data = income_record.price_per_kg
        form.harvesting_wage.data = income_record.harvesting_wage
        form.note.data = income_record.note
    
    return render_template('income_form.html', form=form, income_record=income_record)

@app.route('/income/delete/<int:id>')
@login_required
def income_delete(id):
    income_record = db.session.get(HarvestIncome, id)
    if income_record:
        db.session.delete(income_record)
        db.session.commit()
        flash('ลบข้อมูลรายได้เรียบร้อย', 'success')
    else:
        flash('ไม่พบข้อมูลรายได้', 'error')
    return redirect(url_for('income_list'))

@app.route('/income/export')
@login_required
def income_export():
    # Query data with palm codes
    query = db.text("""
        SELECT hi.sale_date, p.code as palm_area, hi.total_weight_kg, 
               hi.price_per_kg, hi.gross_amount, hi.harvesting_wage, 
               hi.net_amount, hi.note
        FROM harvest_income hi
        LEFT JOIN palms p ON hi.palm_id = p.id
        ORDER BY hi.sale_date DESC
    """)
    result = db.session.execute(query)
    rows = result.fetchall()
    
    # Prepare data for CSV
    data = []
    for row in rows:
        data.append([
            row.sale_date or '',
            row.palm_area or 'ไม่ระบุ',
            row.total_weight_kg or 0,
            row.price_per_kg or 0,
            row.gross_amount or 0,
            row.harvesting_wage or 0,
            row.net_amount or 0,
            row.note or ''
        ])
    
    headers = ['วันที่ขาย', 'พื้นที่ปาล์ม', 'น้ำหนักรวม(กก.)', 'ราคา/กก.', 'รายได้รวม', 'ค่าแรงเก็บ', 'รายได้สุทธิ', 'หมายเหตุ']
    return create_csv_response(data, headers, 'harvest_income.csv')

@app.route('/income/import', methods=['POST'])
@login_required
def income_import():
    f = request.files.get('file')
    if not f:
        flash('ไม่พบไฟล์', 'warning')
        return redirect(url_for('income_list'))
    
    required_columns = ['sale_date', 'total_weight_kg', 'price_per_kg']
    data, error = process_csv_file(f, required_columns)
    
    if error:
        flash(error, 'error')
        return redirect(url_for('income_list'))
    
    success_count = 0
    error_count = 0
    
    for row in data:
        try:
            # Find palm by code if provided
            palm_id = None
            if row.get('palm_code'):
                palm = db.session.query(Palm).filter_by(code=row['palm_code']).first()
                if palm:
                    palm_id = palm.id
            
            income_record = HarvestIncome(
                sale_date=datetime.strptime(row['sale_date'], '%Y-%m-%d').date(),
                palm_id=palm_id,
                total_weight_kg=float(row['total_weight_kg']),
                price_per_kg=float(row['price_per_kg']),
                harvesting_wage=float(row.get('harvesting_wage', 0)),
                note=row.get('note', '')
            )
            
            # Calculate amounts
            income_record.gross_amount = income_record.total_weight_kg * income_record.price_per_kg
            income_record.net_amount = income_record.gross_amount - income_record.harvesting_wage
            
            db.session.add(income_record)
            success_count += 1
            
        except Exception as e:
            error_count += 1
            continue
    
    if success_count > 0:
        db.session.commit()
        flash(f'นำเข้าข้อมูลสำเร็จ {success_count} รายการ', 'success')
    
    if error_count > 0:
        flash(f'ข้อมูลที่นำเข้าไม่ได้ {error_count} รายการ', 'warning')
    
    return redirect(url_for('income_list'))

# Fertilizer routes (similar pattern, without pandas)
@app.route('/fertilizer')
@login_required
def fertilizer_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = db.session.query(FertilizerRecord).order_by(FertilizerRecord.date.desc())
    
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            db.or_(
                FertilizerRecord.item.contains(search),
                FertilizerRecord.note.contains(search),
                FertilizerRecord.date.contains(search)
            )
        )
    
    fertilizer_records = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    total_amount = db.session.query(db.func.sum(FertilizerRecord.total_amount)).scalar() or 0
    
    return render_template('fertilizer_list.html', 
                         fertilizer_records=fertilizer_records,
                         total_amount=total_amount,
                         search=search)

# Continue with other routes...
# (Similar pattern for fertilizer, harvest, notes without pandas)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
