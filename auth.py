from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import db, User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("เข้าสู่ระบบสำเร็จ", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")
    return render_template("login.html", form=form)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("มีชื่อผู้ใช้นี้แล้ว", "warning")
        else:
            user = User(username=form.username.data.strip(), email=form.email.data.strip() if form.email.data else None)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ออกจากระบบแล้ว", "info")
    return redirect(url_for("auth.login"))
