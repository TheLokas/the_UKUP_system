from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Direction(db.Model):
    __tablename__ = 'directions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    code = db.Column(db.String(50))


class Discipline(db.Model):
    __tablename__ = 'disciplines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    year_approved = db.Column(db.Integer)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    block = db.relationship('Block', backref='disciplines')
    module = db.relationship('Module', backref='disciplines')
    department = db.relationship('Department', backref='disciplines')
    directions = db.relationship('Direction', secondary='direction_disciplines', backref=db.backref('disciplines', lazy='dynamic'))

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Block(db.Model):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Competence(db.Model):
    __tablename__ = 'competences'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    year_approved = db.Column(db.Integer)
    type = db.Column(db.String(100))
    formulation = db.Column(db.String(255))
    direction_id = db.Column(db.Integer, db.ForeignKey('directions.id'))

    direction = db.relationship('Direction', backref='competences')


class Indicator(db.Model):
    __tablename__ = 'indicators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    formulation = db.Column(db.String(255))
    competence_id = db.Column(db.Integer, db.ForeignKey('competences.id'))

    competence = db.relationship('Competence', backref='indicators')


class DirectionDiscipline(db.Model):
    __tablename__ = 'direction_disciplines'
    id = db.Column(db.Integer, primary_key=True)
    discipline_id = db.Column(db.Integer, db.ForeignKey('disciplines.id'))
    direction_id = db.Column(db.Integer, db.ForeignKey('directions.id'))


class CompetenceDiscipline(db.Model):
    __tablename__ = 'competence_disciplines'
    id = db.Column(db.Integer, primary_key=True)
    competence_id = db.Column(db.Integer, db.ForeignKey('competences.id'))
    discipline_id = db.Column(db.Integer, db.ForeignKey('disciplines.id'))


class IndicatorDiscipline(db.Model):
    __tablename__ = 'indicator_disciplines'
    id = db.Column(db.Integer, primary_key=True)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicators.id'))
    discipline_id = db.Column(db.Integer, db.ForeignKey('disciplines.id'))

