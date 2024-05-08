from app.models import Block, Module


# Получаем все блоки из базы данных
def get_block():
    blocks = Block.query.all()
    return blocks


# Получаем все модули из базы данных
def get_modules():
    modules = Module.query.all()
    return modules



