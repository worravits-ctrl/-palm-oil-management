
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, login_required, current_user
from sqlalchemy import func, select
from datetime import date
import io, csv
import pandas as pd

from config import Config
from models import db, User, Palm, HarvestIncome, FertilizerRecord, HarvestDetail, Note
from forms import HarvestIncomeForm, FertilizerForm, HarvestDetailForm, NoteForm
from auth import auth_bp
from ai import ai_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp, url_prefix="/ai")

    # ------- Delete Routes -------
    @app.route("/income/delete/<int:id>", methods=["POST"])
    @login_required
    def income_delete(id):
        row = HarvestIncome.query.get_or_404(id)
        db.session.delete(row)
        db.session.commit()
        flash("ลบข้อมูลรายได้เก็บเกี่ยวแล้ว", "success")
        return redirect(url_for("income_list"))

    @app.route("/fertilizer/delete/<int:id>", methods=["POST"])
    @login_required
    def fertilizer_delete(id):
        row = FertilizerRecord.query.get_or_404(id)
        db.session.delete(row)
        db.session.commit()
        flash("ลบข้อมูลใส่ปุ๋ยแล้ว", "success")
        return redirect(url_for("fertilizer_list"))

    @app.route("/harvest/delete/<int:id>", methods=["POST"])
    @login_required
    def harvest_delete(id):
        row = HarvestDetail.query.get_or_404(id)
        db.session.delete(row)
        db.session.commit()
        flash("ลบข้อมูลเก็บเกี่ยวรายต้นแล้ว", "success")
        return redirect(url_for("harvest_list"))

    @app.route("/notes/delete/<int:id>", methods=["POST"])
    @login_required
    def note_delete(id):
        row = Note.query.get_or_404(id)
        db.session.delete(row)
        db.session.commit()
        flash("ลบโน้ตแล้ว", "success")
        return redirect(url_for("notes"))

    @app.route("/")
    def index():
        # Simple dashboard totals
        inc_sum = db.session.scalar(db.select(func.coalesce(func.sum(HarvestIncome.net_amount), 0.0)))
        fert_sum = db.session.scalar(db.select(func.coalesce(func.sum(FertilizerRecord.total_amount), 0.0)))
        bunch_sum = db.session.scalar(db.select(func.coalesce(func.sum(HarvestDetail.bunch_count), 0)))
        return render_template("index.html", inc_sum=inc_sum, fert_sum=fert_sum, bunch_sum=bunch_sum)


    # ------- Harvest Income -------
    @app.route("/income/new", methods=["GET","POST"])
    @login_required
    def income_new():
        form = HarvestIncomeForm()
        if form.validate_on_submit():
            gross = form.total_weight_kg.data * form.price_per_kg.data
            net = gross - form.harvesting_wage.data
            row = HarvestIncome(
                date=form.date.data,
                total_weight_kg=form.total_weight_kg.data,
                price_per_kg=form.price_per_kg.data,
                gross_amount=gross,
                harvesting_wage=form.harvesting_wage.data,
                net_amount=net,
                note=form.note.data or None
            )
            db.session.add(row)
            db.session.commit()
            flash("บันทึกรายได้การเก็บเกี่ยวสำเร็จ", "success")
            return redirect(url_for("income_list"))
        return render_template("income_form.html", form=form)

    @app.route("/income/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def income_edit(id):
        row = HarvestIncome.query.get_or_404(id)
        form = HarvestIncomeForm(obj=row)
        if form.validate_on_submit():
            gross = form.total_weight_kg.data * form.price_per_kg.data
            net = gross - form.harvesting_wage.data
            row.date = form.date.data
            row.total_weight_kg = form.total_weight_kg.data
            row.price_per_kg = form.price_per_kg.data
            row.gross_amount = gross
            row.harvesting_wage = form.harvesting_wage.data
            row.net_amount = net
            row.note = form.note.data or None
            db.session.commit()
            flash("แก้ไขข้อมูลรายได้เก็บเกี่ยวสำเร็จ", "success")
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
        import pandas as pd
        from io import BytesIO
        
        # ใช้ SQLAlchemy connection แทน
        with db.engine.connect() as conn:
            query = "SELECT * FROM harvest_income"
            df = pd.read_sql(query, conn)
        
        # สร้าง CSV ใน memory
        output = BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='harvest_income.csv'
        )

    @app.route("/income/import", methods=["POST"])
    @login_required
    def income_import():
        import pandas as pd
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("income_list"))
        
        try:
            df = pd.read_csv(f)
            count = 0
            for _, r in df.iterrows():
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if pd.isna(r.get("date")) or pd.isna(r.get("total_weight_kg")):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    if isinstance(r["date"], str):
                        # รองรับรูปแบบ d/m/yyyy หรือ dd/mm/yyyy
                        date_val = pd.to_datetime(r["date"], dayfirst=True).date()
                    else:
                        date_val = pd.to_datetime(r["date"]).date()
                except:
                    continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                row = HarvestIncome(
                    date=date_val,
                    total_weight_kg=float(r["total_weight_kg"]),
                    price_per_kg=float(r["price_per_kg"]),
                    gross_amount=float(r["gross_amount"]),
                    harvesting_wage=float(r["harvesting_wage"]),
                    net_amount=float(r["net_amount"]),
                    note=(str(r["note"]) if "note" in r and pd.notna(r["note"]) else None)
                )
                db.session.add(row)
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
            total = form.sacks.data * form.unit_price.data + form.spreading_wage.data
            row = FertilizerRecord(
                date=form.date.data,
                item=form.item.data.strip(),
                sacks=form.sacks.data,
                unit_price=form.unit_price.data,
                spreading_wage=form.spreading_wage.data,
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
        row = FertilizerRecord.query.get_or_404(id)
        form = FertilizerForm(obj=row)
        if form.validate_on_submit():
            total = form.sacks.data * form.unit_price.data + form.spreading_wage.data
            row.date = form.date.data
            row.item = form.item.data.strip()
            row.sacks = form.sacks.data
            row.unit_price = form.unit_price.data
            row.spreading_wage = form.spreading_wage.data
            row.total_amount = total
            row.note = form.note.data or None
            db.session.commit()
            flash("แก้ไขข้อมูลใส่ปุ๋ยสำเร็จ", "success")
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
        import pandas as pd
        from io import BytesIO
        
        # ใช้ SQLAlchemy connection แทน
        with db.engine.connect() as conn:
            query = "SELECT * FROM fertilizer_record"
            df = pd.read_sql(query, conn)
        
        # สร้าง CSV ใน memory
        output = BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='fertilizer_records.csv'
        )

    @app.route("/fertilizer/import", methods=["POST"])
    @login_required
    def fertilizer_import():
        import pandas as pd
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("fertilizer_list"))
        
        try:
            df = pd.read_csv(f)
            count = 0
            for _, r in df.iterrows():
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if pd.isna(r.get("date")) or pd.isna(r.get("item")):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    if isinstance(r["date"], str):
                        date_val = pd.to_datetime(r["date"], dayfirst=True).date()
                    else:
                        date_val = pd.to_datetime(r["date"]).date()
                except:
                    continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                row = FertilizerRecord(
                    date=date_val,
                    item=str(r["item"]),
                    sacks=float(r["sacks"]),
                    unit_price=float(r["unit_price"]),
                    spreading_wage=float(r["spreading_wage"]),
                    total_amount=float(r["total_amount"]),
                    note=(str(r["note"]) if "note" in r and pd.notna(r["note"]) else None)
                )
                db.session.add(row)
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
        # load palm codes into select
        codes = [p.code for p in Palm.query.order_by(Palm.code.asc()).all()]
        form.palm_code.choices = [(c, c) for c in codes]
        if form.validate_on_submit():
            palm = Palm.query.filter_by(code=form.palm_code.data).first()
            row = HarvestDetail(
                date=form.date.data,
                palm_id=palm.id,
                bunch_count=form.bunch_count.data,
                remarks=form.remarks.data or None
            )
            db.session.add(row)
            db.session.commit()
            flash("บันทึกรายการเก็บเกี่ยวรายต้นสำเร็จ", "success")
            return redirect(url_for("harvest_list"))
        return render_template("harvest_form.html", form=form)

    @app.route("/harvest/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def harvest_edit(id):
        row = HarvestDetail.query.get_or_404(id)
        form = HarvestDetailForm(obj=row)
        codes = [p.code for p in Palm.query.order_by(Palm.code.asc()).all()]
        form.palm_code.choices = [(c, c) for c in codes]
        if form.validate_on_submit():
            palm = Palm.query.filter_by(code=form.palm_code.data).first()
            row.date = form.date.data
            row.palm_id = palm.id
            row.bunch_count = form.bunch_count.data
            row.remarks = form.remarks.data or None
            db.session.commit()
            flash("แก้ไขข้อมูลเก็บเกี่ยวรายต้นสำเร็จ", "success")
            return redirect(url_for("harvest_list"))
        # set selected palm_code
        form.palm_code.data = palm.code if (palm := Palm.query.get(row.palm_id)) else None
        return render_template("harvest_form.html", form=form)

    @app.route("/harvest")
    @login_required
    def harvest_list():
        rows = db.session.execute(
            db.select(HarvestDetail.id, HarvestDetail.date, Palm.code, HarvestDetail.bunch_count, HarvestDetail.remarks)
            .join(Palm, Palm.id == HarvestDetail.palm_id)
            .order_by(HarvestDetail.date.desc(), HarvestDetail.id.desc())
        ).all()
        return render_template("harvest_list.html", rows=rows)

    @app.route("/harvest/export")
    @login_required
    def harvest_export():
        import pandas as pd
        from io import BytesIO
        
        # ใช้ SQLAlchemy connection แทน
        with db.engine.connect() as conn:
            query = "SELECT * FROM harvest_detail"
            df = pd.read_sql(query, conn)
        
        # สร้าง CSV ใน memory
        output = BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='harvest_details.csv'
        )

    @app.route("/harvest/import", methods=["POST"])
    @login_required
    def harvest_import():
        import pandas as pd
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("harvest_list"))
        
        try:
            df = pd.read_csv(f)
            count = 0
            errors = []
            for _, r in df.iterrows():
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if pd.isna(r.get("date")) or pd.isna(r.get("palm_code")):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    if isinstance(r["date"], str):
                        date_val = pd.to_datetime(r["date"], dayfirst=True).date()
                    else:
                        date_val = pd.to_datetime(r["date"]).date()
                except:
                    continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                # Find palm by code
                palm = Palm.query.filter_by(code=str(r["palm_code"])).first()
                if not palm:
                    errors.append(f"ไม่พบต้นปาล์มรหัส {r['palm_code']}")
                    continue
                row = HarvestDetail(
                    date=date_val,
                    palm_id=palm.id,
                    bunch_count=int(r["bunch_count"]),
                    remarks=(str(r["remarks"]) if "remarks" in r and pd.notna(r["remarks"]) else None)
                )
                db.session.add(row)
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
            row = Note(date=form.date.data, title=form.title.data.strip(), content=form.content.data.strip())
            db.session.add(row)
            db.session.commit()
            flash("บันทึกโน้ตแล้ว", "success")
            return redirect(url_for("notes"))
        rows = Note.query.order_by(Note.date.desc(), Note.id.desc()).all()
        return render_template("notes.html", form=form, rows=rows)

    @app.route("/notes/edit/<int:id>", methods=["GET", "POST"])
    @login_required
    def note_edit(id):
        row = Note.query.get_or_404(id)
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
        import pandas as pd
        from io import BytesIO
        
        # ใช้ SQLAlchemy connection แทน
        with db.engine.connect() as conn:
            query = "SELECT * FROM note"
            df = pd.read_sql(query, conn)
        
        # สร้าง CSV ใน memory
        output = BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='notes.csv'
        )

    @app.route("/notes/import", methods=["POST"])
    @login_required
    def notes_import():
        import pandas as pd
        f = request.files.get("file")
        if not f:
            flash("ไม่พบไฟล์", "warning")
            return redirect(url_for("notes"))
        
        try:
            df = pd.read_csv(f)
            count = 0
            for _, r in df.iterrows():
                # ข้ามแถวที่ไม่มีข้อมูลสำคัญ
                if pd.isna(r.get("date")) or pd.isna(r.get("title")):
                    continue
                    
                # แปลงวันที่ให้รองรับรูปแบบต่างๆ
                try:
                    if isinstance(r["date"], str):
                        date_val = pd.to_datetime(r["date"], dayfirst=True).date()
                    else:
                        date_val = pd.to_datetime(r["date"]).date()
                except:
                    continue  # ข้ามแถวที่แปลงวันที่ไม่ได้
                
                row = Note(
                    date=date_val,
                    title=str(r["title"]),
                    content=str(r["content"]) if pd.notna(r.get("content")) else ""
                )
                db.session.add(row)
                count += 1
            db.session.commit()
            flash(f"นำเข้าข้อมูลแล้ว {count} รายการ", "success")
        except Exception as e:
            flash(f"เกิดข้อผิดพลาด: {str(e)}", "danger")
        return redirect(url_for("notes"))

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8000)
