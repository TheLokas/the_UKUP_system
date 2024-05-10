from app.models import Block, Module, Department, Direction, Discipline, Competence, DirectionDiscipline


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






