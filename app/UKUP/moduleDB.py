from app.models import db, Block, Module, Department, Direction, Discipline, Competence, DirectionDiscipline, CompetenceDiscipline, Indicator, IndicatorDiscipline
from sqlalchemy import and_


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


# Получает направление по его идентификатору
def get_direction_by_id(direction_id):
    return db.session.get(Direction, direction_id)


# Получает дисциплину по её идентификатору
def get_discipline_by_id(discipline_id):
    return db.session.get(Discipline, discipline_id)


# Получает компетенцию по её идентификатору
def get_competence_by_id(competence_id):
    return db.session.get(Competence, competence_id)


# Возвращает список дисциплин с указанными параметрами, а также информацией о модуле, блоке, кафедре и направлении.
def get_disciplines(direction, year):
    disciplines = Discipline.query \
        .join(DirectionDiscipline, Discipline.id == DirectionDiscipline.discipline_id) \
        .filter(DirectionDiscipline.direction_id == direction.id) \
        .filter(Discipline.year_approved == year) \
        .all()
    return disciplines


# Функция удаления дисциплины
def delete_discipline(id_discipline):
    # Находим дисциплину по ее идентификатору
    discipline = db.session.get(Discipline, id_discipline)
    db.session.delete(discipline)
    db.session.commit()


# Функция для добавления новой дисциплины в базу данных
def add_discipline(discipline_params, directions_list):
    new_discipline = Discipline(name=discipline_params[0],
                                year_approved=discipline_params[1],
                                block_id=discipline_params[2],
                                module_id=discipline_params[3],
                                department_id=discipline_params[4])
    db.session.add(new_discipline)
    db.session.commit()

    for direction in directions_list:
        direction_to_discipline = DirectionDiscipline(discipline_id=new_discipline.id,
                                                  direction_id=direction)
        db.session.add(direction_to_discipline)
    db.session.commit()


def edit_discipline(id_discipline, discipline_params, directions_list):
    # Находим дисциплину по ее идентификатору
    discipline = db.session.get(Discipline, id_discipline)

    if discipline:
        # Обновляем данные дисциплины
        discipline.name = discipline_params[0]
        discipline.block_id = discipline_params[2]
        discipline.module_id = discipline_params[3]
        discipline.department_id = discipline_params[4]

        if discipline.year_approved == discipline_params[1]:
            # Находим текущие связанные направления дисциплины
            existing_directions = [direction.id for direction in discipline.directions]

            # Определяем направления, которые были удалены
            removed_directions = set(existing_directions) - set(directions_list)

            # Удаляем записи в таблице direction_disciplines, где направления были удалены
            db.session.query(DirectionDiscipline).filter(
                DirectionDiscipline.discipline_id == id_discipline,
                DirectionDiscipline.direction_id.in_(removed_directions)
            ).delete(synchronize_session=False)

            # Добавляем записи в таблицу direction_disciplines, если их нет в базе данных
            for direction_id in directions_list:
                existing_entry = db.session.query(DirectionDiscipline).filter_by(
                    discipline_id=id_discipline, direction_id=direction_id
                ).first()
                if not existing_entry:
                    new_entry = DirectionDiscipline(discipline_id=id_discipline, direction_id=direction_id)
                    db.session.add(new_entry)

            # Находим компетенции, связанные с удаленными направлениями
            competences_to_remove = db.session.query(Competence).join(Direction).filter(
                Direction.id.in_(removed_directions)
            ).all()

            # Удаляем связи компетенции-дисциплины для найденных компетенций
            for competence in competences_to_remove:
                db.session.query(CompetenceDiscipline).filter_by(
                    competence_id=competence.id, discipline_id=id_discipline
                ).delete()

                # Находим индикаторы, связанные с текущей компетенцией и удаляем связи индикатор-дисциплина
                indicators_to_remove = db.session.query(Indicator).join(Competence).filter(
                    Competence.id == competence.id
                ).all()
                for indicator in indicators_to_remove:
                    db.session.query(IndicatorDiscipline).filter_by(
                        indicator_id=indicator.id, discipline_id=id_discipline
                    ).delete()

        if discipline.year_approved != discipline_params[1]:

            removed_directions = [direction.id for direction in discipline.directions]

            # Находим компетенции, связанные с удаленными направлениями
            competences_to_remove = db.session.query(Competence).join(Direction).filter(
                Direction.id.in_(removed_directions)
            ).all()

            # Удаляем связи компетенции-дисциплины для найденных компетенций
            for competence in competences_to_remove:
                db.session.query(CompetenceDiscipline).filter_by(
                    competence_id=competence.id, discipline_id=id_discipline
                ).delete()

                # Находим индикаторы, связанные с текущей компетенцией и удаляем связи индикатор-дисциплина
                indicators_to_remove = db.session.query(Indicator).join(Competence).filter(
                    Competence.id == competence.id
                ).all()
                for indicator in indicators_to_remove:
                    db.session.query(IndicatorDiscipline).filter_by(
                        indicator_id=indicator.id, discipline_id=id_discipline
                    ).delete()
            # Удаляем все записи в таблице direction_disciplines для данной дисциплины
            db.session.query(DirectionDiscipline).filter_by(discipline_id=id_discipline).delete()

            # Добавляем записи в таблицу direction_disciplines, если их нет в базе данных
            for direction_id in directions_list:
                existing_entry = db.session.query(DirectionDiscipline).filter_by(
                            discipline_id=id_discipline, direction_id=direction_id
                        ).first()
                if not existing_entry:
                    new_entry = DirectionDiscipline(discipline_id=id_discipline, direction_id=direction_id)
                    db.session.add(new_entry)
            discipline.year_approved = discipline_params[1]
    db.session.commit()


