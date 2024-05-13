from app.models import db, Block, Module, Department, Direction, Discipline, Competence, DirectionDiscipline, CompetenceDiscipline, Indicator


# Получаем все блоки из базы данных
def get_block():
    blocks = Block.query.all()
    return blocks


# Получаем все модули из базы данных
def get_modules():
    modules = Module.query.all()
    return modules


# Получаем все кафедры из базы данных
def get_departments():
    departments = Department.query.all()
    return departments


# Получаем все направления из базы данных
def get_directions():
    directions = Direction.query.all()
    return directions


# Возвращает список дисциплин с указанными параметрами, а также информацией о модуле, блоке, кафедре и направлении.
def get_disciplines(direction = None, year = None):
    if direction:
        disciplines = Discipline.query \
            .join(DirectionDiscipline, Discipline.id == DirectionDiscipline.discipline_id) \
            .filter(DirectionDiscipline.direction_id == direction.id) \
            .filter(DirectionDiscipline.year_created <= year) \
            .filter((DirectionDiscipline.year_removed > year) | (DirectionDiscipline.year_removed == None)) \
            .all()
    else:
        disciplines = Discipline.query \
            .filter(Discipline.year_approved <= year) \
            .filter((Discipline.year_cancelled > year) | (Discipline.year_cancelled == None)) \
            .all()

    return disciplines


# Возвращает список компетенций с указанными параметрами
def get_competences(direction=None, year=None):
    if direction:
        # Если указано направление, выбираем компетенции с учетом направления и года.
        competences = Competence.query \
            .join(CompetenceDiscipline, Competence.id == CompetenceDiscipline.competence_id) \
            .join(Discipline, CompetenceDiscipline.discipline_id == Discipline.id) \
            .join(DirectionDiscipline, Discipline.id == DirectionDiscipline.discipline_id) \
            .filter(DirectionDiscipline.direction_id == direction.id) \
            .filter(CompetenceDiscipline.year_created <= year) \
            .filter((CompetenceDiscipline.year_removed > year) | (CompetenceDiscipline.year_removed == None)) \
            .all()
    else:
        # Если направление не указано, выбираем все компетенции с учетом года.
        competences = Competence.query \
            .join(CompetenceDiscipline, Competence.id == CompetenceDiscipline.competence_id) \
            .join(Discipline, CompetenceDiscipline.discipline_id == Discipline.id) \
            .filter(Competence.year_approved <= year) \
            .filter((Competence.year_cancelled > year) | (Competence.year_cancelled == None)) \
            .all()

    return competences


# Функция для добавления новой дисциплины в базу данных
def add_discipline(discipline, directions):
    new_discipline = Discipline(name=discipline[0],
                                year_approved=discipline[1],
                                year_cancelled=None,
                                block_id=discipline[2],
                                module_id=discipline[3],
                                department_id=discipline[4])
    db.session.add(new_discipline)
    db.session.commit()

    for direction in directions:
        direction_to_discipline = DirectionDiscipline(discipline_id=new_discipline.id,
                                                  direction_id=direction,
                                                  year_created=discipline[1],
                                                  year_removed=None)
        db.session.add(direction_to_discipline)
    db.session.commit()




# Функция для добавления новой компетенции в базу данных
def add_competence(competence_params):
    new_competence = Competence(name=competence_params[0],
                                year_approved=competence_params[1],
                                type=competence_params[2],
                                year_cancelled=None,
                                formulation=competence_params[3])

    # Добавляем компетенцию в базу данных
    db.session.add(new_competence)
    db.session.flush()
    db.session.commit()


# Функция редактирования компетенций
def edit_competence(id_competence, competence_params):
    # Находим компетенцию по ее идентификатору
    competence = db.session.get(Competence, id_competence)

    if competence:
        # Обновляем данные компетенции
        competence.name = competence_params[0]
        competence.type = competence_params[1]
        competence.formulation = competence_params[2]

        # Сохраняем изменения в базе данных
        db.session.commit()


def edit_discipline(id_discipline, discipline_params, directions):

    # Находим дисциплину по ее идентификатору
    discipline = db.session.get(Discipline, id_discipline)

    if discipline:
        # Обновляем данные дисциплины
        discipline.name = discipline_params[0]
        discipline.year_approved = discipline_params[1]
        discipline.block_id = discipline_params[2]
        discipline.module_id = discipline_params[3]
        discipline.department_id = discipline_params[4]

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Получаем все записи направления-дисциплины для данной дисциплины
        all_directions_for_discipline = DirectionDiscipline.query.filter_by(discipline_id=id_discipline).all()

        for directionID in directions:
            # Проверяем, существует ли запись для данного направления и дисциплины
            direction_discipline = DirectionDiscipline.query.filter_by(discipline_id=id_discipline, direction_id=directionID).first()

            if not direction_discipline:
                # Если записи нет, добавляем новую запись
                new_direction_to_discipline = DirectionDiscipline(
                    discipline_id=id_discipline,
                    direction_id=directionID,
                    year_created=discipline_params[1]
                )
                db.session.add(new_direction_to_discipline)

        # Обновляем все остальные записи в таблице направления-дисциплины для данной дисциплины, устанавливая год удаления
        for direction_to_discipline in all_directions_for_discipline:
            if direction_to_discipline.direction_id not in directions:
                direction_to_discipline.year_removed = discipline_params[1]

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Получаем все записи направления-дисциплины для данной дисциплины
        all_directions_for_discipline = DirectionDiscipline.query.filter_by(discipline_id=id_discipline).all()
        for i in all_directions_for_discipline:
            if i.year_created == i.year_removed:
                db.session.delete(i)
        db.session.commit()



