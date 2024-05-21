from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Discipline, db, Department, Block, Module, Direction, DirectionDiscipline, Competence, CompetenceDiscipline, Indicator
from .forms import DisciplineForm, CompetenceForm, ConnectForm
from .functions import add_few_data, get_not_available_comp_numbers_for_type, generate_year
from .module_db import connect_discipline_with_competence
from .moduleDB import (get_disciplines, get_competences, add_discipline, add_competence,
                       get_modules, get_block, get_directions, get_departments, edit_discipline,
                       edit_competence, get_connected_competences, get_discipline_by_id,
                       get_competence_by_id, get_direction_by_id, get_disciplines_and_links_by_competence_id,
                       update_discipline_competences, update_competence_disciplines, get_indicators_for_discipline,
                       get_connected_competences, update_discipline_indicators,
                       get_indicators_disciplines_links_by_competence_id, update_indicator_disciplines,
                       delete_discipline, delete_competence, get_competences_and_indicators, get_competences_and_indicators_type, report_matrix)


UKUP = Blueprint('UKUP', __name__, template_folder='templates', static_folder='static')


@UKUP.route("/discipline", methods=["GET"])
def discipline():
    type = "discipline"
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = get_direction_by_id(request.args["direction"])

    disciplines = get_disciplines(directionID=current_direction.id, year=current_year)
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
        current_direction = get_direction_by_id(request.args["direction"])
    competence = get_competences(direction=current_direction.id, year=current_year)
    #print(competence)

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
    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route("/competence/add")
def add_competence_page():
    type = "competence"
    UK = get_not_available_comp_numbers_for_type("УК", request.form.get('current_direction'), request.form.get('current_year'))
    OPK = get_not_available_comp_numbers_for_type("ОПК", request.form.get('current_direction'), request.form.get('current_year'))
    PK = get_not_available_comp_numbers_for_type("ПК", request.form.get('current_direction'), request.form.get('current_year'))
    year_choices = generate_year(2019)


    years = generate_year(2019)[::-1]
    directions = get_directions()
    direction_choices = []
    for direction in directions:
        direction_choices.append((direction.id, direction.name))
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = get_direction_by_id(request.args["direction"])

    form = CompetenceForm(year_approved=current_year)
    form.addYear(year=year_choices)
    form.addDirection(direction=direction_choices)
    return render_template("addCompetence.html", type=type, form=form, UK=UK, OPK=OPK, PK=PK, years=years,
                           directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route("/competence/add", methods=["POST"])
def add_competence_post():
    form = CompetenceForm(request.form)

    #number = int(str(form.name.data).split("-")[1])
    #if number in not_available_numbers:
        #flash("Номер компетенции недопустим")
    #else:
    #print(form.direction)
    add_competence([form.name.data, form.year_approved.data, form.type.data, form.formulation.data, form.direction.data])
    return redirect(f"/UKUP/competence?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route('/discipline/<discipline_id>', methods=['GET'])
def edit_discipline_page(discipline_id):
    type = "discipline"

    # Необходима функция
    discipline = Discipline.query.get(discipline_id)

    year_approved = generate_year(2019)

    directions = get_directions()
    direction_choices = []
    for direction in directions:
        direction_choices.append((direction.id, direction.name))

    #print(direction_choices)

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
    directionDiscipline = DirectionDiscipline.query.filter_by(discipline_id=discipline.id).all()
    dirDiscipline =[]
    for direction_link in directionDiscipline:
        direction = get_direction_by_id(direction_link.direction_id)
        dirDiscipline.append((direction.id, direction.name))

    #print(dirDiscipline)



    years = generate_year(2019)[::-1]
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])

    form = DisciplineForm(name=discipline.name, year_approved=discipline.year_approved,
                          block=discipline.block_id, module=discipline.module_id,
                          department=discipline.department_id, direction=dirDiscipline)
    form.addData(year_approved, block_choices, module_choices, department_choices, direction_choices)

    return render_template("editDiscipline.html", type=type, form=form, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


@UKUP.route('/discipline/<discipline_id>', methods=['POST'])
def edit_discipline_post(discipline_id):
    form = DisciplineForm(request.form)
    #print(request.form)
    edit_discipline(discipline_id, [form.name.data, form.year_approved.data, form.block.data, form.module.data, form.department.data], form.direction.data)
    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route('/competence/<competence_id>')
def edit_competence_page(competence_id):
    type = "competence"
    UK = get_not_available_comp_numbers_for_type("УК", request.form.get('current_direction'), request.form.get('current_year'))
    OPK = get_not_available_comp_numbers_for_type("ОПК", request.form.get('current_direction'), request.form.get('current_year'))
    PK = get_not_available_comp_numbers_for_type("ПК", request.form.get('current_direction'), request.form.get('current_year'))

    # Необходима функция
    competence = Competence.query.get(competence_id)

    year_approved = generate_year(2019)

    indicators = Indicator.query.filter_by(competence_id=competence_id).all()

    form = CompetenceForm(name=competence.name, year_approved=competence.year_approved,
                          num=int(competence.name.split("-")[1]), type=competence.type, formulation=competence.formulation)
    form.addYear(year_approved)

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])

    return render_template("editCompetence.html", type=type, form=form, UK=UK, OPK=OPK, PK=PK, years=years, directions=directions, current_year=current_year, current_direction=current_direction, indicators=indicators)


