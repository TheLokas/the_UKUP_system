from app.models import db, Block, Module, Department, Direction, Discipline, Competence, DirectionDiscipline, CompetenceDiscipline


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


#Возвращает список дисциплин с указанными параметрами, а также информацией о модуле, блоке, кафедре и направлении.
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


#Возвращает список компетенций с указанными параметрами
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


#Функция для добавления новой дисциплины в базу данных
def add_discipline(discipline):
    new_discipline = Discipline(name=discipline[0],
                                year_approved=discipline[1],
                                year_cancelled=None,
                                block_id=discipline[2],
                                module_id=discipline[3],
                                department_id=discipline[4])
    db.session.add(new_discipline)
    db.session.commit()

    direction_to_discipline = DirectionDiscipline(discipline_id=new_discipline.id,
                                                  direction_id=discipline[5],
                                                  year_created=discipline[1],
                                                  year_removed=None)
    db.session.add(direction_to_discipline)
    db.session.commit()


#Функция для добавления новой компетенции в базу данных
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


def edit_competence(id_competence, competence_params):
    # Находим компетенцию по ее идентификатору
    competence = db.session.get(Competence, id_competence)

    if competence:
        # Обновляем данные компетенции
        competence.name = competence_params[0]
        competence.year_approved = competence_params[1]
        competence.type = competence_params[2]
        competence.formulation = competence_params[3]

        # Сохраняем изменения в базе данных
        db.session.commit()


def edit_discipline(id_discipline, discipline_params):
    # Находим дисциплину по ее идентификатору
    discipline = db.session.get(Discipline, id_discipline)

    if discipline:
        # Обновляем данные дисциплины
        discipline.name = discipline_params[0]
        discipline.year_approved = discipline_params[1]
        discipline.block_id = discipline_params[2]
        discipline.module_id = discipline_params[3]
        discipline.department_id = discipline_params[4]

        # Обновляем данные связи между дисциплиной и направлением
        direction_to_discipline = DirectionDiscipline.query.filter_by(discipline_id=id_discipline).first()
        if direction_to_discipline:
            direction_to_discipline.direction_id = discipline_params[5]
            direction_to_discipline.year_created = discipline_params[1]

        # Сохраняем изменения в базе данных
        db.session.commit()


#Функция для получения компетенций, привязанных к дисциплине
def get_connected_competences(discipline_id):
    connected_competences = Competence.query.join(CompetenceDiscipline, CompetenceDiscipline.competence_id == Competence.id)\
                                            .filter(CompetenceDiscipline.discipline_id == discipline_id)\
                                            .all()
    return connected_competences





