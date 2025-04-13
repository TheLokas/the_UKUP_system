from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Discipline, db, Department, Block, Module, Direction, DirectionDiscipline, Competence, \
    CompetenceDiscipline, Indicator, ZE, RequiredDiscipline, IndicatorDiscipline
from .forms import DisciplineForm, CompetenceForm, ConnectForm, ZEForm
from .functions import add_few_data, get_not_available_comp_numbers_for_type, generate_year
from .module_db import connect_discipline_with_competence
from .moduleDB import (get_disciplines, get_competences, add_discipline, add_competence,
                       get_modules, get_block, get_directions, get_departments, edit_discipline,
                       edit_competence, get_connected_competences, get_discipline_by_id,
                       get_competence_by_id, get_direction_by_id, get_disciplines_and_links_by_competence_id,
                       update_discipline_competences, update_competence_disciplines, get_indicators_for_discipline,
                       get_connected_competences, update_discipline_indicators,
                       get_indicators_disciplines_links_by_competence_id, update_indicator_disciplines,
                       delete_discipline, delete_competence, get_competences_and_indicators, get_competences_and_indicators_type,
                       report_matrix, get_required_disciplines, get_required_discipline, update_data, get_ze, update_ze)
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

UKUP = Blueprint('UKUP', __name__, template_folder='templates', static_folder='static')

# Страница дисциплин
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
    return render_template("Discipline.html", type=type, disciplines=disciplines,
                           years=years, directions=directions, current_year=current_year,
                           current_direction=current_direction)


# Страница компетенций
@UKUP.route("/competence", methods=['GET'])
def competence():
    type = "competence"
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = get_direction_by_id(request.args["direction"])
    competence = get_competences(direction=current_direction.id, year=current_year)

    return render_template("Competence.html", type=type,
                           competencies=competence, years=years, directions=directions,
                           current_year=current_year, current_direction=current_direction)