# Функция получения компетенций, привязанных к дисциплине
def get_connected_competences(discipline_id):
    connected_competences = Competence.query.join(CompetenceDiscipline, CompetenceDiscipline.competence_id == Competence.id)\
                                            .filter(CompetenceDiscipline.discipline_id == discipline_id)\
                                            .all()
    return connected_competences



# Функция удаления связи дисциплины и компетенции по id связи
def delete_connection(connection_id):
    connection = CompetenceDiscipline.query.filter_by(id=connection_id).first()
    if connection:
        db.session.delete(connection)
        db.session.commit()
        return True
    else:
        return False


# Функция удаления дисциплины
def delete_discipline(id_discipline, year_cancelled_value):
    # Находим дисциплину по ее идентификатору
    discipline = db.session.get(Discipline, id_discipline)

    if discipline:
        # Устанавливаем год удаления
        discipline.year_cancelled = year_cancelled_value
        # Сохраняем изменения в базе данных
        db.session.commit()

    discipline = db.session.get(Discipline, id_discipline)

    if discipline.year_cancelled == discipline.year_approved:
        db.session.delete(discipline)
        db.session.commit()
        return True

    else:
        return False


# Функция удаления компетенций
def delete_competence(id_competence, year_cancelled_value):
    # Находим компетенцию по ее идентификатору
    competence = db.session.get(Competence, id_competence)

    if competence:
        competence.year_cancelled = year_cancelled_value
        # Сохраняем изменения в базе данных
        db.session.commit()

    competence = db.session.get(Competence, id_competence)

    if competence.year_cancelled == competence.year_approved:
        db.session.delete(competence)
        db.session.commit()
        return True

    else:
        return False


# Функция для генерации отчета матрицы
def report_matrix(direction=None, year=None):
    if direction:
        direction_disciplines = DirectionDiscipline.query \
            .filter_by(direction_id=direction.id) \
            .filter(DirectionDiscipline.year_created <= year) \
            .filter((DirectionDiscipline.year_removed > year) | (DirectionDiscipline.year_removed == None)) \
            .all()
        discipline_ids = [dd.discipline_id for dd in direction_disciplines]
        disciplines = Discipline.query.filter(Discipline.id.in_(discipline_ids)).all()
    else:
        disciplines = Discipline.query \
            .filter(Discipline.year_approved <= year) \
            .filter((Discipline.year_cancelled > year) | (Discipline.year_cancelled == None)) \
            .all()

    # Получаем все компетенции, связанные с дисциплинами
    competence_ids = [cd.competence_id for cd in CompetenceDiscipline.query.filter(CompetenceDiscipline.discipline_id.in_([d.id for d in disciplines])).all()]
    competences = Competence.query \
        .filter(Competence.id.in_(competence_ids)) \
        .filter(CompetenceDiscipline.year_created <= year) \
        .filter((CompetenceDiscipline.year_removed > year) | (CompetenceDiscipline.year_removed == None)) \
        .all()

    # Получаем все связи дисциплин и компетенций за выбранный год
    discipline_competence_links = CompetenceDiscipline.query \
        .filter(CompetenceDiscipline.discipline_id.in_([d.id for d in disciplines])) \
        .filter(CompetenceDiscipline.year_created <= year) \
        .filter((CompetenceDiscipline.year_removed > year) | (CompetenceDiscipline.year_removed == None)) \
        .all()

    return disciplines, competences, discipline_competence_links


# Функция для генерации отчета компетенций
def get_competences_and_indicators(direction, year):
    # Получаем список дисциплин для данного направления и года
    direction_disciplines = DirectionDiscipline.query \
        .filter_by(direction_id=direction.id) \
        .filter(DirectionDiscipline.year_created <= year) \
        .filter((DirectionDiscipline.year_removed > year) | (DirectionDiscipline.year_removed == None)) \
        .all()
    discipline_ids = [dd.discipline_id for dd in direction_disciplines]

    # Получаем все компетенции для этих дисциплин и указанного года
    competence_ids = [cd.competence_id for cd in CompetenceDiscipline.query.filter(CompetenceDiscipline.discipline_id.in_(discipline_ids)).all()]
    competences = Competence.query \
        .filter(Competence.id.in_(competence_ids)) \
        .filter(Competence.year_approved <= year) \
        .filter((Competence.year_cancelled > year) | (Competence.year_cancelled == None)) \
        .all()

    # Получаем все индикаторы для этих компетенций
    indicator_ids = [i.id for competence in competences for i in competence.indicator]
    indicators = Indicator.query \
        .filter(Indicator.id.in_(indicator_ids)) \
        .all()

    return competences, indicators
