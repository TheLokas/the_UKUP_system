#!flask/bin/python
from app import app

app.run(debug=True)

# Работа с компетенциями
# http://127.0.0.1:5000/UKUP/competence
# http://127.0.0.1:5000/UKUP/competence/add
#
# Работа с дисциплинами
# http://127.0.0.1:5000/UKUP/discipline
# http://127.0.0.1:5000/UKUP/discipline/add

# Для работы с локальной бд sqlite раскомментить строку в конфиге
# Для заполнения локальной бд тестовыми данными перейти по
# http://127.0.0.1:5000/UKUP/addData
