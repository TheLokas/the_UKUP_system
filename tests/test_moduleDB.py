from app.UKUP import moduleDB, functions
from app.models import (Discipline,
                        Direction,
                        DirectionDiscipline,
                        Competence,
                        CompetenceDiscipline,
                        IndicatorDiscipline,
                        Block,
                        Module,
                        Department)
from .conftest import db
from .data_func import (add_disciplines_data,
                        add_competence_data,
                        add_competence_discipline_links,
                        add_indicator_discipline_links,
                        add_all)
import pytest


class TestClassDisciplines:
    # Проверка возврата списка дисциплин с заданными параметрами (позитивный)
    def test_get_disciplines(client, app):
        added_disciplines, direction, direction_d = add_disciplines_data()
        got_disciplines = moduleDB.get_disciplines(direction=direction.id,
                                                   year="2023")
        assert added_disciplines[0] in got_disciplines
        assert added_disciplines[1] in got_disciplines

    # Проверка возврата списка дисциплин с заданными параметрами (негативный)
    def test_get_disciplines_negative(client, app):
        add_disciplines_data()
        disciplines = moduleDB.get_disciplines(direction=None,
                                               year="2023")
        assert len(disciplines) == 0

    # Проверка успешного добавления дисциплины
    def test_add_disciplines(client, app):
        functions.add_few_data()

        module = db.session.get(Module, 1)
        department = db.session.get(Department, 2)
        block = db.session.get(Block, 2)
        direction = db.session.get(Direction, 1)

        print(module)

        discipline_params = [
            "Новая дисциплина",
            "2024",
            block.id,
            module.id,
            department.id,
            ]

        moduleDB.add_discipline(discipline_params=discipline_params,
                                directions_list=[direction.id])

        discipline = Discipline.query.first()

        assert all([
            discipline.name == "Новая дисциплина",
            discipline.year_approved == 2024,
            discipline.block == block,
            discipline.module == module,
            discipline.department == department,
            direction in discipline.directions,
            len(discipline.directions) == 1
        ])

    # Проверка обработки некорректных входных данных
    # Failed: DID NOT RAISE <class 'ValueError'> date: 18:05:2024
    # Решение: сделать поля модуля, блока и кафедры обязательными
    def test_add_disciplines_negative(client, app):
        functions.add_few_data()

        module = None
        department = db.session.get(Department, 2)
        block = db.session.get(Block, 2)
        direction = db.session.get(Direction, 1)

        print(module)

        discipline_params = [
            "Новая дисциплина",
            "2024",
            block.id,
            module,
            department.id
            ]

        with pytest.raises(Exception) as er:
            moduleDB.add_discipline(discipline_params=discipline_params,
                                    directions_list=[direction.id])
            assert er.type is Exception

    # Проверка успешного редактирования дисциплины при новом году дисциплины
    def test_edit_discipline_with_new_year(client, app):
        year = 2024
        added_disciplines = add_disciplines_data()[0]
        discipline_to_edit = added_disciplines[0]

        module = db.session.get(Module, 2)
        department = db.session.get(Department, 1)
        block = db.session.get(Block, 2)
        direction = db.session.get(Direction, 3)

        new_discipline_params = [
            "Отредактированная дисциплина",
            year,
            block.id,
            module.id,
            department.id,
        ]

        moduleDB.edit_discipline(discipline_to_edit.id,
                                 new_discipline_params,
                                 directions_list=[direction.id])

        edited_discipline = Discipline.query.get(discipline_to_edit.id)

        assert all([
            edited_discipline.name == new_discipline_params[0],
            edited_discipline.year_approved == new_discipline_params[1],
            edited_discipline.block_id == new_discipline_params[2],
            edited_discipline.module_id == new_discipline_params[3],
            edited_discipline.department_id == new_discipline_params[4],
            len(edited_discipline.directions) == 1,
            direction in edited_discipline.directions
        ])

    # Проверка успешного редактирования дисциплины при том же году дисциплины
    def test_edit_discipline_with_same_year(client, app):
        added_disciplines = add_disciplines_data()[0]
        discipline_to_edit = added_disciplines[0]
        year = discipline_to_edit.year_approved

        module = db.session.get(Module, 2)
        department = db.session.get(Department, 1)
        block = db.session.get(Block, 2)
        direction = db.session.get(Direction, 3)

        new_discipline_params = [
            "Отредактированная дисциплина",
            year,
            block.id,
            module.id,
            department.id,
        ]

        moduleDB.edit_discipline(discipline_to_edit.id,
                                 new_discipline_params,
                                 directions_list=[direction.id])

        edited_discipline = Discipline.query.get(discipline_to_edit.id)

        assert all([
            edited_discipline.name == new_discipline_params[0],
            edited_discipline.year_approved == new_discipline_params[1],
            edited_discipline.block_id == new_discipline_params[2],
            edited_discipline.module_id == new_discipline_params[3],
            edited_discipline.department_id == new_discipline_params[4],
            len(edited_discipline.directions) == 1,
            direction in edited_discipline.directions
        ])

    # Проверка обработки некорректного идентификатора
    # Failed: DID NOT RAISE <class 'Exception'>
    # Date: 18:05:2024
    def test_edit_discipline_negative(client, app):
        year = 2023
        module = db.session.get(Module, 2)
        department = db.session.get(Department, 1)
        block = db.session.get(Block, 2)
        direction = db.session.get(Direction, 3)

        new_discipline_params = [
            "Отредактированная дисциплина",
            year,
            block.id,
            module.id,
            department.id,
        ]

        with pytest.raises(Exception) as er:
            moduleDB.edit_discipline(99,
                                     new_discipline_params,
                                     directions_list=[direction.id])
            assert er.type is ValueError

    # Проверка успешного удаления дисциплины
    def test_delete_discipline(client, app):
        added_disciplines, direction, direction_disciplines = add_disciplines_data()  # noqa E501
        indicator_disciplines = add_indicator_discipline_links()
        competences_discipline = add_competence_discipline_links()

        discipline_to_delete = added_disciplines[0]

        moduleDB.delete_discipline(discipline_to_delete.id)

        assert all([
            direction_disciplines[0] not in DirectionDiscipline.query.all(),
            indicator_disciplines[0] not in IndicatorDiscipline.query.all(),
            competences_discipline[0] not in CompetenceDiscipline.query.all(),
        ])


