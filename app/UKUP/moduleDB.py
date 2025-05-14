from app.models import db, Block, Module, Department, Direction, Discipline, Competence, CompetenceDiscipline, Indicator, IndicatorDiscipline, RequiredDiscipline, ZE
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
    direction = db.session.get(Direction, direction_id)
    if direction is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(direction_id))
    return direction


# Получает дисциплину по её идентификатору
def get_discipline_by_id(discipline_id):
    discipline = db.session.get(Discipline, discipline_id)
    if discipline is None:
        raise ValueError("Дисциплина с идентификатором {} не найдена".format(discipline_id))
    return discipline


# Получает компетенцию по её идентификатору
def get_competence_by_id(competence_id):
    competence = db.session.get(Competence, competence_id)
    if competence is None:
        raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))
    return competence


# Возвращает список дисциплин с указанными параметрами, а также информацией о модуле, блоке, кафедре и направлении.
def get_disciplines(directionID, year):
    direction = db.session.get(Direction, directionID)
    if direction is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(directionID))
    # Запрос дисциплин с учетом направления и года
    disciplines = Discipline.query \
        .filter(Discipline.direction_id == directionID) \
        .filter(Discipline.year_approved == year) \
        .order_by(Discipline.module_id) \
        .all()
    return disciplines


# Возвращает список необходимых(базовых) дисциплин.
def get_required_disciplines(directionID, year, current_discipline_id):
    direction = db.session.get(Direction, directionID)
    if direction is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(directionID))
    # Запрос дисциплин с учетом направления и года
    disciplines = Discipline.query \
        .filter(Discipline.direction_id == directionID) \
        .filter(Discipline.year_approved == year) \
        .filter(Discipline.id != current_discipline_id) \
        .order_by(Discipline.module_id) \
        .all()
    return disciplines


# Возвращает необходимую(базовую) дисциплину для дисциплины по её идентификатору.
def get_required_discipline(discipline_id): 
    discipline = Discipline.query \
        .join(RequiredDiscipline, Discipline.id == RequiredDiscipline.required_discipline_id) \
        .filter(RequiredDiscipline.dependent_discipline_id == discipline_id) \
        .first()
    return discipline

# Возвращает список зависимых дисциплин для дисциплины по её идентификатору.
def get_dependent_disciplines(discipline_id): 
    disciplines = Discipline.query \
        .join(RequiredDiscipline, Discipline.id == RequiredDiscipline.dependent_discipline_id) \
        .filter(RequiredDiscipline.required_discipline_id == discipline_id) \
        .all()
    return disciplines


# Функция удаления дисциплины
def delete_discipline(id_discipline):
    # Находим дисциплину по ее идентификатору
    discipline = db.session.query(Discipline).get(id_discipline)

    if discipline is None:
        raise ValueError("Дисциплина с идентификатором {} не найдена".format(id_discipline))

    # Удаляем связанные записи в таблице indicator_disciplines
    IndicatorDiscipline.query.filter_by(discipline_id=id_discipline).delete()

    # Удаляем связанные записи в таблице competence_disciplines
    CompetenceDiscipline.query.filter_by(discipline_id=id_discipline).delete()

    # Удаляем связанные необходимые дисциплины
    RequiredDiscipline.query.filter_by(dependent_discipline_id=id_discipline).delete()

    # Удаляем связанные зависимые дисциплины
    RequiredDiscipline.query.filter_by(required_discipline_id=id_discipline).delete()

    ZE.query.filter_by(discipline_id = id_discipline).delete()

    # Удаляем дисциплину
    db.session.delete(discipline)

    # Применяем изменения
    db.session.commit()


# Функция для добавления новой дисциплины в базу данных
def add_discipline(discipline_params, direction, required_discipline_id):

    new_discipline = Discipline(name=discipline_params[0],
                                year_approved=discipline_params[1],
                                block_id=discipline_params[2],
                                module_id=discipline_params[3],
                                department_id=discipline_params[4],
                                direction_id=direction)
    
    db.session.add(new_discipline)
    db.session.commit()

    required_discipline = RequiredDiscipline(required_discipline_id=required_discipline_id,
                                              dependent_discipline_id=new_discipline.id)
    db.session.add(required_discipline)

    ze = ZE(discipline_id=new_discipline.id, 
            c1=0, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0, c8=0, ze=0)
    db.session.add(ze)

    db.session.commit()


