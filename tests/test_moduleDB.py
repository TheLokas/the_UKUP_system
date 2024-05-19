from app.UKUP import moduleDB, functions
from app.models import (Discipline,
                        Direction,
                        DirectionDiscipline,
                        Competence,
                        CompetenceDiscipline,
                        IndicatorDiscipline,
                        Block,
                        Module,
                        Department,
                        Indicator)
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

    # Проверка правильной работы функции получения дисциплин по id
    def test_get_discipline_by_id(client, app):
        disciplines = add_disciplines_data()[0]
        discipline = moduleDB.get_discipline_by_id(1)
        assert discipline == disciplines[0]

    # Проверка обработки неверного ввода функции получения дисциплины по id
    def test_get_discipline_by_id_negative(client, app):
        with pytest.raises(ValueError):
            moduleDB.get_discipline_by_id(1000)

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
        competences = add_competence_data()

        direction = Direction.query.first()

        got_competences = moduleDB.get_competences(direction=direction,
                                                   year=2023)

        assert all([
            competences[0] in got_competences,
            competences[1] in got_competences
        ])

    # Проверка работоспособности функции получения компетенции по id
    def test_get_competence_by_id(client, app):
        competences = add_competence_data()
        competence = moduleDB.get_competence_by_id(competences[0].id)
        assert competences[0] == competence

    # Проверка обработки неверного ввода функции получения компетенции по id
    # Failed: DID NOT RAISE <class 'ValueError'>
    # Date: 18:05:2024
    def test_get_competence_by_id_negative(client, app):
        with pytest.raises(ValueError):
            moduleDB.get_competence_by_id(1000)

    # Проверка возврата списка компетенций с заданными параметрами (негативный)
    def test_get_competences_negative(client, app):
        with pytest.raises(AttributeError) as er:
            moduleDB.get_competences(direction="Информатика",
                                     year="2023")
            assert er.type is AttributeError

    # Проверка успешного добавления компетенции
    def test_add_competence(client, app):
        functions.add_few_data()
        name = "ОПК-1"
        year = "2023"
        type = "ОПК"
        formulation = "Способность решать задачи..."
        direction = Direction.query.first()
        competence_params = [
            name,
            year,
            type,
            formulation,
            [direction.id]
        ]

        moduleDB.add_competence(competence_params=competence_params)

        competence = Competence.query.filter(Competence.direction_id == direction.id).all()  # noqa E501

        bool_states = []
        for comp in competence:
            bool_states.append(comp.name == name)
            bool_states.append(comp.year_approved == int(year))
            bool_states.append(comp.type == type)
            bool_states.append(comp.formulation == formulation)

        assert all(bool_states)

    # Проверка обработки пустых входных данных
    # IndexError: list index out of range date = "17:05:2024"
    # Не та ошибка
    def test_add_competence_negative(client, app):
        competence_params = []
        with pytest.raises(ValueError) as er:
            moduleDB.add_competence(competence_params=competence_params)
            assert er.type is ValueError

    # Проверка корректного удаления компетенции
    def test_delete_competence(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        assert competences[1] in Competence.query.all()
        assert competence_disciplines[1] in CompetenceDiscipline.query.all()
        moduleDB.delete_competence(id_competence=competences[1].id)
        assert competences[1] not in Competence.query.all()
        assert competence_disciplines[1] not in CompetenceDiscipline.query.all()  # noqa E501

    # Проверка успешного редактирования компетенции
    def test_edit_competence(client, app):
        competences = add_competence_data()

        new_year = 2030
        new_name = "УК-100"
        new_type = "УК"
        new_formulation = "...."
        competence_params = [
            new_name,
            new_type,
            new_formulation,
            new_year
        ]
        indicator_params = [
            'None',
            "УК-100.1",
            "..."
        ]
        moduleDB.edit_competence(id_competence=competences[1].id,
                                 competence_params=competence_params,
                                 indicators_list=[indicator_params])

        edited_comp = Competence.query.get(competences[1].id)
        indicators = Indicator.query.all()  # noqa E501

        assert all([
            edited_comp.name == new_name,
            edited_comp.type == new_type,
            edited_comp.year_approved == new_year,
            edited_comp.formulation == new_formulation,
            len(indicators) == 1,
            indicators[0].name == indicator_params[1],
            indicators[0].formulation == indicator_params[2]
        ])

    # Проверка успешного редактирования компетенции
    # Index out of range exception
    # Добавить обработчик
    def test_edit_competence_negative(client, app):
        competences = add_competence_data()

        new_year = "2030"
        new_name = 123
        new_type = "Некорректные данные"
        new_formulation = "...."
        competence_params = [
            new_name,
            new_type,
            new_formulation,
            new_year
        ]
        moduleDB.edit_competence(id_competence=competences[1].id,
                                 competence_params=competence_params,
                                 indicators_list=["11"])

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

    # Проверка работоспособности получения направления по id
    def test_get_directions_by_id(client, app):
        directions = [
            Direction(name="Информационные системы и технологии",
                      code="09.03.02"),
            Direction(name="Программная инженерия", code="sdadsafas")
        ]
        db.session.add_all(directions)
        db.session.commit()

        direction = moduleDB.get_direction_by_id(1)
        assert direction == directions[0]

    # Проверка обработки неверного ввода функции получения направления по id
    # Failed: DID NOT RAISE <class 'ValueError'>
    # date: 18:05:2024
    def test_get_directions_by_id_negative(client, app):
        with pytest.raises(ValueError):
            moduleDB.get_direction_by_id(1000)


class TestClassesLinks():
    # Проверка успешного получения списка индикаторов для дисциплины
    def test_get_indicators_for_discipline(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        discipline_to_get_indicators = disciplines[0].id
        competences_to_get_indicators = [competences[0].id]
        indicators = moduleDB.get_indicators_for_discipline(discipline_to_get_indicators, competences_to_get_indicators)  # noqa E501
        indicators_from_db = Indicator.query.all()
        assert all([
            len(indicators) == 2,
            len(indicators[0]) == 1,
            len(indicators[1]) == 1,
            indicators[0][0] == indicators_from_db[0],
            indicators[1][0] == indicator_disciplines[0]
        ])

    # Проверка обработки
    def test_get_indicators_for_disscipline_negative(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        with pytest.raises(AttributeError):
            moduleDB.get_indicators_for_discipline(None, None)

    # Проверка успешного обновления списка связей дисциплин и компетенций
    # sqlalchemy.exc.ArgumentError
    # Date: 18:05:2024
    # Добавить обработку неверных входных данных
    def test_update_discipline_competences(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        moduleDB.update_discipline_competences(disciplines[0].id,
                                               [competences[0].id,
                                                competences[1].id])
        discipline_zero_comps = CompetenceDiscipline.query\
            .filter(CompetenceDiscipline.discipline_id == disciplines[0].id).all()  # noqa E501
        assert all([
            discipline_zero_comps[0].competence_id == competences[0].id,
            discipline_zero_comps[1].competence_id == competences[1].id,
            len(discipline_zero_comps) == 2
        ])

    # Проверка обработки неверного ввода функции успешного обновления списка связей дисциплин и компетенций # noqa E501
    # Failed: DID NOT RAISE <class 'ValueError'>
    # Решение: добавление обработки неверного ввода
    def test_update_discipline_competences_negative(client, app):
        with pytest.raises(ValueError):
            moduleDB.update_discipline_competences(100, [100, 100])

    # Проверка работоспособности функции получения связанных дисциплин и связей
    def test_get_disciplines_and_links_by_competence_id(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        related_disciplines, competence_disciplines_link = moduleDB.get_disciplines_and_links_by_competence_id(competences[0].id)  # noqa E501
        assert all([
            len(competence_disciplines_link) == 1,
            competence_disciplines_link[0] == competence_disciplines[0],
            len(related_disciplines) == 1,
            related_disciplines[0] == disciplines[0]
        ])

    # Проверка работоспособности функции редактирования индикаторов дисциплины
    def test_update_discipline_indicators(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        moduleDB.update_discipline_indicators(disciplines[0].id,
                                              [competences[0].id,
                                               competences[1].id,
                                               competences[2].id],
                                              [1, 2, 3, 4, 5])
        connected_competences = moduleDB.get_connected_competences(disciplines[0].id) # noqa E501
        conncted_indicators = moduleDB.get_indicators_for_discipline(disciplines[0].id, # noqa E501
                                                                     [competences[0].id,competences[1].id, competences[2].id]) # noqa E501
        assert all(
            [ind.id in [1, 2, 3, 4, 5] for ind in conncted_indicators[0]]
        )

    # Проверка работоспособности функции получения связей дисциплин
    # с индикаторами по id компетенции
    def test_get_indicators_disciplines_links_by_competence_id(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        indicators, dises, ind_disciplines = moduleDB.get_indicators_disciplines_links_by_competence_id(competences[1].id)  # noqa E501
        assert 2 == indicators[0].id
        assert 3 == indicators[1].id
        assert disciplines[1] == dises[0]
        assert indicator_disciplines[1] == ind_disciplines[0]
        assert indicator_disciplines[2] == ind_disciplines[1]

    # Проверка работоспособности функции редактирования компетенций,
    # привязанных к дисциплине
    def test_update_competence_disciplines(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501

        disciplines_ids = [discipline.id for discipline in disciplines]

        competence_id = competences[0].id

        moduleDB.update_competence_disciplines(competence_id=competence_id,
                                               discipline_ids=disciplines_ids)

        # competence_disciplines = moduleDB.get_disciplines_by_competence_id(competence_id) # noqa E501
        competence_disciplines = \
            [c.discipline_id for c in CompetenceDiscipline.query.filter(CompetenceDiscipline.competence_id == competence_id)] # noqa E501
        real_ids_bools = [dis.id in competence_disciplines for dis in disciplines] # noqa E501
        assert all(real_ids_bools, len(real_ids_bools) == 3)

    # Проверка работоспособности функции
    # удаления связи компетенции и дисциплины
    def test_delete_connection(client, app):
        competence_disciplines = add_competence_discipline_links()
        moduleDB.delete_connection(competence_disciplines[1].id)
        assert competence_disciplines[1] not in CompetenceDiscipline.query.all()   # noqa E501

    # Проверка работоспособности функции
    # удаления связи компетенции и дисциплины с неверным входом
    def test_delete_connection_negative(client, app):
        add_competence_discipline_links()
        assert not moduleDB.delete_connection(10000)

    # Проверка работоспособности функции 
    # удаления связи компетенции и дисциплины с неверным типом входа
    def test_delete_connection_negative_bad_input(client, app):
        with pytest.raises(ValueError):
            moduleDB.delete_connection(None)

    # Проверка работоспособности функции получения связанных
    # компетенций для дисциплины
    def test_get_connected_competences(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        conn = CompetenceDiscipline.query\
            .filter(CompetenceDiscipline.discipline_id == disciplines[1].id)\
            .all()
        real_connected = [c.competence_id for c in conn]
        connected = moduleDB.get_connected_competences(disciplines[1].id)
        assert all([c.id in real_connected for c in connected])

    # Проверка работоспособности функции получения связанных
    # компетенций для дисциплины
    def test_get_connected_competences_negative(client, app):
        with pytest.raises(ValueError):
            moduleDB.get_connected_competences("sdad")

    # Проверка работоспособности функции обновления связи индикаторы-дисциплины
    def test_update_indicator_disciplines(client, app):
        competences, disciplines, competence_disciplines, indicator_disciplines = add_all()  # noqa E501
        indicators = Indicator.query.all()
        new_connections = [
            (indicators[0].id, [disciplines[0].id,
                                disciplines[1].id,
                                disciplines[2].id]),
            (indicators[1].id, [disciplines[1].id])
        ]
        moduleDB.update_indicator_disciplines(new_connections)
        disciplines_for_first = Indicator.query\
                                         .filter_by(id=indicators[0].id)\
                                         .all()
        disciplines_for_second = Indicator.query\
                                          .filter_by(id=indicators[1].id)\
                                          .all()
        assert all([dis.id in new_connections[0][1] for dis in disciplines_for_first])  # noqa E501
        assert all([dis.id in new_connections[1][1] for dis in disciplines_for_second])  # noqa E501


# class TestClassReport():
    # Проверка функции получения данных для генерации матрицы компетенций
    # def test_report_matrix(client, app)