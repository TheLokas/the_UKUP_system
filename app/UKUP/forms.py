from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SelectField, EmailField, PasswordField, Field, SelectMultipleField, TextAreaField, SubmitField, HiddenField, widgets, FieldList, FormField
from wtforms.validators import input_required, data_required, ValidationError, Length


class DisciplineForm(FlaskForm):
    name = StringField()
    year_approved = SelectField()
    year_cancelled = SelectField()
    block = SelectField()
    module = SelectField()
    department = SelectField()
    direction = SelectField()
    required = SelectField()
    submit = SubmitField("Добавить")

    def addData(self, year, block, module, department, direction, required_discipines):
        self.year_approved.choices = year
        self.block.choices = block
        self.module.choices = module
        self.department.choices = department
        self.direction.choices = direction
        self.required.choices = required_discipines

    #def addRequiredDisciplines(self, )

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
    source = TextAreaField()
    direction = SelectField()
    submit = SubmitField("Добавить")

    def addYear(self, year):
        self.year_approved.choices = year

    def addDirection(self, direction):
        self.direction.choices = direction


class ConnectForm(FlaskForm):
    connect = BooleanField()
    hidden = HiddenField()
    submit = SubmitField()

class ZEForm(FlaskForm):
    num = IntegerField()
    id_discipline= IntegerField()
    c = IntegerField()
    submit = SubmitField()

#class zeDiscipline(FlaskForm):
#    id = IntegerField()
#    ze = FieldList(FormField(ze), min_entries=8)

#class ZEForm(FlaskForm):
#    dis = FieldList(FormField(zeDiscipline))
#    submit = SubmitField()
#class ze(FlaskForm):
#    num = IntegerField()
#    id_discipline= IntegerField()
#    c = IntegerField()

#class ZEForm(FlaskForm):
#    ze = FieldList(FormField(ze))
#    submit = SubmitField()