def edit_discipline(id_discipline, discipline_params, direction, required_discipline_id):
    # Находим дисциплину по ее идентификатору
    discipline = db.session.get(Discipline, id_discipline)
    if discipline is None:
        raise ValueError("Дисциплина с идентификатором {} не найдена".format(id_discipline))
    if discipline:
        # Обновляем данные дисциплины
        discipline.name = discipline_params[0]

        discipline.block_id = discipline_params[2]
        discipline.module_id = discipline_params[3]
        discipline.department_id = discipline_params[4]
        discipline.direction_id = direction

        if discipline.year_approved == int(discipline_params[1]):

            required_id = -1
            required_discipline = get_required_discipline(id_discipline)
            if not required_discipline is None:
                required_id = required_discipline.id
            required_discipline_id = int(required_discipline_id)

            # Сравниваем id текущей необходимой дисциплины и полученной 
            if required_id != required_discipline_id:
                #print(type(required_discipline_id))
                if required_discipline_id == -1:
                    # Удаляем связанные необходимые дисциплины
                    RequiredDiscipline.query.filter_by(dependent_discipline_id=id_discipline).delete()
                else:
                    # Ищем необходимую дисциплину
                    required = RequiredDiscipline.query.filter_by(dependent_discipline_id=id_discipline).first()
                    # Если она отсутствует, то создаем
                    if required is None:
                        required = RequiredDiscipline()
                        required.dependent_discipline_id = id_discipline
                    required.required_discipline_id = required_discipline_id
                    db.session.add(required)

        if discipline.year_approved != int(discipline_params[1]):

            # Удаляем связи компетенции-дисциплины
            CompetenceDiscipline.query.filter_by(discipline_id=id_discipline).delete()

            # Удаляем связи индикаторы-дисциплины
            IndicatorDiscipline.query.filter_by(discipline_id=id_discipline).delete()

            # Удаляем связанные необходимые дисциплины
            RequiredDiscipline.query.filter_by(dependent_discipline_id=id_discipline).delete()

            # Удаляем связанные зависимые дисциплины
            RequiredDiscipline.query.filter_by(required_discipline_id=id_discipline).delete()

            discipline.year_approved = discipline_params[1]
    db.session.commit()


# Возвращает список компетенций с указанными параметрами
def get_competences(direction, year):
    direction_n = db.session.get(Direction, direction)
    if direction_n is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(direction))
    competences = Competence.query \
        .filter_by(direction_id=direction) \
        .filter_by(year_approved=year) \
        .order_by(Competence.type.desc()).order_by(Competence.name).all()
    return competences


# Функция для добавления новой компетенции в базу данных
def add_competence(competence_params, indicators_list):
    # Разделяем параметры компетенции
    name, year_approved, competence_type, formulation, direction_ids, source = competence_params

    if source.strip() == "":
        source = None
    # Создаем компетенцию для каждого направления
    for direction_id in direction_ids:
        direction_n = db.session.get(Direction, direction_id)
        if direction_n is None:
            raise ValueError("Направление с идентификатором {} не найдено".format(direction_id))
        new_competence = Competence(name=name,
                                    year_approved=year_approved,
                                    type=competence_type,
                                    formulation=formulation,
                                    direction_id=direction_id,
                                    source=source)
        # Добавляем компетенцию в базу данных
        db.session.add(new_competence)
        db.session.commit()

        for indicator_params in indicators_list:
            indicator_id = indicator_params[0]
            indicator_name = indicator_params[1]
            indicator_formulation = indicator_params[2]

            if indicator_id == 'None':
                indicator = Indicator(name=indicator_name, formulation=indicator_formulation, competence_id=new_competence.id)
                db.session.add(indicator)

    # Применяем изменения
    db.session.commit()