@UKUP.route('/competence/<competence_id>', methods=['POST'])
def edit_competence_post(competence_id):
    form = CompetenceForm(request.form)
    #print(request.form.getlist("indicator"))
    indicators = []
    for indicator in request.form.getlist("indicator"):
        a = indicator.split("||")
        if a[2].strip()!="":
            indicators.append((a[0], a[1], a[2]))
    #print(indicators)
    #print(form.data)
    edit_competence(competence_id, [form.name.data, form.type.data, form.formulation.data, form.year_approved.data], indicators)
    return redirect(f"/UKUP/competence?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route('/competence/connect_discipline/<competence_id>', methods=['GET'])
def connect_disciplines_to_competence(competence_id):
    type = "competence"
    # Необходима функция
    competence = get_competence_by_id(competence_id)
    form = ConnectForm()
    checked=[]
    # Необходима функция
    disciplines, check = get_disciplines_and_links_by_competence_id(competence_id)
    for ch in check:
        checked.append(ch.discipline_id)
    #print(checked)

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = get_direction_by_id(request.args["direction"])
    return render_template("CompetenceDisciplines.html", type=type, form=form, competence=competence, disciplines=disciplines, years=years, directions=directions, current_year=current_year, current_direction=current_direction, checked=checked)


@UKUP.route('/competence/connect_discipline/<competence_id>', methods=['POST'])
def connect_disciplines_to_competence_post(competence_id):
    checked = request.form.getlist("connect")
    update_competence_disciplines(competence_id, checked)
    return redirect(f"/UKUP/competence?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route('/discipline/connect_competence/<discipline_id>', methods=["GET"])
def connect_competences_to_discipline(discipline_id):
    type = "discipline"

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    # Необходима функция
    discipline = get_discipline_by_id(discipline_id)


    form = ConnectForm()
    checked = []
    check = get_connected_competences(discipline_id, current_direction.id, current_year)
    #check = CompetenceDiscipline.query.filter_by(discipline_id=discipline_id).all()
    for ch in check:
        checked.append(ch.id)



    # Необходима функция
    competence = get_competences(current_direction.id, discipline.year_approved)

    return render_template('connectCompetences.html', type=type, form=form,
                           competences=competence,
                           discipline=discipline,
                           years=years,
                           directions=directions,
                           current_direction=current_direction,
                           current_year=current_year,
                           checked=checked)


@UKUP.route('/discipline/connect_competence/<discipline_id>', methods=['POST'])
def connect_competences_to_discipline_post(discipline_id):
    checked = request.form.getlist("connect")
    update_discipline_competences(discipline_id, checked, request.form.get('current_direction'))
   #print(request.form.get('year'))

    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route("/discipline/<discipline_id>/indicators")
def connect_indicators_discipline(discipline_id):
    type = "discipline"
    form = ConnectForm()

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    discipline = get_discipline_by_id(discipline_id)
    competencies = get_connected_competences(discipline_id, current_direction.id, current_year)
    competencies_id = []
    for competence in competencies:
        competencies_id.append(competence.id)
    indicators, checked = get_indicators_for_discipline(discipline_id, competencies_id)
    indicators.sort(key=lambda x: x.name)
    #print(checked[0].indicator_id)
    checked_id = []
    for check in checked:
        checked_id.append(check.indicator_id)

    #print(competencies)
    #print(indicators[0].name)


    return render_template('IndicatorsDiscipline.html', type=type, form=form,
                           competencies=competencies,
                           discipline=discipline,
                           indicators=indicators,
                           years=years,
                           directions=directions,
                           current_direction=current_direction,
                           current_year=current_year,
                           checked=checked_id)


@UKUP.route("/discipline/<discipline_id>/indicators", methods=['POST'])
def connect_indicators_discipline_post(discipline_id):
    indicators_id = []
    indicators = request.form.getlist("connect")
    for indicator in indicators:
        indicators_id.append(int(indicator))

    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    competencies = get_connected_competences(discipline_id, current_direction.id, current_year)
    competencies_id = []
    for competence in competencies:
        competencies_id.append(competence.id)

    update_discipline_indicators(discipline_id, competencies_id, indicators_id)
    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route("/competence/<competence_id>/indicators")
def connect_indicators_competence(competence_id):
    type = "competence"
    form = ConnectForm()

    competence = get_competence_by_id(competence_id)

    indicators, disciplines, checked = get_indicators_disciplines_links_by_competence_id(competence_id)
    indicators.sort(key=lambda x: x.name)

    checked_id = []
    for check in checked:
        checked_id.append(f"{check.indicator_id}-{check.discipline_id}")

    #print(competencies)
    #print(indicators[0].name)

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])


    return render_template('IndicatorsCompetence.html', type=type, form=form,
                           competence=competence,
                           disciplines=disciplines,
                           indicators=indicators,
                           years=years,
                           directions=directions,
                           current_direction=current_direction,
                           current_year=current_year,
                           checked=checked_id)