# Возвращает список компетенций с указанными параметрами
def get_competences(direction, year):
    competences = Competence.query \
        .filter_by(direction_id=direction.id) \
        .filter_by(year_approved=year) \
        .all()
    return competences


# Функция для добавления новой компетенции в базу данных
def add_competence(competence_params):
    new_competence = Competence(name=competence_params[0],
                                year_approved=competence_params[1],
                                type=competence_params[2],
                                formulation=competence_params[3],
                                direction_id=competence_params[4])
    # Добавляем компетенцию в базу данных
    db.session.add(new_competence)
    db.session.flush()
    db.session.commit()


# Функция привязки дисциплины к компетенциям
def update_discipline_competences(discipline_id, competence_ids):
    existing_links = CompetenceDiscipline.query.filter_by(discipline_id=discipline_id).all()
    existing_competence_ids = {link.competence_id for link in existing_links}

    # Ищем компетенции, которые нужно добавить
    competence_ids_to_add = set(competence_ids) - existing_competence_ids
    for competence_id in competence_ids_to_add:
        new_link = CompetenceDiscipline(discipline_id=discipline_id, competence_id=competence_id)
        db.session.add(new_link)

    # Ищем компетенции, которые нужно удалить
    competence_ids_to_remove = existing_competence_ids - set(competence_ids)
    for link in existing_links:
        if link.competence_id in competence_ids_to_remove:
            db.session.delete(link)

    db.session.commit()


def get_indicators_for_discipline(discipline_id, competence_ids):
    # Получаем индикаторы для компетенций, привязанных к дисциплине
    indicators = db.session.query(Indicator).join(Competence, Indicator.competence_id == Competence.id)\
                         .join(CompetenceDiscipline, Competence.id == CompetenceDiscipline.competence_id)\
                         .filter(CompetenceDiscipline.discipline_id == discipline_id)\
                         .filter(Competence.id.in_(competence_ids))\
                         .all()

    # Получаем связи с индикаторами для этой дисциплины
    indicator_links = IndicatorDiscipline.query.filter_by(discipline_id=discipline_id).all()

    return indicators, indicator_links


# Функция создания связи между дисциплиной и индикатором для страницы дисциплин
# Функция получает id дисциплины, id компетенций и id индикаторов, которые теперь привязаны к дисциплине.
def update_discipline_indicators(discipline_id, competence_ids, indicator_ids):
    # Получаем все индикаторы для переданных компетенций
    relevant_indicators = Indicator.query.join(Indicator.competence)\
                                          .filter(Indicator.competence_id.in_(competence_ids))\
                                          .all()

    # Получаем существующие связи индикаторов с дисциплиной для переданных компетенций
    existing_indicator_links = IndicatorDiscipline.query.filter(
        IndicatorDiscipline.discipline_id == discipline_id,
        IndicatorDiscipline.indicator_id.in_([indicator.id for indicator in relevant_indicators])
    ).all()

    existing_indicator_ids = {link.indicator_id for link in existing_indicator_links}

    # Создаем новые связи для переданных индикаторов и дисциплины
    for indicator_id in indicator_ids:
        if indicator_id not in existing_indicator_ids:
            new_link = IndicatorDiscipline(discipline_id=discipline_id, indicator_id=indicator_id)
            db.session.add(new_link)

    # Удаляем связи, которые больше не нужны
    for link in existing_indicator_links:
        if link.indicator_id not in indicator_ids:
            db.session.delete(link)

    db.session.commit()


# Функция удаления компетенции
def delete_competence(id_competence):
    # Находим компетенцию по ее идентификатору
    competence = Competence.query.get(id_competence)

    # Удаляем все связи с дисциплинами для этой компетенции
    CompetenceDiscipline.query.filter_by(competence_id=id_competence).delete()

    # Находим все связи с индикаторами для этой компетенции
    indicator_links = IndicatorDiscipline.query.join(IndicatorDiscipline.indicator) \
        .filter(Indicator.competence_id == id_competence) \
        .all()

    # Удаляем все связи с индикаторами для этой компетенции
    for link in indicator_links:
        db.session.delete(link)

    # Удаляем саму компетенцию
    db.session.delete(competence)
    db.session.commit()


# После этой строчки функции скорее всего не работают


# Функция удаления связи дисциплины и компетенции по id связи
def delete_connection(connection_id):
    connection = CompetenceDiscipline.query.filter_by(id=connection_id).first()
    if connection:
        db.session.delete(connection)
        db.session.commit()
        return True
    else:
        return False


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



# Функция получения компетенций, привязанных к дисциплине
def get_connected_competences(discipline_id):
    connected_competences = Competence.query.join(CompetenceDiscipline, CompetenceDiscipline.competence_id == Competence.id)\
                                            .filter(CompetenceDiscipline.discipline_id == discipline_id)\
                                            .all()
    return connected_competences




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


# Функция получения всех компетенций по году
def get_competences_by_year(year):
    return Competence.query \
        .filter(Competence.year_approved <= year) \
        .filter((Competence.year_cancelled > year) | (Competence.year_cancelled == None)) \
        .all()


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

    # Получаем все компетенции этого года
    competences = get_competences_by_year(year)

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


# Получает список дисциплин, привязанных к компетенции по её идентификатору.
def get_disciplines_by_competence_id(competence_id):
    # Находим объект компетенции по её идентификатору
    competence = db.session.get(Competence, competence_id)

    if competence:
        # Получаем список компетенций для данной дисциплины
        disciplines = [cd.discipline for cd in competence.competence_disciplines]
        return disciplines
    else:
        # Если компетенция с указанным идентификатором не найдена, возвращаем пустой список
        return []