# Функция привязки дисциплины к компетенциям
def update_discipline_competences(discipline_id, competence_ids, direction_id):
    discipline = db.session.get(Discipline, discipline_id)
    if discipline is None:
        raise ValueError("Дисциплина с идентификатором {} не найдена".format(discipline_id))
    existing_links = CompetenceDiscipline.query.filter_by(discipline_id=discipline_id).join(Competence) \
        .filter(Competence.direction_id == direction_id) \
        .all()
    existing_competence_ids = {link.competence_id for link in existing_links}

    # Ищем компетенции, которые нужно добавить
    competence_ids_to_add = set(competence_ids) - existing_competence_ids
    for competence_id in competence_ids_to_add:
        competence = db.session.get(Competence, competence_id)
        if competence is None:
            raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))
        new_link = CompetenceDiscipline(discipline_id=discipline_id, competence_id=int(competence_id))
        db.session.add(new_link)

    # Ищем компетенции, которые нужно удалить
    competence_ids_to_remove = existing_competence_ids - set(competence_ids)
    for link in existing_links:
        if link.competence_id in competence_ids_to_remove:
            db.session.delete(link)

    db.session.commit()


def get_indicators_for_discipline(discipline_id, competence_ids):
    # Получаем индикаторы для компетенций, привязанных к дисциплине
    discipline = db.session.get(Discipline, discipline_id)
    if discipline is None:
        raise ValueError("Дисциплина с идентификатором {} не найдена".format(discipline_id))

    for competence_id in competence_ids:
        competence = db.session.get(Competence, competence_id)
        if competence is None:
            raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))

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
    discipline = db.session.get(Discipline, discipline_id)
    if discipline is None:
        raise ValueError("Дисциплина с идентификатором {} не найдена".format(discipline_id))

    for competence_id in competence_ids:
        competence = db.session.get(Competence, competence_id)
        if competence is None:
            raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))


    # Получаем все индикаторы для переданных компетенций
    relevant_indicators = Indicator.query\
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
    if competence is None:
        raise ValueError("Компетенция с идентификатором {} не найдена".format(id_competence))


    # Удаляем все связи с дисциплинами для этой компетенции
    CompetenceDiscipline.query.filter_by(competence_id=id_competence).delete()

    # Находим все связи с индикаторами для этой компетенции
    indicator_links = IndicatorDiscipline.query \
        .join(Indicator, Indicator.id == IndicatorDiscipline.indicator_id) \
        .filter(Indicator.competence_id == id_competence) \
        .all()

    indicators = Indicator.query.filter(Indicator.competence_id == id_competence).all()

    # Удаляем все связи с индикаторами и дисциплинами для этой компетенции
    for link in indicator_links:
        db.session.delete(link)

    for indicator in indicators:
        db.session.delete(indicator)

    # Удаляем саму компетенцию
    db.session.delete(competence)
    db.session.commit()


