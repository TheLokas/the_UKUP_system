from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from . import db


db = SQLAlchemy()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb://root:123qwe@localhost/UKUP_DB'


class Direction(db.Model):
    __tablename__ = 'directions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    code = db.Column(db.String(50))
    disciplines = db.relationship('DirectionDiscipline', backref='direction', lazy='dynamic')


class DirectionDiscipline(db.Model):
    __tablename__ = 'direction_disciplines'
    id = db.Column(db.Integer, primary_key=True)
    discipline_id = db.Column(db.Integer, db.ForeignKey('disciplines.id'))
    direction_id = db.Column(db.Integer, db.ForeignKey('directions.id'))
    year_created = db.Column(db.Integer)
    year_removed = db.Column(db.Integer)


class Discipline(db.Model):
    __tablename__ = 'disciplines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    year_approved = db.Column(db.Integer)
    year_cancelled = db.Column(db.Integer)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    competence_disciplines = db.relationship('CompetenceDiscipline', backref='discipline', lazy='dynamic')
    indicator_disciplines = db.relationship('IndicatorDiscipline', backref='discipline', lazy='dynamic')
    direction = db.relationship('DirectionDiscipline', backref='discipline', lazy='dynamic')


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    disciplines = db.relationship('Discipline', backref='department', lazy='dynamic')


class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    disciplines = db.relationship('Discipline', backref='module', lazy='dynamic')


class Block(db.Model):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    disciplines = db.relationship('Discipline', backref='block', lazy='dynamic')


class CompetenceDiscipline(db.Model):
    __tablename__ = 'competence_disciplines'
    id = db.Column(db.Integer, primary_key=True)
    competence_id = db.Column(db.Integer, db.ForeignKey('competences.id'))
    discipline_id = db.Column(db.Integer, db.ForeignKey('disciplines.id'))
    year_created = db.Column(db.Integer)
    year_removed = db.Column(db.Integer)


class IndicatorDiscipline(db.Model):
    __tablename__ = 'indicator_disciplines'
    id = db.Column(db.Integer, primary_key=True)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicators.id'))
    discipline_id = db.Column(db.Integer, db.ForeignKey('disciplines.id'))
    year_created = db.Column(db.Integer)
    year_removed = db.Column(db.Integer)


class Competence(db.Model):
    __tablename__ = 'competences'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    year_approved = db.Column(db.Integer)
    type = db.Column(db.String(50))
    year_cancelled = db.Column(db.Integer)
    formulation = db.Column(db.Text)
    competence_disciplines = db.relationship('CompetenceDiscipline', backref='competence', lazy='dynamic')
    indicator = db.relationship('Indicator', backref='competence', lazy='dynamic')


class Indicator(db.Model):
    __tablename__ = 'indicators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    formulation = db.Column(db.Text)
    competence_id = db.Column(db.Integer, db.ForeignKey('competences.id'))

