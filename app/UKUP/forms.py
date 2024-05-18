from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SelectField, EmailField, PasswordField, Field, SelectMultipleField, TextAreaField, SubmitField, HiddenField, widgets
from wtforms.validators import input_required, data_required, ValidationError, Length


class DisciplineForm(FlaskForm):
    name = StringField()
    year_approved = SelectField()
    year_cancelled = SelectField()
    block = SelectField()
    module = SelectField()
    department = SelectField()
    direction = SelectMultipleField()
    submit = SubmitField()

    def addData(self, year, block, module, department, direction):
        self.year_approved.choices = year
        self.block.choices = block
        self.module.choices = module
        self.department.choices = department
        self.direction.choices = direction

    def addYearCancelled(self, year):
        NoneArray = ["-"]
        self.year_cancelled.choices = NoneArray + year


class CompetenceForm(FlaskForm):
    name = StringField()
    num = IntegerField()
    year_cancelled = SelectField()
    year_approved = SelectField()
    type = SelectField(choices=["УК", "ОПК", "ПК"])
    formulation = TextAreaField()
    submit = SubmitField()

    def addData(self, year):
        self.year_approved.choices = year

    def addYearCancelled(self, year):
        NoneArray = ["-"]
        self.year_cancelled.choices = NoneArray + year

class CompetenceConnectForm(FlaskForm):
    connect = BooleanField()
    hidden = HiddenField()
    submit = SubmitField()