# Страница добавления дисциплин
@UKUP.route("/discipline/add", methods=['GET'])
def add_discipline_page():
    type = "discipline"
    year_choices = generate_year(2019)
    # Получение списков и формирование из них списков кортежей из id и name
    # Направления
    directions = get_directions()
    direction_choices = []
    for direction in directions:
        direction_choices.append((direction.id, direction.name))
    # Кафедры
    departments = get_departments()
    department_choices = []
    for department in departments:
        department_choices.append((department.id, department.name))
    # Модули
    modules = get_modules()
    module_choices = []
    for module in modules:
        module_choices.append((module.id, module.name))
    # Блоки
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
        current_direction = Direction.query.get(request.args["direction"])

    # Получение списка необходимых (базовых) дисциплин и формирование из них списка кортежей из id и name
    disciplines = get_disciplines(directionID=current_direction.id, year=current_year)
    required_disciplines_choices = [(-1, " - ")]
    for discipline in disciplines:
        required_disciplines_choices.append((discipline.id, discipline.name))

    # Инициализация формы и установка начальных зачений
    form = DisciplineForm(year_approved=current_year, direction=(current_direction.id, current_direction.name))
    # Заполнение формы
    form.addData(year=year_choices, block=block_choices,
                 module=module_choices, direction=direction_choices,
                 department=department_choices, required_discipines=required_disciplines_choices)
    return render_template("addDiscipline.html",type=type, form=form, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


# Обработка POST-запроса на добавление дисциплины
@UKUP.route("/discipline/add", methods=['POST'])
def add_discipline_post():
    form = DisciplineForm(request.form)
    add_discipline([form.name.data, form.year_approved.data, form.block.data, form.module.data, form.department.data], form.direction.data, form.required.data)
    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


# Страница добавления компетенций
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


# Обработка POST-запроса на добавление компетенции
@UKUP.route("/competence/add", methods=["POST"])
def add_competence_post():
    form = CompetenceForm(request.form)

    #number = int(str(form.name.data).split("-")[1])
    #if number in not_available_numbers:
        #flash("Номер компетенции недопустим")
    #else:
    #print(form.direction)
    #print("this '" + form.source.data + "'." + " type '" + str(type(form.source.data)) + "'.")
    add_competence([form.name.data, form.year_approved.data, form.type.data, form.formulation.data, form.direction.data, form.source.data])
    return redirect(f"/UKUP/competence?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


# Страница выбранной дисциплины
@UKUP.route('/discipline/<discipline_id>', methods=['GET'])
def edit_discipline_page(discipline_id):

    type = "discipline"
    discipline = get_discipline_by_id(discipline_id)
    year_approved = generate_year(2019)

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
    directionDiscipline = DirectionDiscipline.query.filter_by(discipline_id=discipline.id).all()
    dirDiscipline =[]
    for direction_link in directionDiscipline:
        direction = get_direction_by_id(direction_link.direction_id)
        dirDiscipline.append((direction.id, direction.name))


    # Установка текущего года и направления 
    years = generate_year(2019)[::-1]
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        # Необходима функция
        current_direction = Direction.query.get(request.args["direction"])

    # Получение списка необходимых дисциплин
    required_disciplines = get_required_disciplines(directionID=current_direction.id, year=current_year, current_discipline_id=discipline_id)
    required_disciplines_choices = [(-1, " - ")]
    for required_discipline in required_disciplines:
        required_disciplines_choices.append((required_discipline.id, required_discipline.name))

    # Получение необходимой дисциплины
    required_id = -1
    required_discipline = get_required_discipline(discipline_id)
    if not required_discipline is None:
        required_id = required_discipline.id
    

    # Заполнение формы 
    form = DisciplineForm(name=discipline.name, year_approved=discipline.year_approved,
                          block=discipline.block_id, module=discipline.module_id,
                          department=discipline.department_id, direction=dirDiscipline, required= required_id)
    form.addData(year_approved, block_choices, module_choices, department_choices, direction_choices, required_disciplines_choices)

    return render_template("editDiscipline.html", type=type, form=form, years=years, directions=directions, current_year=current_year, current_direction=current_direction)


# Обработка POST-запроса на обновление выбранной дисциплины
@UKUP.route('/discipline/<discipline_id>', methods=['POST'])
def edit_discipline_post(discipline_id):
    form = DisciplineForm(request.form)
    #print(request.form)
    edit_discipline(discipline_id, [form.name.data, form.year_approved.data, form.block.data, form.module.data, form.department.data], form.direction.data, form.required.data)
    return redirect(f"/UKUP/discipline?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


# Страница выбранной компетенции
@UKUP.route('/competence/<competence_id>')
def edit_competence_page(competence_id):
    type = "competence"
    UK = get_not_available_comp_numbers_for_type("УК", request.form.get('current_direction'), request.form.get('current_year'))
    OPK = get_not_available_comp_numbers_for_type("ОПК", request.form.get('current_direction'), request.form.get('current_year'))
    PK = get_not_available_comp_numbers_for_type("ПК", request.form.get('current_direction'), request.form.get('current_year'))

    competence = get_competence_by_id(competence_id)

    year_approved = generate_year(2019)

    indicators = Indicator.query.filter_by(competence_id=competence_id).all()

    form = CompetenceForm(name=competence.name, year_approved=competence.year_approved,
                          num=int(competence.name.split("-")[1]), type=competence.type,
                          formulation=competence.formulation, source=competence.source)
    form.addYear(year_approved)

    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = get_direction_by_id(request.args["direction"])

    return render_template("editCompetence.html", type=type, form=form, UK=UK, OPK=OPK, PK=PK, years=years, directions=directions, current_year=current_year, current_direction=current_direction, indicators=indicators)


# Обработка POST-запроса на обновление выбранной компетенции
@UKUP.route('/competence/<competence_id>', methods=['POST'])
def edit_competence_post(competence_id):
    form = CompetenceForm(request.form)
    indicators = []
    for indicator in request.form.getlist("indicator"):
        a = indicator.split("||")
        if a[2].strip()!="":
            indicators.append((a[0], a[1], a[2]))

    edit_competence(competence_id, [form.name.data, form.type.data, form.formulation.data, form.year_approved.data, form.source.data], indicators)
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
    delete_discipline(int(discipline_id))
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

@UKUP.route("/updateData")
def updateData():
    update_data()
    return "обновили зачетные единицы"


@UKUP.route("/ze")
def ze():
    years = generate_year(2019)[::-1]
    directions = get_directions()
    current_direction = directions[0]
    current_year = date.today().year
    if request and {"year", "direction"} <= set(request.args):
        current_year = request.args["year"]
        current_direction = Direction.query.get(request.args["direction"])
    ze = get_ze(current_direction.id, current_year)
    form = ZEForm()
    return render_template('ze.html', current_direction=current_direction,
                           years=years,
                           current_year=current_year, ze=ze, form=form)


@UKUP.route("/ze", methods=['POST'])
def ze_post():
    ze = get_ze(request.form.get('current_direction'), request.form.get('current_year'))
    ze_discipline_id_list = []
    for z in ze:
        ze_discipline_id_list.append(z.discipline.id)
    ze_dict = {}
    for id in ze_discipline_id_list:
        ze_dict[id]={}
        k = 0
        for i in range(1,9):
            number = int(request.form.get(f"{id}-{i}")) if request.form.get(f"{id}-{i}") else 0
            ze_dict[id][i] = number
            k = k + number
        ze_dict[id]["ze"] = k
    update_ze(ze_dict)
    return redirect(f"/UKUP/ze?year={request.form.get('current_year')}&direction={request.form.get('current_direction')}")


# Декоратор маршрута Flask для обработки POST-запросов на '/copy-data'
@UKUP.route('/copy-data', methods=['POST'])
def copy_data():
    try:
        data = request.get_json()
        source_year = int(data['sourceYear'])
        target_year = int(data['targetYear'])
        direction_ids = list(map(int, data['directions']))
        entities = data['entities']
        overwrite = data.get('overwrite', False)  # Получаем параметр перезаписи

        result = {
            'copied': 0,
            'updated': 0,
            'skipped': 0,
            'details': {
                'disciplines': {'created': [], 'updated': [], 'skipped': []},
                'competences': {'created': [], 'updated': [], 'skipped': []},
                'discipline_competence_links': {'created': [], 'skipped': []},
                'discipline_indicator_links': {'created': [], 'skipped': []},
                'ze': {'created': [], 'updated': [], 'skipped': []},
                'dependent_disciplines': {'created': [], 'skipped': []}
            }
        }

        # 1. Копирование дисциплин
        if 'disciplines' in entities:
            for direction_id in direction_ids:
                source_disciplines = Discipline.query.join(
                    DirectionDiscipline
                ).filter(
                    DirectionDiscipline.direction_id == direction_id,
                    Discipline.year_approved == source_year
                ).all()

                for disc in source_disciplines:
                    target_disc = Discipline.query.join(
                        DirectionDiscipline
                    ).filter(
                        DirectionDiscipline.direction_id == direction_id,
                        Discipline.name == disc.name,
                        Discipline.year_approved == target_year
                    ).first()

                    if not target_disc:
                        # Создаем новую дисциплину
                        new_disc = Discipline(
                            name=disc.name,
                            year_approved=target_year,
                            block_id=disc.block_id,
                            module_id=disc.module_id,
                            department_id=disc.department_id
                        )
                        db.session.add(new_disc)
                        db.session.flush()

                        # Создаем ZE
                        new_ze = ZE(
                            discipline_id=new_disc.id,
                            c1=0, c2=0, c3=0, c4=0,
                            c5=0, c6=0, c7=0, c8=0,
                            ze=0
                        )
                        db.session.add(new_ze)

                        # Копируем связи с направлениями
                        direction = Direction.query.get(direction_id)
                        new_disc.directions.append(direction)

                        result['details']['disciplines']['created'].append(disc.name)
                        result['copied'] += 1

                        # Копируем ZE если нужно
                        if 'ze' in entities and disc.ze:
                            source_ze = disc.ze[0] if disc.ze else None
                            if source_ze:
                                new_ze.c1 = source_ze.c1
                                new_ze.c2 = source_ze.c2
                                new_ze.c3 = source_ze.c3
                                new_ze.c4 = source_ze.c4
                                new_ze.c5 = source_ze.c5
                                new_ze.c6 = source_ze.c6
                                new_ze.c7 = source_ze.c7
                                new_ze.c8 = source_ze.c8
                                new_ze.ze = source_ze.ze
                                result['details']['ze']['created'].append(disc.name)

                        # Копируем зависимости если нужно
                        if 'dependent_disciplines' in entities:
                            dependencies = RequiredDiscipline.query.filter(
                                RequiredDiscipline.dependent_discipline_id == disc.id
                            ).all()

                            for dep in dependencies:
                                required_disc_name = db.session.query(Discipline.name)\
                                    .filter(Discipline.id == dep.required_discipline_id)\
                                    .scalar()

                                required_disc = Discipline.query.join(
                                    DirectionDiscipline
                                ).filter(
                                    DirectionDiscipline.direction_id == direction_id,
                                    Discipline.name == required_disc_name,
                                    Discipline.year_approved == target_year
                                ).first()

                                if required_disc:
                                    new_dep = RequiredDiscipline(
                                        required_discipline_id=required_disc.id,
                                        dependent_discipline_id=new_disc.id
                                    )
                                    db.session.add(new_dep)
                                    result['details']['dependent_disciplines']['created'].append(
                                        f"{disc.name} → {required_disc_name}"
                                    )

                    elif overwrite:
                        # Обновляем существующую дисциплину
                        target_disc.block_id = disc.block_id
                        target_disc.module_id = disc.module_id
                        target_disc.department_id = disc.department_id

                        # Обновляем ZE если нужно
                        if 'ze' in entities and disc.ze:
                            target_ze = target_disc.ze[0] if target_disc.ze else None
                            source_ze = disc.ze[0] if disc.ze else None
                            if target_ze and source_ze:
                                target_ze.c1 = source_ze.c1
                                target_ze.c2 = source_ze.c2
                                target_ze.c3 = source_ze.c3
                                target_ze.c4 = source_ze.c4
                                target_ze.c5 = source_ze.c5
                                target_ze.c6 = source_ze.c6
                                target_ze.c7 = source_ze.c7
                                target_ze.c8 = source_ze.c8
                                target_ze.ze = source_ze.ze
                                result['details']['ze']['updated'].append(disc.name)

                        result['details']['disciplines']['updated'].append(disc.name)
                        result['updated'] += 1
                    else:
                        result['details']['disciplines']['skipped'].append(disc.name)
                        result['skipped'] += 1

        # 2. Копирование компетенций
        if 'competences' in entities:
            for direction_id in direction_ids:
                source_competences = Competence.query.filter(
                    Competence.direction_id == direction_id,
                    Competence.year_approved == source_year
                ).all()

                for comp in source_competences:
                    target_comp = Competence.query.filter(
                        Competence.direction_id == direction_id,
                        Competence.name == comp.name,
                        Competence.year_approved == target_year
                    ).first()

                    if not target_comp:
                        # Создаем новую компетенцию
                        new_comp = Competence(
                            name=comp.name,
                            year_approved=target_year,
                            type=comp.type,
                            formulation=comp.formulation,
                            source=comp.source,
                            direction_id=direction_id
                        )
                        db.session.add(new_comp)
                        db.session.flush()

                        result['details']['competences']['created'].append(comp.name)
                        result['copied'] += 1

                        # Копируем индикаторы если нужно
                        if 'indicators' in entities:
                            for indicator in comp.indicators:
                                new_ind = Indicator(
                                    name=indicator.name,
                                    formulation=indicator.formulation,
                                    competence_id=new_comp.id
                                )
                                db.session.add(new_ind)

                    elif overwrite:
                        # Обновляем существующую компетенцию
                        target_comp.type = comp.type
                        target_comp.formulation = comp.formulation
                        target_comp.source = comp.source

                        # Обновляем индикаторы если нужно
                        if 'indicators' in entities:
                            # Удаляем старые индикаторы
                            Indicator.query.filter_by(competence_id=target_comp.id).delete()
                            # Добавляем новые
                            for indicator in comp.indicators:
                                new_ind = Indicator(
                                    name=indicator.name,
                                    formulation=indicator.formulation,
                                    competence_id=target_comp.id
                                )
                                db.session.add(new_ind)

                        result['details']['competences']['updated'].append(comp.name)
                        result['updated'] += 1
                    else:
                        result['details']['competences']['skipped'].append(comp.name)
                        result['skipped'] += 1

        # 3. Копирование связей дисциплина-компетенция
        if 'discipline_competence_links' in entities:
            for direction_id in direction_ids:
                source_links = db.session.query(CompetenceDiscipline)\
                    .join(Discipline, CompetenceDiscipline.discipline_id == Discipline.id)\
                    .join(Competence, CompetenceDiscipline.competence_id == Competence.id)\
                    .join(DirectionDiscipline, Discipline.id == DirectionDiscipline.discipline_id)\
                    .filter(
                        Discipline.year_approved == source_year,
                        Competence.year_approved == source_year,
                        DirectionDiscipline.direction_id == direction_id
                    ).all()

                for link in source_links:
                    disc_name = db.session.query(Discipline.name)\
                        .filter(Discipline.id == link.discipline_id).scalar()
                    comp_name = db.session.query(Competence.name)\
                        .filter(Competence.id == link.competence_id).scalar()

                    if not disc_name or not comp_name:
                        continue

                    target_disc = Discipline.query.join(
                        DirectionDiscipline,
                        Discipline.id == DirectionDiscipline.discipline_id
                    ).filter(
                        DirectionDiscipline.direction_id == direction_id,
                        Discipline.name == disc_name,
                        Discipline.year_approved == target_year
                    ).first()

                    target_comp = Competence.query.filter(
                        Competence.direction_id == direction_id,
                        Competence.name == comp_name,
                        Competence.year_approved == target_year
                    ).first()

                    if target_disc and target_comp:
                        exists = CompetenceDiscipline.query.filter(
                            CompetenceDiscipline.discipline_id == target_disc.id,
                            CompetenceDiscipline.competence_id == target_comp.id
                        ).first()

                        if not exists:
                            new_link = CompetenceDiscipline(
                                discipline_id=target_disc.id,
                                competence_id=target_comp.id
                            )
                            db.session.add(new_link)
                            result['details']['discipline_competence_links']['created'].append(
                                f"{disc_name} ↔ {comp_name}"
                            )
                            result['copied'] += 1
                        else:
                            result['details']['discipline_competence_links']['skipped'].append(
                                f"{disc_name} ↔ {comp_name}"
                            )
                            result['skipped'] += 1

        # 4. Копирование связей дисциплина-индикатор
        if 'discipline_indicator_links' in entities:
            for direction_id in direction_ids:
                source_links = db.session.query(IndicatorDiscipline)\
                    .join(Discipline, IndicatorDiscipline.discipline_id == Discipline.id)\
                    .join(Indicator, IndicatorDiscipline.indicator_id == Indicator.id)\
                    .join(Competence, Indicator.competence_id == Competence.id)\
                    .join(DirectionDiscipline, Discipline.id == DirectionDiscipline.discipline_id)\
                    .filter(
                        Discipline.year_approved == source_year,
                        Competence.year_approved == source_year,
                        DirectionDiscipline.direction_id == direction_id
                    ).all()

                for link in source_links:
                    disc_name = db.session.query(Discipline.name)\
                        .filter(Discipline.id == link.discipline_id).scalar()
                    ind_name = db.session.query(Indicator.name)\
                        .filter(Indicator.id == link.indicator_id).scalar()

                    if not disc_name or not ind_name:
                        continue

                    target_disc = Discipline.query.join(
                        DirectionDiscipline,
                        Discipline.id == DirectionDiscipline.discipline_id
                    ).filter(
                        DirectionDiscipline.direction_id == direction_id,
                        Discipline.name == disc_name,
                        Discipline.year_approved == target_year
                    ).first()

                    target_ind = Indicator.query.join(Competence)\
                        .filter(
                            Competence.direction_id == direction_id,
                            Indicator.name == ind_name,
                            Competence.year_approved == target_year
                        ).first()

                    if target_disc and target_ind:
                        exists = IndicatorDiscipline.query.filter(
                            IndicatorDiscipline.discipline_id == target_disc.id,
                            IndicatorDiscipline.indicator_id == target_ind.id
                        ).first()

                        if not exists:
                            new_link = IndicatorDiscipline(
                                discipline_id=target_disc.id,
                                indicator_id=target_ind.id
                            )
                            db.session.add(new_link)
                            result['details']['discipline_indicator_links']['created'].append(
                                f"{disc_name} → {ind_name}"
                            )
                            result['copied'] += 1
                        else:
                            result['details']['discipline_indicator_links']['skipped'].append(
                                f"{disc_name} → {ind_name}"
                            )
                            result['skipped'] += 1

        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Копирование завершено",
            "stats": result
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500