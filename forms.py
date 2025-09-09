from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Optional

class LoginForm(FlaskForm):
    username = StringField("ชื่อผู้ใช้", validators=[DataRequired()])
    password = PasswordField("รหัสผ่าน", validators=[DataRequired()])
    submit = SubmitField("เข้าสู่ระบบ")

class RegisterForm(FlaskForm):
    username = StringField("ชื่อผู้ใช้", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("อีเมล (ไม่บังคับ)", validators=[Optional(), Email()])
    password = PasswordField("รหัสผ่าน", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("ยืนยันรหัสผ่าน", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("สมัครสมาชิก")

from datetime import date

class HarvestIncomeForm(FlaskForm):
    date = DateField("วันที่ขายปาล์ม", validators=[DataRequired()], default=date.today)
    total_weight_kg = FloatField("น้ำหนักรวม (กก.)", validators=[DataRequired(), NumberRange(min=0)])
    price_per_kg = FloatField("ราคาต่อกก. (บาท)", validators=[DataRequired(), NumberRange(min=0)])
    gross_amount = FloatField("ยอดรวม (บาท)", validators=[DataRequired(), NumberRange(min=0)])
    harvesting_wage = FloatField("ค่าจ้างเก็บเกี่ยว (บาท)", validators=[DataRequired(), NumberRange(min=0)])
    note = TextAreaField("หมายเหตุ", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("บันทึก")

class FertilizerForm(FlaskForm):
    date = DateField("วัน/เดือน/ปี", validators=[DataRequired()], default=date.today)
    item = StringField("รายการ", validators=[DataRequired(), Length(max=255)])
    sacks = FloatField("จำนวน (กระสอบ)", validators=[DataRequired(), NumberRange(min=0)])
    unit_price = FloatField("หน่วยละ (บาท)", validators=[DataRequired(), NumberRange(min=0)])
    spreading_wage = FloatField("ค่าจ้างหว่านปุ๋ย (บาท)", validators=[Optional(), NumberRange(min=0)], default=0)
    note = TextAreaField("หมายเหตุ", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("บันทึก")

class HarvestDetailForm(FlaskForm):
    date = DateField("วัน/เดือน/ปี", validators=[DataRequired()], default=date.today)
    palm_code = StringField("รหัสต้นปาล์ม", validators=[DataRequired(), Length(max=10)])
    bunch_count = IntegerField("จำนวนทะลาย", validators=[DataRequired(), NumberRange(min=0)])
    remarks = TextAreaField("หมายเหตุ", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("บันทึก")

class NoteForm(FlaskForm):
    date = DateField("วัน/เดือน/ปี", validators=[DataRequired()], default=date.today)
    title = StringField("หัวข้อ", validators=[DataRequired(), Length(max=255)])
    content = TextAreaField("รายละเอียด", validators=[DataRequired()])
    submit = SubmitField("บันทึก")
