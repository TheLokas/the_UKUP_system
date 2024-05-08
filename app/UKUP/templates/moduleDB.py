from app.models import Block, Module, Department, Direction


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

