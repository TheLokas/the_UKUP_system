from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Discipline, db, Department, Block, Module, Direction, DirectionDiscipline, Competence
from .forms import DisciplineForm, CompetenceForm
from .functions import add_few_data, get_not_available_comp_numbers_for_type



#class Discipline:
#def __init__(self, name, block, faculty, module):
#   self.name = name
#   self.block = block
#   self.faculty = faculty
#   self.module = module


#class Competence:
#def __init__(self, code, description,  type):
#   self.code = code
#   self.description = description
#   self.type = type

#disciplines = [Discipline("Линейная алгебра", "Б1.Б", "МА", "Математические и естественнонаучные дисциплины"), Discipline("Матанализ", "Б1.Б", "МА", "Математические и естественнонаучные дисциплины"), Discipline("Дискретная математика", "Б1.Б", "ПМиК", "Модуль 2")]

#competencies = [Competence("УК-1", "Способен осуществлять поиск, критический анализ и синтез информации, применять системный подход для решения поставленных задач", "Универсальные компетенции"),
#         Competence("УК-2", "Способен определять круг задач в рамках поставленной цели и выбирать оптимальные способы их решения, исходя из действующих правовых норм, имеющихся ресурсов и ограничений", "Универсальные компетенции"),
#         Competence("ОПК-1", "Способен применять естественнонаучные и общеинженерные знания, методы математического анализа и моделирования, теоретического и экспериментального исследования в профессиональной деятельности", "Общепрофессиональные компетенции"),
#         Competence("ОПК-2", "Способен понимать принципы работы современных информационных технологий и программных средств, в том числе отечественного производства, и использовать их при решении задач профессиональной деятельности", "Общепрофессиональные компетенции"),
#         Competence("ОПК-3", "Способен решать стандартные задачи профессиональной деятельности на основе информационной и библиографической культуры с применением информационно-коммуникационных технологий и с учетом основных требований информационной безопасности", "Общепрофессиональные компетенции"),
#         Competence("ПК-1", "Способен осуществлять выявление требований к информационным системам", "Профессиональные компетенции"),
#         Competence("ПК-2", "Способность осуществлять проектирование и дизайн ИС", "Профессиональные компетенции"),
#         Competence("ПК-3", "Способность осуществлять разработку прототипов ИС", "Профессиональные компетенции")]




UKUP = Blueprint('UKUP', __name__, template_folder='templates', static_folder='static')

@UKUP.route("/discipline")
def discipline():
    disciplines = Discipline.query.order_by(Discipline.module_id)
    return render_template("Discipline.html", disciplines=disciplines)


@UKUP.route("/competence")
def competence():
    competence = Competence.query.all()
    return render_template("Competence.html", competencies=competence)


@UKUP.route("/test")
def test():
    competence = Competence.query.all()
    return render_template("competence.html", competencies=competence)


@UKUP.route("/discipline/add", methods=['POST', 'GET'])
def add_discipline():
    #form = DisciplineForm()
    #form.data([2020, 2021], ["блок1", "блок2"], ["модуль1", "модуль2"], ["кафедра1", "кафедра2"], ["Исит", "ПриМат", "ПрогИнж"])
    #return render_template("addDiscipline.html", form=form)

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
                                    department_id=form.department.data[0])
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
            return redirect("/UKUP/discipline")
        except Exception as e:
            print(e)
            db.session.rollback()
    return render_template("addDiscipline.html", form=form)


@UKUP.route("/competence/add")
def add_competence():
    UK = get_not_available_comp_numbers_for_type("УК")
    OPK = get_not_available_comp_numbers_for_type("ОПК")
    PK = get_not_available_comp_numbers_for_type("ПК")
    current_year = date.today().year
    year_choices = []
    for year in range(2019, current_year + 2):
        year_choices.append((year, year))
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


@UKUP.route("/addData")
def addData():
    return add_few_data()