@UKUP.route("/competence/<competence_id>/indicators", methods=['POST'])
def connect_indicators_competence_post(competence_id):
    #print(request.form)
    indicators, he, hi = get_indicators_disciplines_links_by_competence_id(competence_id)
    indicator_disciplines = []
    #indicators = request.form.getlist("connect")
    for indicator in indicators:
        indicator_disciplines.append((indicator.id, request.form.getlist(str(indicator.id))))

    #print(hehe)

    update_indicator_disciplines(indicator_disciplines)

    #competencies = get_connected_competences(competence_id)
    #competencies_id = []
    #for competence in competencies:
    #    competencies_id.append(competence.id)

    #update_discipline_indicators(discipline_id, competencies_id, indicators_id)
    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


@UKUP.route("/discipline/delete/<discipline_id>", methods=['POST'])
def delete_discipline_post(discipline_id):
    delete_discipline(discipline_id)
    return redirect(f"/UKUP/discipline?year={request.form.get('year')}&direction={request.form.get('direction')}")


@UKUP.route("/competence/delete/<competence_id>", methods=['POST'])
def delete_competence_post(competence_id):
    delete_competence(competence_id)
    return redirect(f"/UKUP/competence?year={request.form.get('year')}&direction={request.form.get('direction')}")


@UKUP.route("report/competence/<type>")
def report_competence(type):
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    competences, indicators = get_competences_and_indicators_type(current_direction.id, current_year, type)
    #competences, indicators = get_competences_and_indicators(current_direction.id, current_year)
    #print(type)
    print(competences)
    print(indicators)
    return render_template('reportCompetence.html', type=type,
                           competences=competences,
                           indicators=indicators,
                           direction=current_direction,
                           year=current_year)


@UKUP.route("report/competence/all")
def report_all_competence():
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    UK_competences, UK_indicators = get_competences_and_indicators_type(current_direction.id, current_year, "УК")
    OPK_competences, OPK_indicators = get_competences_and_indicators_type(current_direction.id, current_year, "ОПК")
    PK_competences, PK_indicators = get_competences_and_indicators_type(current_direction.id, current_year, "ПК")
    type = ["Универсальная компетенция", "Общепрофессиональная компетенция", "Профессиональная компетенция"]
    competences = [UK_competences, OPK_competences, PK_competences]
    indicators = [UK_indicators, OPK_indicators, PK_indicators]
    #competences, indicators = get_competences_and_indicators(current_direction.id, current_year)
    #print(type)
    #print(competences)
    #print(indicators)
    return render_template('reportAllCompetence.html', types=type,
                           competences=competences, indicators=indicators,
                           direction=current_direction,
                           year=current_year)


@UKUP.route("report/matrix")
def report_matrix_page():
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])

    disciplines, competences, discipline_competence_link = report_matrix(current_direction.id, current_year)
    print(discipline_competence_link)

    UK_competences, UK_indicators = get_competences_and_indicators_type(current_direction.id, current_year, "УК")
    OPK_competences, OPK_indicators = get_competences_and_indicators_type(current_direction.id, current_year, "ОПК")
    PK_competences, PK_indicators = get_competences_and_indicators_type(current_direction.id, current_year, "ПК")
    type = ["Универсальная компетенция", "Общепрофессиональная компетенция", "Профессиональная компетенция"]
    competences = [UK_competences, OPK_competences, PK_competences]

    return render_template('reportMatrix.html', types=type,
                           UK_competences=UK_competences,
                           OPK_competences=OPK_competences,
                           PK_competences=PK_competences,
                           disciplines=disciplines,
                           dis_comp_link=discipline_competence_link,
                           direction=current_direction,
                           year=current_year)


@UKUP.route("/addData")
def addData():
    return add_few_data()
