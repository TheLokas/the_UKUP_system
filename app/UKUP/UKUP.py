from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Discipline, db, Department, Block, Module, Direction, DirectionDiscipline, Competence, CompetenceDiscipline
from .forms import DisciplineForm, CompetenceForm, CreateConnectionToCompetenceForm
from .functions import add_few_data, get_not_available_comp_numbers_for_type, generate_year
from .module_db import connect_discipline_with_competence, get_connected_competences, delete_connection

UKUP = Blueprint('UKUP', __name__, template_folder='templates', static_folder='static')


@UKUP.route("/discipline", methods=["GET"])
def discipline():
    disciplines = Discipline.query.order_by(Discipline.module_id)
    years = generate_year(2019)[::-1]
    directions = Direction.query.all()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])
    return render_template("Discipline.html", disciplines=disciplines, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route("/competence")
def competence():
    competence = Competence.query.all()
    years = generate_year(2019)[::-1]
    directions = Direction.query.all()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])
    return render_template("Competence.html", competencies=competence, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route("/discipline/add")
def add_discipline():
    year_choices = generate_year(2019)

    # Заменить на функции из модуля бд
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
    return render_template("addDiscipline.html", form=form)


@UKUP.route("/discipline/add", methods=['POST'])
def add_discipline_post():
    form = DisciplineForm(request.form)
    discipline = Discipline(name=form.name.data,
                            year_approved=form.year_approved.data,
                            year_cancelled=None,
                            block_id=form.block.data[0],
                            module_id=form.module.data[0],
                            department_id=form.department.data[0])
    direction_to_discipline_list = []
    if form.direction.data:
        for direction in form.direction.data:
            direction_to_discipline = DirectionDiscipline(discipline_id=discipline.id,
                                                          direction_id=direction,
                                                          year_created=form.year_approved.data,
                                                          year_removed=None)
            direction_to_discipline_list.append(direction_to_discipline)
    try:
        db.session.add(discipline)
        db.session.flush()
        db.session.add_all(direction_to_discipline_list)
        db.session.flush()
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    return redirect("/UKUP/discipline")


@UKUP.route("/competence/add")
def add_competence():
    UK = get_not_available_comp_numbers_for_type("УК")
    OPK = get_not_available_comp_numbers_for_type("ОПК")
    PK = get_not_available_comp_numbers_for_type("ПК")
    year_choices = generate_year(2019)

    form = CompetenceForm()
    form.addData(year=year_choices)
    return render_template("addCompetence.html", form=form, UK=UK, OPK=OPK, PK=PK)


@UKUP.route("/competence/add", methods=["POST"])
def add_competence_to_DB():
    form = CompetenceForm(request.form)
    not_available_numbers = get_not_available_comp_numbers_for_type(form.type.data)
    number = int(str(form.name.data).split("-")[1])
    if number in not_available_numbers:
        flash("Номер компетенции недопустим")
    else:
        competence = Competence(name=form.name.data,
                                year_approved=form.year_approved.data,
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


@UKUP.route('/discipline/<discipline_id>')
def edit_discipline(discipline_id):
    discipline = Discipline.query.get(discipline_id)

    year_approved = generate_year(2019)

    year_cancelled = generate_year(discipline.year_approved)

    # Заменить на функции из модуля бд
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

    form = DisciplineForm(name=discipline.name, year_approved=discipline.year_approved,
                          year_cancelled=discipline.year_cancelled, block=discipline.block_id,
                          module=discipline.module_id,
                          department=discipline.department_id, direction=discipline.direction)
    form.addData(year_approved, block_choices, module_choices, department_choices, direction_choices)
    form.addYearCancelled(year_cancelled)
    return render_template("editDiscipline.html", form=form)


@UKUP.route('/discipline/<discipline_id>', methods=['POST'])
def edit_discipline_post(exam_id):
    form = DisciplineForm(request.form)
    # функция занесения данных в таблицу
    return redirect("/UKUP/discipline")


@UKUP.route('/competence/<competence_id>')
def edit_competence(competence_id):
    UK = get_not_available_comp_numbers_for_type("УК")
    OPK = get_not_available_comp_numbers_for_type("ОПК")
    PK = get_not_available_comp_numbers_for_type("ПК")

    current_year = date.today().year
    # Заменить на функции из модуля бд
    competence = Competence.query.get(competence_id)

    year_approved = generate_year(2019)

    year_cancelled = generate_year(competence.year_approved)

    print(competence.name.split("-")[1])
    print(competence.name)
    form = CompetenceForm(name=competence.name, year_approved=competence.year_approved,
                          year_cancelled=competence.year_cancelled, num=int(competence.name.split("-")[1]),
                          type=competence.type, formulation=competence.formulation)
    form.addData(year_approved)
    form.addYearCancelled(year_cancelled)
    return render_template("editCompetence.html", form=form, UK=UK, OPK=OPK, PK=PK)


@UKUP.route('/competence/<competence_id>', methods=['POST'])
def edit_competence_post(competence_id):
    form = CompetenceForm(request.form)
    # функция занесения данных в таблицу
    return redirect("/UKUP/discipline")


@UKUP.route('/discipline/<discipline_id>/connect', methods=["GET"])
def connect_competences_to_discipline(discipline_id):
    years = generate_year(2019)[::-1]
    directions = Direction.query.all()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    discipline = Discipline.query.get(discipline_id)
    competences = Competence.query.all()

    form = CreateConnectionToCompetenceForm()
    checked = []
    check = CompetenceDiscipline.query.filter_by(discipline_id=discipline_id).all()
    for ch in check:
        checked.append(ch.competence_id)

    return render_template('connectCompetences.html', form=form,
                           competences=competences,
                           discipline=discipline,
                           years=years,
                           directions=directions,
                           current_direction=current_direction,
                           current_year=current_year,
                           checked=checked)


@UKUP.route('/discipline/<discipline_id>/connect', methods=['POST'])
def connect_competences_to_discipline_db(discipline_id):
    checked = request.form.getlist("connect")
    year = request.args["year"]

    already_exist = CompetenceDiscipline.query\
                                        .filter_by(discipline_id=discipline_id)\
                                        .filter_by(year_created=year)\
                                        .all()

    # НЕ ПРОТЕСТИРОВАНО
    for ref in already_exist:
        if ref.competence_id not in checked:
            delete_connection(connection_id=ref.id)

    for check in checked:
        connect_discipline_with_competence(discipline_id=discipline_id,
                                           competence_id=check,
                                           year=year)
    return redirect("/UKUP/discipline")


@UKUP.route("/addData")
def addData():
    return add_few_data()