class TestClassCompetences:
    # Проверка возврата списка компетенций с заданными параметрами(позитивный)
    def test_get_competences(client, app):
        functions.add_few_data()

        disciplines = [
            Discipline(name="Математика",
                       year_approved="2019",
                       year_cancelled=None,
                       block_id=1,
                       module_id=1,
                       department_id=1),
            Discipline(name="Информатика",
                       year_approved="2020",
                       year_cancelled=None,
                       block_id=1,
                       module_id=1,
                       department_id=1),
            Discipline(name="Third",
                       year_approved="2024",
                       year_cancelled=None,
                       block_id=1,
                       module_id=1,
                       department_id=1)
        ]

        year = 2022

        direction = Direction(name="Программирование", code="2")
        extra_direction = Direction(name="FSFAF", code="1")
        db.session.add(direction)
        db.session.add(extra_direction)
        db.session.add_all(disciplines)
        db.session.commit()

        directionDisciplines = [
            DirectionDiscipline(discipline_id=disciplines[0].id,
                                direction_id=direction.id,
                                year_created=year),
            DirectionDiscipline(discipline_id=disciplines[1].id,
                                direction_id=direction.id,
                                year_created=year),
            DirectionDiscipline(discipline_id=disciplines[2].id,
                                direction_id=extra_direction.id,
                                year_created=year)
        ]

        db.session.add_all(directionDisciplines)
        db.session.commit()

        competence = Competence(name="УК1.1",
                                year_approved=2016,
                                year_cancelled=2024,
                                type='Вид компетенции',
                                formulation='Формулировка компетенции УК1.1')
        db.session.add(competence)
        db.session.commit()

        competence_disciplines = [
            CompetenceDiscipline(competence_id=competence.id,
                                 discipline_id=disciplines[0].id,
                                 year_created=year),
            CompetenceDiscipline(competence_id=competence.id,
                                 discipline_id=disciplines[2].id,
                                 year_created=year)
        ]
        db.session.add_all(competence_disciplines)
        db.session.commit()

        got_competences = moduleDB.get_competences(direction=direction,
                                                   year=year)

        assert competence in got_competences

    # Проверка возврата списка компетенций с заданными параметрами (негативный)
    # Failed: DID NOT RAISE <class 'ValueError'> date = "16:05:2024"
    # Возвращает AttributeError
    def test_get_competences_negative(client, app):
        with pytest.raises(ValueError) as er:
            moduleDB.get_competences(direction="Информатика",
                                     year="2023")
        assert er.type is ValueError

    # Проверка успешного добавления компетенции
    def test_add_competence(client, app):
        name = "ОПК-1"
        year = "2024"
        type = "ОПК"
        formulation = "Способность решать задачи..."
        competence_params = [
            name,
            year,
            type,
            formulation
        ]

        moduleDB.add_competence(competence_params=competence_params)

        competence = Competence.query.first()

        assert all([
            competence.name == name,
            competence.year_approved == int(year),
            competence.type == type,
            competence.formulation == formulation
        ])

    # Проверка обработки пустых входных данных
    # IndexError: list index out of range date = "17:05:2024"
    # Не та ошибка
    def test_add_competence_negative(client, app):
        competence_params = []
        with pytest.raises(ValueError) as er:
            moduleDB.add_competence(competence_params=competence_params)
        assert er.type is ValueError


class TestClassBlock:

    # Проверка возврата списка всех блоков
    def test_get_block(client, app):
        functions.add_few_data()
        blocks = [
            "Б1.Б",
            "Б1.В.ВД",
            "Б1.В.ОД",
            "Б2",
            "Б2.В",
            "Б2.Б",
            "Б3.Б",
        ]

        assert all([a.name in blocks and type(a) is Block for a in moduleDB.get_block()])  # noqa E501


class TestClassModule():
    # Проверка возврата списка всех модулей
    def test_get_modules(client, app):
        functions.add_few_data()
        modules = [
            "Гуманитарные и социально-экономические дисциплины",
            "Физическая культура и безопасность жизнедеятельности",
            "Математические и естественнонаучные дисциплины",
            "Программное обеспечение",
            "Программирование",
            "Информационные технологии",
            "Разработка информационных систем"
        ]
        assert all([a.name in modules and type(a) is Module for a in moduleDB.get_modules()])  # noqa E501


class TestClassDepartment():
    # Проверка возврата списка всех кафедр
    def test_get_department(client, app):
        functions.add_few_data()
        departments = [
            "ИМО",
            "ПМиК",
            "ГиТ",
            "МА",
            "ТВиАД",
            "ТМОМИ"
        ]
        assert all([a.name in departments and type(a) is Department for a in moduleDB.get_departments()])  # noqa E501


class TestClassDirection():
    # Проверка возврата списка всех направлений
    def test_get_directions(client, app):
        directions = [
            Direction(name="Информационные системы и технологии",
                      code="09.03.02"),
            Direction(name="Программная инженерия", code="sdadsafas")
        ]
        db.session.add_all(directions)
        db.session.commit()

        assert all([a in directions for a in moduleDB.get_directions()])  # noqa E501
