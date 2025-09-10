from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, HarvestIncome, FertilizerRecord, HarvestDetail, Note, Palm
from forms import LoginForm, RegisterForm, HarvestIncomeForm, FertilizerForm, HarvestDetailForm, NoteForm
from auth import auth_bp
from ai import ai_bp
from datetime import date, datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///palm_farm.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-google-api-key-here')
    
    # Initialize database
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Create palm trees if they don't exist
        if db.session.query(Palm).count() == 0:
            # สร้างต้นปาล์ม A1-L26
            rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
            for row in rows:
                for col in range(1, 27):  # 1-26
                    code = f"{row}{col}"
                    palm = Palm(code=code)
                    db.session.add(palm)
            
            try:
                db.session.commit()
                print(f"Created {len(rows) * 26} palm trees")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating palm trees: {e}")
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = 'กรุณาเข้าสู่ระบบก่อนใช้งาน'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register error handlers
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return f"<h1>Internal Server Error</h1><p>กรุณาลองใหม่อีกครั้ง หรือติดต่อผู้ดูแลระบบ</p><p>Error: {str(error)}</p>", 500
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    
    # Basic routes
    @app.route('/')
    def index():
        try:
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Get summary statistics
            total_income = db.session.query(db.func.sum(HarvestIncome.net_amount)).scalar() or 0
            total_fertilizer_cost = db.session.query(db.func.sum(FertilizerRecord.total_amount)).scalar() or 0
            total_harvest_count = db.session.query(db.func.sum(HarvestDetail.bunch_count)).scalar() or 0
            total_palms = db.session.query(Palm).count()
            
            # Get recent activities (limit to prevent timeout)
            recent_income = db.session.query(HarvestIncome).order_by(HarvestIncome.date.desc()).limit(3).all()
            recent_fertilizer = db.session.query(FertilizerRecord).order_by(FertilizerRecord.date.desc()).limit(3).all()
            recent_harvest = db.session.query(HarvestDetail).join(Palm).order_by(HarvestDetail.date.desc()).limit(3).all()
            recent_notes = db.session.query(Note).order_by(Note.date.desc()).limit(3).all()
            
            return render_template('index.html',
                                 total_income=total_income,
                                 total_fertilizer_cost=total_fertilizer_cost,
                                 total_harvest_count=total_harvest_count,
                                 total_palms=total_palms,
                                 recent_income=recent_income,
                                 recent_fertilizer=recent_fertilizer,
                                 recent_harvest=recent_harvest,
                                 recent_notes=recent_notes)
        except Exception as e:
            return f"<h1>Database Error</h1><p>ปัญหา: {str(e)}</p><p>กรุณารอสักครู่แล้วลองใหม่</p>", 500
    
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Palm Oil Management System is running!'}
    
    # Delete routes
    @app.route("/income/delete/<int:id>", methods=["POST"])
    @login_required
    def income_delete(id):
        row = db.session.get(HarvestIncome, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการลบ", "danger")
            return redirect(url_for("income_list"))
        db.session.delete(row)
        db.session.commit()
        flash("ลบรายการสำเร็จ", "success")
        return redirect(url_for("income_list"))

    @app.route("/fertilizer/delete/<int:id>", methods=["POST"])
    @login_required
    def fertilizer_delete(id):
        row = db.session.get(FertilizerRecord, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการลบ", "danger")
            return redirect(url_for("fertilizer_list"))
        db.session.delete(row)
        db.session.commit()
        flash("ลบรายการสำเร็จ", "success")
        return redirect(url_for("fertilizer_list"))

    @app.route("/harvest/delete/<int:id>", methods=["POST"])
    @login_required
    def harvest_delete(id):
        row = db.session.get(HarvestDetail, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการลบ", "danger")
            return redirect(url_for("harvest_list"))
        db.session.delete(row)
        db.session.commit()
        flash("ลบรายการสำเร็จ", "success")
        return redirect(url_for("harvest_list"))

    @app.route("/notes/delete/<int:id>", methods=["POST"])
    @login_required
    def note_delete(id):
        row = db.session.get(Note, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการลบ", "danger")
            return redirect(url_for("notes"))
        db.session.delete(row)
        db.session.commit()
        flash("ลบรายการสำเร็จ", "success")
        return redirect(url_for("notes"))

    # ------- Income Routes -------
    @app.route("/income/new", methods=["GET", "POST"])
    @login_required
    def income_new():
        form = HarvestIncomeForm()
        form.date.data = date.today()  # Set default date
        
        if form.validate_on_submit():
            # Calculate net amount automatically
            net = form.gross_amount.data - form.harvesting_wage.data
            
            row = HarvestIncome(
                date=form.date.data,
                total_weight_kg=form.total_weight_kg.data,
                price_per_kg=form.price_per_kg.data,
                gross_amount=form.gross_amount.data,
                harvesting_wage=form.harvesting_wage.data,
                net_amount=net,
                note=form.note.data or None
            )
            db.session.add(row)
            db.session.commit()
            flash("บันทึกรายได้สำเร็จ", "success")
            return redirect(url_for("income_list"))
        return render_template("income_form.html", form=form)

    @app.route("/income/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def income_edit(id):
        row = db.session.get(HarvestIncome, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการแก้ไข", "danger")
            return redirect(url_for("income_list"))
        form = HarvestIncomeForm(obj=row)
        if form.validate_on_submit():
            # Calculate net amount automatically
            net = form.gross_amount.data - form.harvesting_wage.data
            
            row.date = form.date.data
            row.total_weight_kg = form.total_weight_kg.data
            row.price_per_kg = form.price_per_kg.data
            row.gross_amount = form.gross_amount.data
            row.harvesting_wage = form.harvesting_wage.data
            row.net_amount = net
            row.note = form.note.data or None
            db.session.commit()
            flash("แก้ไขรายการสำเร็จ", "success")
            return redirect(url_for("income_list"))
        return render_template("income_form.html", form=form)

    @app.route("/income")
    @login_required
    def income_list():
        rows = HarvestIncome.query.order_by(HarvestIncome.date.desc(), HarvestIncome.id.desc()).all()
        return render_template("income_list.html", rows=rows)

    @app.route("/income/export")
    @login_required
    def income_export():
        import csv
        from io import StringIO
        
        # Query ข้อมูลรายได้พร้อม palm code
        query = db.text("""
            SELECT hi.date, p.code as palm_area, hi.total_weight_kg, 
                   hi.price_per_kg, hi.gross_amount, hi.harvesting_wage, 
                   hi.net_amount, hi.note
            FROM harvest_income hi
            LEFT JOIN palms p ON hi.palm_id = p.id
            ORDER BY hi.date DESC
        """)
        result = db.session.execute(query)
        rows = result.fetchall()
        
        # สร้าง CSV ในหน่วยความจำ
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Date', 'Palm Area', 'Total Weight (kg)', 'Price per kg', 'Gross Amount', 'Harvesting Wage', 'Net Amount', 'Note'])
        
        # Data rows
        for row in rows:
            writer.writerow([
                row.date.strftime('%Y-%m-%d') if row.date else '',
                row.palm_area or 'Not specified',
                row.total_weight_kg or 0,
                row.price_per_kg or 0,
                row.gross_amount or 0,
                row.harvesting_wage or 0,
                row.net_amount or 0,
                row.note or ''
            ])
        
        # แปลงเป็น bytes สำหรับ send_file
        from io import BytesIO
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return send_file(
            output_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='harvest_income.csv'
        )

    @app.route("/income/import", methods=["POST"])
    @login_required
    def income_import():
        import csv
        from io import StringIO
        
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("income_list"))
        
        try:
            # อ่านไฟล์ CSV
            stream = StringIO(f.stream.read().decode("utf8"))
            reader = csv.DictReader(stream)
            
            count = 0
            for row in reader:
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if not row.get("date") or not row.get("total_weight_kg"):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    date_val = datetime.strptime(row["date"], '%d/%m/%Y').date()
                except:
                    try:
                        date_val = datetime.strptime(row["date"], '%Y-%m-%d').date()
                    except:
                        continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                income_row = HarvestIncome(
                    date=date_val,
                    total_weight_kg=float(row["total_weight_kg"]),
                    price_per_kg=float(row["price_per_kg"]),
                    gross_amount=float(row["gross_amount"]),
                    harvesting_wage=float(row["harvesting_wage"]),
                    net_amount=float(row["net_amount"]),
                    note=(row["note"] if row.get("note") else None)
                )
                db.session.add(income_row)
                count += 1
            db.session.commit()
            flash(f"นำเข้าข้อมูลแล้ว {count} รายการ", "success")
        except Exception as e:
            flash(f"เกิดข้อผิดพลาด: {str(e)}", "danger")
        return redirect(url_for("income_list"))

    # ------- Fertilizer -------
    @app.route("/fertilizer/new", methods=["GET","POST"])
    @login_required
    def fertilizer_new():
        form = FertilizerForm()
        if form.validate_on_submit():
            spreading_wage = form.spreading_wage.data or 0
            total = form.sacks.data * form.unit_price.data + spreading_wage
            row = FertilizerRecord(
                date=form.date.data,
                item=form.item.data.strip(),
                sacks=form.sacks.data,
                unit_price=form.unit_price.data,
                spreading_wage=spreading_wage,
                total_amount=total,
                note=form.note.data or None
            )
            db.session.add(row)
            db.session.commit()
            flash("บันทึกรายการปุ๋ยสำเร็จ", "success")
            return redirect(url_for("fertilizer_list"))
        return render_template("fertilizer_form.html", form=form)

    @app.route("/fertilizer/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def fertilizer_edit(id):
        row = db.session.get(FertilizerRecord, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการแก้ไข", "danger")
            return redirect(url_for("fertilizer_list"))
        form = FertilizerForm(obj=row)
        if form.validate_on_submit():
            spreading_wage = form.spreading_wage.data or 0
            total = form.sacks.data * form.unit_price.data + spreading_wage
            row.date = form.date.data
            row.item = form.item.data.strip()
            row.sacks = form.sacks.data
            row.unit_price = form.unit_price.data
            row.spreading_wage = spreading_wage
            row.total_amount = total
            row.note = form.note.data or None
            db.session.commit()
            flash("แก้ไขรายการปุ๋ยสำเร็จ", "success")
            return redirect(url_for("fertilizer_list"))
        return render_template("fertilizer_form.html", form=form)

    @app.route("/fertilizer")
    @login_required
    def fertilizer_list():
        rows = FertilizerRecord.query.order_by(FertilizerRecord.date.desc(), FertilizerRecord.id.desc()).all()
        return render_template("fertilizer_list.html", rows=rows)

    @app.route("/fertilizer/export")
    @login_required
    def fertilizer_export():
        import csv
        from io import StringIO
        
        # ดึงข้อมูลจากฐานข้อมูล
        rows = FertilizerRecord.query.order_by(FertilizerRecord.date.desc()).all()
        
        # สร้าง CSV ใน memory
        output = StringIO()
        writer = csv.writer(output)
        
        # เขียน header
        writer.writerow(['ID', 'Date', 'Type', 'Amount', 'Cost', 'Notes'])
        
        # เขียนข้อมูล
        for row in rows:
            writer.writerow([
                row.id,
                row.date.strftime('%Y-%m-%d'),
                row.fertilizer_type,
                row.amount,
                row.cost,
                row.notes or ''
            ])
        
        # แปลงเป็น bytes สำหรับ send_file
        from io import BytesIO
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return send_file(
            output_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='fertilizer_records.csv'
        )

    @app.route("/fertilizer/import", methods=["POST"])
    @login_required
    def fertilizer_import():
        import csv
        from io import StringIO
        
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("fertilizer_list"))
        
        try:
            # อ่านไฟล์ CSV
            stream = StringIO(f.stream.read().decode("utf8"))
            reader = csv.DictReader(stream)
            
            count = 0
            for row in reader:
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if not row.get("date") or not row.get("item"):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    if isinstance(row["date"], str):
                        date_val = datetime.strptime(row["date"], '%Y-%m-%d').date()
                    else:
                        date_val = row["date"]
                except:
                    continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                fertilizer = FertilizerRecord(
                    date=date_val,
                    fertilizer_type=str(row["item"]),
                    amount=float(row.get("sacks", 0)),
                    cost=float(row.get("unit_price", 0)),
                    notes=str(row.get("note", "")).strip() if row.get("note") else None
                )
                db.session.add(fertilizer)
                count += 1
            db.session.commit()
            flash(f"นำเข้าข้อมูลแล้ว {count} รายการ", "success")
        except Exception as e:
            flash(f"เกิดข้อผิดพลาด: {str(e)}", "danger")
        return redirect(url_for("fertilizer_list"))

    # ------- Harvest Detail (per tree) -------
    @app.route("/harvest/new", methods=["GET","POST"])
    @login_required
    def harvest_new():
        form = HarvestDetailForm()
        # ดึงข้อมูลต้นปาล์มทั้งหมดเรียงตามรหัส
        palms = Palm.query.order_by(Palm.code).all()
        
        if form.validate_on_submit():
            # Find the palm by code
            palm = Palm.query.filter_by(code=form.palm_code.data).first()
            if not palm:
                flash(f"ไม่พบต้นปาล์มรหัส {form.palm_code.data}", "danger")
                return render_template("harvest_form.html", form=form, palms=palms)
            
            row = HarvestDetail(
                date=form.date.data,
                palm_id=palm.id,
                bunch_count=form.bunch_count.data,
                remarks=form.remarks.data or None
            )
            db.session.add(row)
            db.session.commit()
            flash("บันทึกการเก็บเกี่ยวสำเร็จ", "success")
            return redirect(url_for("harvest_list"))
        return render_template("harvest_form.html", form=form, palms=palms)

    @app.route("/harvest/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def harvest_edit(id):
        row = db.session.get(HarvestDetail, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการแก้ไข", "danger")
            return redirect(url_for("harvest_list"))
        form = HarvestDetailForm(obj=row)
        # ดึงข้อมูลต้นปาล์มทั้งหมดเรียงตามรหัส
        palms = Palm.query.order_by(Palm.code).all()
        # Set the palm_code field from the related palm
        form.palm_code.data = row.palm.code
        
        if form.validate_on_submit():
            # Find the palm by code
            palm = Palm.query.filter_by(code=form.palm_code.data).first()
            if not palm:
                flash(f"ไม่พบต้นปาล์มรหัส {form.palm_code.data}", "danger")
                return render_template("harvest_form.html", form=form, palms=palms)
            
            row.date = form.date.data
            row.palm_id = palm.id
            row.bunch_count = form.bunch_count.data
            row.remarks = form.remarks.data or None
            db.session.commit()
            flash("แก้ไขการเก็บเกี่ยวสำเร็จ", "success")
            return redirect(url_for("harvest_list"))
        return render_template("harvest_form.html", form=form, palms=palms)

    @app.route("/harvest")
    @login_required
    def harvest_list():
        # Join with Palm to get palm code และแยกข้อมูลให้ตรงกับ template
        rows = []
        results = db.session.execute(
            db.select(HarvestDetail, Palm.code).join(Palm).order_by(HarvestDetail.date.desc(), HarvestDetail.id.desc())
        ).all()
        
        for harvest_detail, palm_code in results:
            rows.append((
                harvest_detail.id,
                harvest_detail.date,
                palm_code,
                harvest_detail.bunch_count,
                harvest_detail.remarks
            ))
        
        return render_template("harvest_list.html", rows=rows)

    @app.route("/harvest/export")
    @login_required
    def harvest_export():
        import csv
        from io import StringIO
        
        # ดึงข้อมูลจากฐานข้อมูล พร้อม JOIN เพื่อได้รหัสต้นปาล์ม
        query = db.session.query(
            HarvestDetail.id,
            HarvestDetail.date,
            Palm.code.label('palm_code'),
            HarvestDetail.bunch_count,
            HarvestDetail.remarks
        ).join(Palm, HarvestDetail.palm_id == Palm.id)\
         .order_by(HarvestDetail.date.desc(), Palm.code)
        
        rows = query.all()
        
        # สร้าง CSV ใน memory
        output = StringIO()
        writer = csv.writer(output)
        
        # เขียน header
        writer.writerow(['ID', 'Date', 'Palm Code', 'Bunch Count', 'Remarks'])
        
        # เขียนข้อมูล
        for row in rows:
            writer.writerow([
                row.id,
                row.date.strftime('%Y-%m-%d'),
                row.palm_code,
                row.bunch_count,
                row.remarks or ''
            ])
        
        # แปลงเป็น bytes สำหรับ send_file
        from io import BytesIO
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return send_file(
            output_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='harvest_details.csv'
        )

    @app.route("/harvest/import", methods=["POST"])
    @login_required
    def harvest_import():
        import csv
        from io import StringIO
        
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("harvest_list"))
        
        try:
            # อ่านไฟล์ CSV
            stream = StringIO(f.stream.read().decode("utf8"))
            reader = csv.DictReader(stream)
            
            count = 0
            errors = []
            for row in reader:
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if not row.get("date") or not row.get("palm_code"):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    if isinstance(row["date"], str):
                        date_val = datetime.strptime(row["date"], '%Y-%m-%d').date()
                    else:
                        date_val = row["date"]
                except:
                    continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                # Find palm by code
                palm = Palm.query.filter_by(code=str(row["palm_code"])).first()
                if not palm:
                    errors.append(f"ไม่พบต้นปาล์มรหัส {row['palm_code']}")
                    continue
                
                harvest = HarvestDetail(
                    date=date_val,
                    palm_id=palm.id,
                    bunch_count=int(row.get("bunch_count", 0)),
                    remarks=str(row.get("remarks", "")).strip() if row.get("remarks") else None
                )
                db.session.add(harvest)
                count += 1
            db.session.commit()
            
            if errors:
                flash(f"นำเข้าข้อมูลแล้ว {count} รายการ แต่มีข้อผิดพลาด: {', '.join(errors[:3])}", "warning")
            else:
                flash(f"นำเข้าข้อมูลแล้ว {count} รายการ", "success")
        except Exception as e:
            flash(f"เกิดข้อผิดพลาด: {str(e)}", "danger")
        return redirect(url_for("harvest_list"))

    # ------- Notes -------
    @app.route("/notes", methods=["GET","POST"])
    @login_required
    def notes():
        form = NoteForm()
        if form.validate_on_submit():
            row = Note(
                date=form.date.data,
                title=form.title.data.strip(),
                content=form.content.data.strip()
            )
            db.session.add(row)
            db.session.commit()
            flash("บันทึกโน้ตสำเร็จ", "success")
            return redirect(url_for("notes"))
        rows = Note.query.order_by(Note.date.desc(), Note.id.desc()).all()
        return render_template("notes.html", form=form, rows=rows)

    @app.route("/notes/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def note_edit(id):
        row = db.session.get(Note, id)
        if not row:
            flash("ไม่พบรายการที่ต้องการแก้ไข", "danger")
            return redirect(url_for("notes"))
        form = NoteForm(obj=row)
        if form.validate_on_submit():
            row.date = form.date.data
            row.title = form.title.data.strip()
            row.content = form.content.data.strip()
            db.session.commit()
            flash("แก้ไขโน้ตสำเร็จ", "success")
            return redirect(url_for("notes"))
        # แสดงฟอร์มแก้ไขแยกจากฟอร์มเพิ่ม
        rows = Note.query.order_by(Note.date.desc(), Note.id.desc()).all()
        return render_template("notes.html", form=form, rows=rows)

    @app.route("/notes/export")
    @login_required
    def notes_export():
        import csv
        from io import StringIO
        
        # ดึงข้อมูลจากฐานข้อมูล
        rows = Note.query.order_by(Note.date.desc()).all()
        
        # สร้าง CSV ใน memory
        output = StringIO()
        writer = csv.writer(output)
        
        # เขียน header
        writer.writerow(['ID', 'Date', 'Title', 'Content'])
        
        # เขียนข้อมูล
        for row in rows:
            writer.writerow([
                row.id,
                row.date.strftime('%Y-%m-%d'),
                row.title,
                row.content or ''
            ])
        
        # แปลงเป็น bytes สำหรับ send_file
        from io import BytesIO
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return send_file(
            output_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='notes.csv'
        )

    @app.route("/notes/import", methods=["POST"])
    @login_required
    def notes_import():
        import csv
        from io import StringIO
        
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("notes"))
        
        try:
            # อ่านไฟล์ CSV
            stream = StringIO(f.stream.read().decode("utf8"))
            reader = csv.DictReader(stream)
            
            count = 0
            for row in reader:
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if not row.get("date") or not row.get("title"):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    if isinstance(row["date"], str):
                        date_val = datetime.strptime(row["date"], '%Y-%m-%d').date()
                    else:
                        date_val = row["date"]
                except:
                    continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                note = Note(
                    date=date_val,
                    title=str(row["title"]),
                    content=str(row.get("content", "")).strip() if row.get("content") else ""
                )
                db.session.add(note)
                count += 1
            db.session.commit()
            flash(f"นำเข้าข้อมูลแล้ว {count} รายการ", "success")
        except Exception as e:
            flash(f"เกิดข้อผิดพลาด: {str(e)}", "danger")
        return redirect(url_for("notes"))

    return app

# Create application instance for production deployment
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # For production deployment (Render, Heroku, etc.)
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, host="0.0.0.0", port=port)
