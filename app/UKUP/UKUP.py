from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Discipline, db, Department, Block, Module, Direction, DirectionDiscipline, Competence, CompetenceDiscipline
from .forms import DisciplineForm, CompetenceForm, CompetenceConnectForm
from .functions import add_few_data, get_not_available_comp_numbers_for_type, generate_year
from .module_db import connect_discipline_with_competence
from .moduleDB import get_disciplines, get_competences, add_discipline, add_competence, get_modules, get_block, get_directions, get_departments, edit_discipline, edit_competence, get_connected_competences
from .moduleDB import report_matrix


UKUP = Blueprint('UKUP', __name__, template_folder='templates', static_folder='static')

@UKUP.route("/matrix", methods=["GET"])
def matrix():
    years = generate_year(2019)[::-1]
    directions = Direction.query.all()
    current_direction = directions[0] if directions else None
    current_year = date.today().year

    if request.args.get("year") and request.args.get("direction"):
        current_year = int(request.args["year"])
        current_direction = Direction.query.get(int(request.args["direction"]))

    if current_direction:
        disciplines = [
            discipline
            for direction_discipline in current_direction.disciplines
            if direction_discipline.year_created <= current_year
            and (direction_discipline.year_removed is None or direction_discipline.year_removed > current_year)
            for discipline in [direction_discipline.discipline]
            if discipline is not None
        ]

        competence_set = set()
        for discipline in disciplines:
            if discipline is not None:
                for competence_discipline in discipline.competence_disciplines:
                    if competence_discipline.year_created <= current_year and (
                        competence_discipline.year_removed is None or competence_discipline.year_removed > current_year
                    ):
                        competence_set.add(competence_discipline.competence)

        competences = list(competence_set)

        discipline_competence_links = [
            (discipline, competence)
            for discipline in disciplines
            if discipline is not None
            for competence_discipline in discipline.competence_disciplines
            if competence_discipline.year_created <= current_year
            and (competence_discipline.year_removed is None or competence_discipline.year_removed > current_year)
            for competence in [competence_discipline.competence]
        ]

        competence_types = {competence.id: competence.type for competence in competences}
    else:
        disciplines = []
        competences = []
        discipline_competence_links = []
        competence_types = {}

    return render_template(
        "Matrix.html",
        competences=competences,
        disciplines=disciplines,
        years=years,
        directions=directions,
        current_year=current_year,
        current_direction=current_direction,
        competence_discipline_map=discipline_competence_links,
        competence_types=competence_types,
    )


@UKUP.route("/discipline", methods=["GET"])
def discipline():
    type = "discipline"
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])

    disciplines = get_disciplines(direction=current_direction, year=current_year)
    return render_template("Discipline.html", type=type, disciplines=disciplines, years=years, directions=directions, current_year=current_year, current_direction=current_direction)