# Функция редактирования компетенций
def edit_competence(id_competence, competence_params, indicators_list):
    # Находим компетенцию по ее идентификатору
    competence = db.session.get(Competence, id_competence)
    if competence is None:
        raise ValueError("Компетенция с идентификатором {} не найдена".format(id_competence))

    # Проверяем, совпадает ли год у компетенции и переданных параметров
    if competence.year_approved == int(competence_params[3]):
        # Обновляем параметры компетенции
        competence.name = competence_params[0]
        #competence.type = competence_params[1]
        competence.formulation = competence_params[2]
        if competence_params[4].strip() == "":
            competence_params[4] = None
        competence.source = competence_params[4]

        # Список индикаторов, которые уже связаны с этой компетенцией
        existing_indicator_ids = {indicator.id for indicator in competence.indicators}
        #print(existing_indicator_ids)

        # Создаем новые индикаторы и добавляем их к компетенции
        for indicator_params in indicators_list:
            indicator_id = indicator_params[0]
            indicator_name = indicator_params[1]
            indicator_formulation = indicator_params[2]

            # Если передан None в качестве идентификатора, создаем новый индикатор
            if indicator_id == 'None':
                indicator = Indicator(name=indicator_name, formulation=indicator_formulation, competence_id=id_competence)
                db.session.add(indicator)

            # Если индикатор уже существует, обновляем его параметры
            elif int(indicator_id) in existing_indicator_ids:
                indicator = db.session.get(Indicator, int(indicator_id))
                indicator.name = indicator_name
                indicator.formulation = indicator_formulation

        # Удаляем индикаторы, которых больше нет в списке indicators_list
        for indicator in competence.indicators:
            if indicator.id not in [int(indicator_params[0]) for indicator_params in indicators_list if indicator_params[0] != 'None']:

                # Удаляем связи индикатора с дисциплинами
                IndicatorDiscipline.query.filter_by(indicator_id=indicator.id).delete()

                # Удаляем сам индикатор
                db.session.delete(indicator)

        db.session.commit()


    elif competence.year_approved != int(competence_params[3]):
        # Удаляем связи с дисциплинами для этой компетенции
        CompetenceDiscipline.query.filter_by(competence_id=id_competence).delete()

        # Получаем все связи с индикаторами для этой компетенции
        indicator_links = IndicatorDiscipline.query \
            .join(Indicator, Indicator.id == IndicatorDiscipline.indicator_id)\
            .filter(Indicator.competence_id == id_competence) \
            .all()

        # Удаляем все связи с индикаторами для этой компетенции
        for link in indicator_links:
            db.session.delete(link)
        # Обновляем параметры компетенции
        competence.name = competence_params[0]
        #competence.type = competence_params[1]
        competence.formulation = competence_params[2]
        if competence_params[4].strip() == "":
            competence_params[4] = None
        competence.source = competence_params[4]

        # Список индикаторов, которые уже связаны с этой компетенцией
        existing_indicator_ids = {indicator.id for indicator in competence.indicators}

        # Создаем новые индикаторы и добавляем их к компетенции
        for indicator_params in indicators_list:
            indicator_id = indicator_params[0]
            indicator_name = indicator_params[1]
            indicator_formulation = indicator_params[2]
            

            # Если передан None в качестве идентификатора, создаем новый индикатор
            if indicator_id == 'None':
                indicator = Indicator(name=indicator_name, formulation=indicator_formulation, competence_id=id_competence)
                db.session.add(indicator)
            # Если индикатор уже существует, обновляем его параметры
            elif indicator_id in existing_indicator_ids:
                indicator = db.session.query(Indicator).get(indicator_id)
                indicator.name = indicator_name
                indicator.formulation = indicator_formulation

        # Удаляем индикаторы, которых больше нет в списке indicators_list
        for indicator in competence.indicators:
            if indicator.id not in [int(indicator_params[0]) for indicator_params in indicators_list if indicator_params[0] != 'None']:
                # Удаляем связи индикатора с дисциплинами
                IndicatorDiscipline.query.filter_by(indicator_id=indicator.id).delete()
                # Удаляем сам индикатор
                db.session.delete(indicator)
    competence.year_approved = competence_params[3]
    db.session.commit()


# Функция для получения дисциплин и списка связей компетенции
def get_disciplines_and_links_by_competence_id(competence_id):
    # Получаем информацию о компетенции
    competence = db.session.get(Competence, competence_id)
    if competence is None:
        raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))

    # Получаем направление и год компетенции
    direction_id = competence.direction_id
    year_approved = competence.year_approved
    # Получаем список дисциплин с таким же годом и направлением, что и у компетенции
    related_disciplines = get_disciplines(direction_id, year_approved)

    # Получаем список связей компетенция-дисциплина для данной компетенции
    competence_discipline_links = db.session.query(CompetenceDiscipline) \
        .filter_by(competence_id=competence_id) \
        .all()

    return related_disciplines, competence_discipline_links


# Функция получения индикаторов, дисциплин и связей между ними для определенной компетенции
def get_indicators_disciplines_links_by_competence_id(competence_id):

    competence = db.session.get(Competence, competence_id)
    if competence is None:
        raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))

    # Получаем список индикаторов, связанных с компетенцией
    indicators = db.session.query(Indicator)\
                           .filter(Indicator.competence_id == competence_id)\
                           .all()

    # Получаем список дисциплин, связанных с этой компетенцией
    disciplines = db.session.query(Discipline)\
                            .join(CompetenceDiscipline, Discipline.id == CompetenceDiscipline.discipline_id)\
                            .filter(CompetenceDiscipline.competence_id == competence_id)\
                            .all()

    # Получаем список связей дисциплин и индикаторов
    links = db.session.query(IndicatorDiscipline)\
                      .join(Indicator, IndicatorDiscipline.indicator_id == Indicator.id)\
                      .filter_by(competence_id=competence_id)\
                      .all()

    return indicators, disciplines, links


