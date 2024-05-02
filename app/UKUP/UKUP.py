from datetime import date

from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import db, Block, Direction, Discipline, Module, Department, DirectionDiscipline, Competence
from app.forms import DisciplineForm, CompetenceForm

#disciplines = [Discipline("Линейная алгебра", "Б1.Б", "МА", "Математические и естественнонаучные дисциплины"), Discipline("Матанализ", "Б1.Б", "МА", "Математические и естественнонаучные дисциплины"), Discipline("Дискретная математика", "Б1.Б", "ПМиК", "Модуль 2")]

UKUP = Blueprint('UKUP', __name__, template_folder='templates', static_folder='static')


def add_few_data():
    directions = [
        Direction(name="Информационные системы и технологии", code="09.03.02")
    ]
    modules = [
        Module(name="Гуманитарные и социально-экономические дисциплины"),
        Module(name="Физическая культура и безопасность жизнедеятельности"),
        Module(name="Математические и естественнонаучные дисциплины"),
        Module(name="Программное обеспечение"),
        Module(name="Программирование"),
        Module(name="Информационные технологии"),
        Module(name="Разработка информационных систем")
        ]
    blocks = [
        Block(name="Б1.Б"),
        Block(name="Б1.В.ВД"),
        Block(name="Б1.В.ОД"),
        Block(name="Б2"),
        Block(name="Б2.В"),
        Block(name="Б2.Б"),
        Block(name="Б3.Б"),
        ]
    departments = [
        Department(name="ИМО"),
        Department(name="ПМиК"),
        Department(name="ГиТ"),
        Department(name="МА"),
        Department(name="ТВиАД"),
        Department(name="ТМОМИ")
        ]
    try:
        db.session.add_all(modules)
        db.session.flush()
        db.session.add_all(blocks)
        db.session.flush()
        db.session.add_all(departments)
        db.session.flush()
        db.session.add_all(directions)
        db.session.flush()
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_not_available_comp_numbers_for_type(type: str):
    competence_names = Competence.query.filter(Competence.type == type).with_entities(Competence.name).all()
    numbers = []
    if competence_names is not None:
        for competence_name in competence_names:
            number = int(str(competence_name[0]).split("-")[1])
            numbers.append(number)
        numbers.sort()

    return numbers


@UKUP.route("/discipline")
def discipline():
    return render_template("discipline.html", disciplines=disciplines)


@UKUP.route("/competence")
def competence():
    return render_template("competence.html")


@UKUP.route("/competence/add", methods=["POST"])
def add_competence_to_DB():
    form = CompetenceForm(request.form)
    not_available_numbers = get_not_available_comp_numbers_for_type(form.type.data)
    number = int(str(form.name.data).split("-")[1])
    if number in not_available_numbers:
        flash("Номер компетенции недопустим")
    else:
        competence = Competence(name=form.name.data,
                                year_approved=form.year_approved.data[0],
                                type=form.type.data,
                                year_cancelled=None,
                                formulation=form.formulation.data)
        try:
            db.session.add(competence)
            db.session.flush()
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Произошла ошибка, компетенция не добавлена")
    return redirect("/UKUP/competence")


@UKUP.route("/test")
def test():
    return render_template("competence.html", competencies=competencies)


@UKUP.route("/discipline/add", methods=["POST", "GET"])
def add_discipline():
    current_year = date.today().year
    year_choices = []
    for year in range(2019, current_year + 2):
        year_choices.append((year, year))

    directions = Direction.query.all()
    direction_choices = []
    for direction in directions:
        direction_choices.append((direction.id, direction.name))

    departments = Department.query.all()
    department_choices = []
    for department in departments:
        department_choices.append((department.id, department.name))

    modules = Module.query.all()
    module_choices = []
    for module in modules:
        module_choices.append((module.id, module.name))

    blocks = Block.query.all()
    block_choices = []
    for block in blocks:
        block_choices.append((block.id, block.name))

    form = DisciplineForm()
    form.addData(year=year_choices, block=block_choices,
                module=module_choices, direction=direction_choices,
                department=department_choices)
    
    if request.method == 'POST':
        discipline = Discipline(name=form.name.data,
                                year_approved=form.year_approved.data[0],
                                year_cancelled=None,
                                block_id=form.block.data[0],
                                module_id=form.module.data[0],
                                department=form.department.data[0])
        direction_to_discipline_list = []
        if form.direction.data:
            for direction in form.direction.data:
                direction_to_discipline = DirectionDiscipline(discipline_id=discipline.id,
                                                              direction_id=direction,
                                                              year_created=form.year_approved.data[0],
                                                              year_removed=None)
                direction_to_discipline_list.append(direction_to_discipline)
        try:
            db.session.add(discipline)
            db.session.flush()
            db.session.add_all(direction_to_discipline_list)
            db.session.flush()
            db.session.commit()
        except Exception:
            db.session.rollback()
    return render_template("disciplineAdd.html", form=form)