@UKUP.route("/competence", methods=['GET'])
def competence():
    type = "competence"
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])
    competence = get_competences(direction=current_direction, year=current_year)
    print(competence)

    return render_template("Competence.html", type=type, competencies=competence, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route("/discipline/add", methods=['GET'])
def add_discipline_page():
    type = "discipline"
    year_choices = generate_year(2019)

    # Заменить на функции из модуля бд
    directions = get_directions()
    direction_choices = []
    for direction in directions:
        direction_choices.append((direction.id, direction.name))

    departments = get_departments()
    department_choices = []
    for department in departments:
        department_choices.append((department.id, department.name))

    modules = get_modules()
    module_choices = []
    for module in modules:
        module_choices.append((module.id, module.name))

    blocks = get_block()
    block_choices = []
    for block in blocks:
        block_choices.append((block.id, block.name))

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])

    form = DisciplineForm(year_approved=current_year, direction=(current_direction.id, current_direction.name))
    form.addData(year=year_choices, block=block_choices,
                 module=module_choices, direction=direction_choices,
                 department=department_choices)
    return render_template("addDiscipline.html",type=type, form=form, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route("/discipline/add", methods=['POST'])
def add_discipline_post():
    form = DisciplineForm(request.form)
    add_discipline([form.name.data, form.year_approved.data, form.block.data, form.module.data, form.department.data], form.direction.data)
    return redirect("/UKUP/discipline")


@UKUP.route("/competence/add")
def add_competence_page():
    type = "competence"
    UK = get_not_available_comp_numbers_for_type("УК")
    OPK = get_not_available_comp_numbers_for_type("ОПК")
    PK = get_not_available_comp_numbers_for_type("ПК")
    year_choices = generate_year(2019)

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    form = CompetenceForm(year_approved=current_year)
    form.addData(year=year_choices)
    return render_template("addCompetence.html", type=type, form=form, UK=UK, OPK=OPK, PK=PK, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route("/competence/add", methods=["POST"])
def add_competence_post():
    form = CompetenceForm(request.form)
    not_available_numbers = get_not_available_comp_numbers_for_type(form.type.data)
    number = int(str(form.name.data).split("-")[1])
    if number in not_available_numbers:
        flash("Номер компетенции недопустим")
    else:
        add_competence([form.name.data, form.year_approved.data, form.type.data, form.formulation.data])
    return redirect("/UKUP/competence")


@UKUP.route('/discipline/<discipline_id>', methods=['GET'])
def edit_discipline_page(discipline_id):
    type = "discipline"

    # Необходима функция
    discipline = Discipline.query.get(discipline_id)

    year_approved = generate_year(2019)

    year_cancelled = generate_year(discipline.year_approved)

    directions = get_directions()
    direction_choices = []
    for direction in directions:
        direction_choices.append((direction.id, direction.name))

    departments = get_departments()
    department_choices = []
    for department in departments:
        department_choices.append((department.id, department.name))

    modules = get_modules()
    module_choices = []
    for module in modules:
        module_choices.append((module.id, module.name))

    blocks = get_block()
    block_choices = []
    for block in blocks:
        block_choices.append((block.id, block.name))


    form = DisciplineForm(name=discipline.name, year_approved=discipline.year_approved,
                          year_cancelled=discipline.year_cancelled, block=discipline.block_id,
                          module=discipline.module_id,
                          department=discipline.department_id, direction=discipline.direction)
    form.addData(year_approved, block_choices, module_choices, department_choices, direction_choices)
    form.addYearCancelled(year_cancelled)

    years = generate_year(2019)[::-1]
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])

    return render_template("editDiscipline.html", type=type, form=form, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route('/discipline/<discipline_id>', methods=['POST'])
def edit_discipline_post(discipline_id):
    form = DisciplineForm(request.form)
    #print(request.form)
    edit_discipline(discipline_id, [form.name.data, "1970", form.block.data, form.module.data, form.department.data], form.direction.data, request.form.get("current_year"))
    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route('/competence/<competence_id>')
def edit_competence_page(competence_id):
    type = "competence"
    UK = get_not_available_comp_numbers_for_type("УК")
    OPK = get_not_available_comp_numbers_for_type("ОПК")
    PK = get_not_available_comp_numbers_for_type("ПК")

    # Необходима функция
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

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])

    return render_template("editCompetence.html", type=type, form=form, UK=UK, OPK=OPK, PK=PK, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route('/competence/<competence_id>', methods=['POST'])
def edit_competence_post(competence_id):
    form = CompetenceForm(request.form)
    print(request.form)
    edit_competence(competence_id, [form.name.data, form.type.data, form.formulation.data])
    return redirect(f"/UKUP/competence?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route('/competence/connect_discipline/<competence_id>', methods=['GET'])
def connect_disciplines_to_competence(competence_id):
    type = "competence"
    # Необходима функция
    competence = Competence.query.get(competence_id)
    form = CompetenceConnectForm()
    checked=[]
    # Необходима функция
    check = CompetenceDiscipline.query.filter_by(competence_id=competence_id).all()
    for ch in check:
        checked.append(ch.discipline_id)
    print(checked)

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])
    disciplines = get_disciplines(direction=current_direction, year=current_year)

    return render_template("CompetenceDisciplines.html", type=type, form=form, competence=competence, disciplines=disciplines, years=years, directions=directions, current_year=current_year, current_direction=current_direction, checked=checked)


@UKUP.route('/competence/connect_discipline/<competence_id>', methods=['POST'])
def connect_disciplines_to_competence_post(competence_id):
    req = request.form.getlist("connect")
    # В будущем заменить на другую функцию
    for check in req:
        connect_discipline_with_competence(competence_id, check, request.args["year"])
    return redirect("/UKUP/competence")


@UKUP.route('/discipline/connect_competence/<discipline_id>', methods=["GET"])
def connect_competences_to_discipline(discipline_id):
    type = "discipline"

    # Необходима функция
    discipline = Discipline.query.get(discipline_id)


    form = CompetenceConnectForm()
    checked = []
    check = get_connected_competences(discipline_id)
    #check = CompetenceDiscipline.query.filter_by(discipline_id=discipline_id).all()
    for ch in check:
        checked.append(ch.id)

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    # Необходима функция
    competence = Competence.query.all()

    return render_template('connectCompetences.html', type=type, form=form,
                           competences=competence,
                           discipline=discipline,
                           years=years,
                           directions=directions,
                           current_direction=current_direction,
                           current_year=current_year,
                           checked=checked)


@UKUP.route('/discipline/connect_competence/<discipline_id>', methods=['POST'])
def connect_competences_to_discipline_db(discipline_id):

    checked = request.form.getlist("connect")
    year = request.args["year"]

    already_exist = CompetenceDiscipline.query\
                                        .filter_by(discipline_id=discipline_id)\
                                        .filter_by(year_created=year)\
                                        .all()

    # НЕ ПРОТЕСТИРОВАНО
    #for ref in already_exist:
    #    if ref.competence_id not in checked:
    #        delete_connection(connection_id=ref.id)

    for check in checked:
        connect_discipline_with_competence(discipline_id=discipline_id,
                                           competence_id=check,
                                           year=year)
    return redirect("/UKUP/discipline")


@UKUP.route("/addData")
def addData():
    return add_few_data()