# Функция обновления связи компетенция-дисциплины
def update_competence_disciplines(competence_id, discipline_ids):
    competence = db.session.get(Competence, competence_id)
    if competence is None:
        raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))

    for discipline_id in discipline_ids:
        discipline = db.session.get(Discipline, discipline_id)
        if discipline is None:
            raise ValueError("Дисциплина с идентификатором {} не найдена".format(discipline_id))
    # Получаем текущие записи в таблице competence_disciplines для данной компетенции
    current_disciplines = CompetenceDiscipline.query.filter_by(competence_id=competence_id).all()

    # Составляем список ID дисциплин, которые уже привязаны к компетенции
    current_discipline_ids = [cd.discipline_id for cd in current_disciplines]

    # Удаляем записи, которые нужно удалить
    for discipline_id in current_discipline_ids:
        if discipline_id not in discipline_ids:
            CompetenceDiscipline.query.filter_by(competence_id=competence_id, discipline_id=int(discipline_id)).delete()

    # Добавляем новые записи, если их еще нет
    for discipline_id in discipline_ids:
        if discipline_id not in current_discipline_ids:
            new_link = CompetenceDiscipline(competence_id=competence_id, discipline_id=int(discipline_id))
            db.session.add(new_link)

    # Применяем изменения
    db.session.commit()
             


# Функция обновления связи индикаторы-дисциплины
def update_indicator_disciplines(indicator_discipline_pairs):
    for indicator_id, discipline_ids in indicator_discipline_pairs:

        indicator = db.session.get(Indicator, indicator_id)
        if indicator is None:
            raise ValueError("Индикатор с идентификатором {} не найден".format(indicator_id))

        # Получаем текущие записи в таблице indicator_disciplines для данного индикатора
        current_disciplines = IndicatorDiscipline.query.filter_by(indicator_id=indicator_id).all()

        # Составляем список ID дисциплин, которые уже привязаны к данному индикатору
        current_discipline_ids = [cd.discipline_id for cd in current_disciplines]

        # Удаляем записи, которые нужно удалить
        for discipline_id in current_discipline_ids:
            discipline = db.session.get(Discipline, discipline_id)
            if discipline is None:
                raise ValueError("Дисциплина с идентификатором {} не найдена".format(discipline_id))
            if discipline_id not in discipline_ids:
                IndicatorDiscipline.query.filter_by(indicator_id=indicator_id, discipline_id=discipline_id).delete()

        # Добавляем новые записи, если их еще нет
        for discipline_id in discipline_ids:
            if discipline_id not in current_discipline_ids:
                new_link = IndicatorDiscipline(indicator_id=indicator_id, discipline_id=discipline_id)
                db.session.add(new_link)

    # Применяем изменения
    db.session.commit()


# Функция удаления связи дисциплины и компетенции по id связи
def delete_connection(connection_id):
    connection = CompetenceDiscipline.query.filter_by(id=connection_id).first()
    if connection:
        db.session.delete(connection)
        db.session.commit()
        return True
    else:
        return False


# Функция получения компетенций, привязанных к дисциплине
def get_connected_competences(discipline_id, direction_id, year):
    connected_competences = Competence.query \
        .join(CompetenceDiscipline, CompetenceDiscipline.competence_id == Competence.id) \
        .filter(CompetenceDiscipline.discipline_id == discipline_id) \
        .filter(Competence.direction_id == direction_id) \
        .filter(Competence.year_approved == year) \
        .all()
    return connected_competences


# Функция получения всех компетенций по году
def get_competences_by_year(year):
    return Competence.query \
        .filter(Competence.year_approved <= year) \
        .filter((Competence.year_cancelled > year) | (Competence.year_cancelled == None)) \
        .all()


def get_ze(directionID, year):

    direction = db.session.get(Direction, directionID)
    if direction is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(directionID))
    
    # Запрос зачетных единиц с учетом направления и года
    ze = ZE.query \
        .join(Discipline, ZE.discipline_id == Discipline.id) \
        .filter(Discipline.direction_id == directionID) \
        .filter(Discipline.year_approved == year) \
        .order_by(Discipline.module_id) \
        .all()
    return ze


