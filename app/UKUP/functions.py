from datetime import date
from .forms import DisciplineForm, CompetenceForm
from app.models import Discipline, db, Department, Block, Module, Direction, DirectionDiscipline, Competence


def get_not_available_comp_numbers_for_type(type: str, direction, year):
    competence_names = Competence.query.filter_by(type= type) \
        .filter_by(direction_id=direction) \
        .filter_by(year_approved=year) \
        .with_entities(Competence.name).all()
    numbers = []
    if competence_names is not None:
        for competence_name in competence_names:
            number = int(str(competence_name[0]).split("-")[1])
            numbers.append(number)
        numbers.sort()

    return numbers


def generate_year(year):
    years = []
    current_year = date.today().year
    for year in range(year, current_year + 2):
        years.append(year)
    return years

def add_few_data():
    directions = [
        Direction(name="Математика", code="01.03.01"),
        Direction(name="Прикладная математика и информатика", code="01.03.02"),
        Direction(name="Информационные системы и технологии", code="09.03.02"),
        Direction(name="Программная инженерия", code="09.03.04"),
        Direction(name="Педагогическое образование", code="44.03.05")
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
        Block(name="Б1.В.ОД"),
        Block(name="Б1.В.ВД"),
        Block(name="Б2.Б"),
        Block(name="Б2.В"),
        Block(name="Б3"),
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
        return "Всё ок, братан"
    except Exception:
        db.session.rollback()
        return "Всё не ок, братан"