

-- Добавление тестовых данных для таблицы Directions
INSERT INTO directions (name, code)
VALUES
('Информационные системы и технологии', '09.03.02'),
('Математика', '01.03.01'),
('Прикладная математика и информатика', '01.03.02'),
('Программная инженерия', '09.03.04'),
('Педагогическое образование', '44.03.05');


-- Добавление тестовых данных для таблицы Modules
INSERT INTO modules (name)
VALUES
('Гуманитарные и социально-экономические дисциплины'),
('Физическая культура и безопасность жизнедеятельности'),
('Математические и естественнонаучные дисциплины'),
('Программное обеспечение'),
('Программирование'),
('Информационные технологии'),
('Разработка информационных систем');


-- Добавление тестовых данных для таблицы Blocks
INSERT INTO blocks (name)
VALUES
('Б1.Б'),
('Б1.В.ВД'),
('Б1.В.ОД'),
('Б2'),
('Б2.В'),
('Б2.Б'),
('Б3.Б');


-- Добавление тестовых данных для таблицы Departments
INSERT INTO departments (name)
VALUES
('ИМО'),
('ПМиК'),
('ГиТ'),
('МА'),
('ТВиАД'),
('ТМОМИ');


-- Добавление тестовых данных для таблицы Competences
INSERT INTO competences (name, year_approved, type, year_cancelled, formulation)
VALUES
('Компетенция 1', 2020, 'Тип 1', NULL, 'Формулировка компетенции 1'),
('Компетенция 2', 2019, 'Тип 2', 2022, 'Формулировка компетенции 2'),
('Компетенция 3', 2021, 'Тип 3', NULL, 'Формулировка компетенции 3');


-- Добавление тестовых данных для таблицы Indicators
INSERT INTO indicators (name, formulation, competence_id)
VALUES
('Индикатор 1', 'Формулировка индикатора 1', 1),
('Индикатор 2', 'Формулировка индикатора 2', 1),
('Индикатор 3', 'Формулировка индикатора 3', 2);


-- Добавление тестовых данных для таблицы Disciplines
INSERT INTO disciplines (name, year_approved, year_cancelled, block_id, module_id, department_id)
VALUES
('Дисциплина 1', 2020, NULL, 1, 1, 1),
('Дисциплина 2', 2019, 2021, 2, 2, 2),
('Дисциплина 3', 2021, NULL, 3, 3, 3);


-- Добавление тестовых данных для таблицы DirectionDisciplines
INSERT INTO direction_disciplines (discipline_id, direction_id, year_created, year_removed)
VALUES
(1, 1, 2020, NULL),
(2, 1, 2019, 2021),
(3, 1, 2021, NULL);


-- Добавление тестовых данных для таблицы CompetenceDisciplines
INSERT INTO competence_disciplines (competence_id, discipline_id, year_created)
VALUES
(1, 1, 2020),
(1, 2, 2019),
(2, 3, 2021);


-- Добавление тестовых данных для таблицы IndicatorDisciplines
INSERT INTO indicator_disciplines (indicator_id, discipline_id, year_created)
VALUES
(1, 1, 2020),
(2, 1, 2020),
(3, 2, 2019);


-- Создание триггера before_competence_delete
CREATE TRIGGER `before_competence_delete` BEFORE DELETE ON `competences`
 FOR EACH ROW BEGIN
    -- Удаление связанных записей в competence_disciplines
    DELETE FROM competence_disciplines WHERE competence_id = OLD.id;

	-- Удаление связанных записей в indicator_disciplines
    DELETE FROM indicator_disciplines WHERE indicator_id IN (SELECT id FROM indicators WHERE competence_id = OLD.id);

    -- Удаление записей из таблицы indicators
    DELETE FROM indicators WHERE competence_id = OLD.id;

END


-- Создание триггера before_discipline_delete
CREATE TRIGGER `before_discipline_delete` BEFORE DELETE ON `disciplines`
 FOR EACH ROW BEGIN
    -- Удаление связанных записей из таблицы direction_disciplines
    DELETE FROM direction_disciplines WHERE discipline_id = OLD.id;

    -- Удаление связанных записей из таблицы competence_disciplines
    DELETE FROM competence_disciplines WHERE discipline_id = OLD.id;

    -- Удаление связанных записей из таблицы indicator_disciplines
    DELETE FROM indicator_disciplines WHERE discipline_id = OLD.id;

END