def update_ze(dict):
    for id, subdict in dict.items():
        ze = ZE.query.filter_by(discipline_id=id).first()
        ze.c1 = subdict[1]
        ze.c2 = subdict[2]
        ze.c3 = subdict[3]
        ze.c4 = subdict[4]
        ze.c5 = subdict[5]
        ze.c6 = subdict[6]
        ze.c7 = subdict[7]
        ze.c8 = subdict[8]
        ze.ze = subdict["ze"]
    db.session.commit()


# Функция для генерации отчета матрицы
def report_matrix(directionID, year):
    direction = db.session.get(Direction, directionID)
    if direction is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(directionID))
    disciplines = Discipline.query\
        .filter_by(direction_id=directionID) \
        .filter_by(year_approved=year) \
        .order_by(Discipline.block_id).all()

    # Получаем все компетенции этого года и направления
    competences = get_competences(directionID, year)

    # Получаем все связи дисциплин и компетенций за выбранный год
    discipline_competence_links = CompetenceDiscipline.query \
        .filter(CompetenceDiscipline.discipline_id.in_([d.id for d in disciplines])) \
        .all()

    return disciplines, competences, discipline_competence_links


# Функция для генерации отчета компетенций
def get_competences_and_indicators(direction_id, year):
    direction = db.session.get(Direction, direction_id)
    if direction is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(direction_id))
    # Получаем список компетенций для данного направления и года
    competences = Competence.query \
        .filter_by(direction_id=direction_id) \
        .filter_by(year_approved=year) \
        .all()

    # Создаем список для компетенций
    competences_list = []

    # Создаем список для индикаторов
    indicators_list = []

    # Для каждой компетенции получаем список ее индикаторов
    for competence in competences:
        competences_list.append(competence)
        indicators = Indicator.query \
            .filter_by(competence_id=competence.id) \
            .all()
        indicators_list.append(indicators)

    return competences_list, indicators_list


# Получает список дисциплин, привязанных к компетенции по её идентификатору.
def get_disciplines_by_competence_id(competence_id):
    # Находим объект компетенции по её идентификатору
    competence = db.session.get(Competence, competence_id)
    if competence is None:
        raise ValueError("Компетенция с идентификатором {} не найдена".format(competence_id))
    if competence:
        # Получаем список компетенций для данной дисциплины
        disciplines = [cd.discipline for cd in competence.competence_disciplines]
        return disciplines
    else:
        # Если компетенция с указанным идентификатором не найдена, возвращаем пустой список
        return []


# Функция возвращает компетенции определенного типа
def get_competences_and_indicators_type(direction_id, year, competence_type):
    direction = db.session.get(Direction, direction_id)
    #print(type(competence_type))
    if direction is None:
        raise ValueError("Направление с идентификатором {} не найдено".format(direction_id))
    # Получаем все компетенции для данного направления, указанного года и типа
    competences = Competence.query \
        .filter_by(direction_id=direction.id) \
        .filter_by(year_approved=year) \
        .filter_by(type=competence_type) \
        .all()


    # Получаем все индикаторы для этих компетенций
    #indicator_ids = [indicator.id for competence in competences for indicator in competence.indicators]
    #indicators = Indicator.query \
    #    .filter(Indicator.id.in_(indicator_ids)) \
    #    .all()
    indicators_list = []
    for competence in competences:
        indicators = Indicator.query \
            .filter_by(competence_id=competence.id) \
            .all()
        indicators_list.append(indicators)

    return competences, indicators_list




def update_data():
    disciplines = Discipline.query.all()
    for discipline in disciplines:
        ze = ZE.query.filter(ZE.discipline_id == discipline.id).one_or_none()
        if ze is None:
            ze = ZE(discipline_id=discipline.id, c1=0, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0, c8=0, ze=0)
            db.session.add(ze)
    db.session.commit()


def get_unique_discipline():
    discipline_names = db.session.query(Discipline.name).distinct().all()
    discipline_names = [name for (name,) in discipline_names]
    return (discipline_names)

