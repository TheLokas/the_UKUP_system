from flask import Blueprint, render_template
from app.models import Discipline, Competence

#class Discipline:
# def __init__(self, name, block, faculty, module):
#     self.name = name
#     self.block = block
#     self.faculty = faculty
#     self.module = module


#class Competence:
# def __init__(self, code, description, type):
#     self.code = code
#     self.description = description
#     self.type = type


#disciplines = [Discipline("Линейная алгебра", "Б1.Б", "МА", "Математические и естественнонаучные дисциплины"), Discipline("Матанализ", "Б1.Б", "МА", "Математические и естественнонаучные дисциплины"), Discipline("Дискретная математика", "Б1.Б", "ПМиК", "Модуль 2")]


UKUP = Blueprint('UKUP', __name__, template_folder='templates', static_folder='static')
#competencies = [Competence("УК-1", "Способен осуществлять поиск, критический анализ и синтез информации, применять системный подход для решения поставленных задач", "Универсальные компетенции"),
#               Competence("УК-2", "Способен определять круг задач в рамках поставленной цели и выбирать оптимальные способы их решения, исходя из действующих правовых норм, имеющихся ресурсов и ограничений", "Универсальные компетенции"),
#               Competence("ОПК-1", "Способен применять естественнонаучные и общеинженерные знания, методы математического анализа и моделирования, теоретического и экспериментального исследования в профессиональной деятельности", "Общепрофессиональные компетенции"),
#               Competence("ОПК-2", "Способен понимать принципы работы современных информационных технологий и программных средств, в том числе отечественного производства, и использовать их при решении задач профессиональной деятельности", "Общепрофессиональные компетенции"),
#               Competence("ОПК-3", "Способен решать стандартные задачи профессиональной деятельности на основе информационной и библиографической культуры с применением информационно-коммуникационных технологий и с учетом основных требований информационной безопасности", "Общепрофессиональные компетенции"),
#               Competence("ПК-1", "Способен осуществлять выявление требований к информационным системам", "Профессиональные компетенции"),
#               Competence("ПК-2", "Способность осуществлять проектирование и дизайн ИС", "Профессиональные компетенции"),
#               Competence("ПК-3", "Способность осуществлять разработку прототипов ИС", "Профессиональные компетенции")]

disciplines = Discipline.query.all()
competencies = Competence.query.all()

@UKUP.route("/discipline")
def discipline():
    return render_template("discipline.html", disciplines=disciplines)


@UKUP.route("/competence")
def competence():
    return render_template("competence.html", competencies=competencies)

@UKUP.route("/test")
def test():
    return render_template("competence.html", competencies=competencies)


