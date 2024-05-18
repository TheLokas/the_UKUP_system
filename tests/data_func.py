from app.UKUP import functions
from app.models import (Discipline,
                        Direction,
                        DirectionDiscipline,
                        Competence,
                        CompetenceDiscipline,
                        Module,
                        Indicator,
                        IndicatorDiscipline)
from .conftest import db


def add_disciplines_data():
    if (len(Module.query.all()) == 0):
        functions.add_few_data()
    year = 2023
    disciplines = [
        Discipline(name="Математика",
                   year_approved=year,
                   block_id=1,
                   module_id=1,
                   department_id=1),
        Discipline(name="Информатика",
                   year_approved=year,
                   block_id=1,
                   module_id=1,
                   department_id=1),
        Discipline(name="Third",
                   year_approved=year,
                   block_id=1,
                   module_id=1,
                   department_id=1)
    ]
    
    direction = Direction(name="Информатика", code="1")
    extra_direction = Direction(name="FSFAF", code="1")
    db.session.add(direction)
    db.session.add(extra_direction)
    db.session.add_all(disciplines)
    db.session.commit()

    direction_disciplines = [
        DirectionDiscipline(discipline_id=disciplines[0].id,
                            direction_id=direction.id
                            ),
        DirectionDiscipline(discipline_id=disciplines[1].id,
                            direction_id=direction.id
                            ),
        DirectionDiscipline(discipline_id=disciplines[2].id,
                            direction_id=extra_direction.id
                            )
    ]

    db.session.add_all(direction_disciplines)
    db.session.commit()
    return disciplines, direction, direction_disciplines


def add_competence_data():
    if (len(Module.query.all()) == 0):
        functions.add_few_data()

    direction = Direction.query.get(1)

    competences_to_add = [
        Competence(name="УК-1",
                   year_approved="2023",
                   type="УК",
                   formulation="...",
                   direction_id=direction.id),
        Competence(name="УК-2",
                   year_approved="2023",
                   type="УК",
                   formulation="...",
                   direction_id=direction.id),
        Competence(name="ОПК-1",
                   year_approved="2024",
                   type="ОПК",
                   formulation="...",
                   direction_id=direction.id),
    ]

    db.session.add_all(competences_to_add)
    db.session.commit()
    return competences_to_add


def add_indicators():
    if len(Competence.query.all()) == 0:
        competences = add_competence_data()
    else:
        competences = Competence.query.all()

    indicators = [
        Indicator(name=competences[0].name + ".1",
                  formulation="...",
                  competence_id=competences[0].id),
        Indicator(name=competences[1].name + ".1",
                  formulation="...",
                  competence_id=competences[1].id),
        Indicator(name=competences[1].name + ".2",
                  formulation="...",
                  competence_id=competences[1].id),
        Indicator(name=competences[2].name + ".1",
                  formulation="...",
                  competence_id=competences[2].id),
        Indicator(name=competences[2].name + ".1",
                  formulation="...",
                  competence_id=competences[2].id)
    ]

    db.session.add_all(indicators)
    db.session.commit()

    return indicators


def add_competence_discipline_links():
    if len(Discipline.query.all()) == 0:
        disciplines = add_disciplines_data()
    else:
        disciplines = Discipline.query.all()

    if len(Competence.query.all()) == 0:
        competences = add_disciplines_data()
    else:
        competences = Discipline.query.all()

    links = [
        CompetenceDiscipline(competence_id=competences[0].id,
                             discipline_id=disciplines[0].id),
        CompetenceDiscipline(competence_id=competences[1].id,
                             discipline_id=disciplines[1].id),
        CompetenceDiscipline(competence_id=competences[2].id,
                             discipline_id=disciplines[2].id),
        CompetenceDiscipline(competence_id=competences[0].id,
                             discipline_id=disciplines[2].id)
    ]

    db.session.add_all(links)
    db.session.commit()
    return links


def add_indicator_discipline_links():
    if len(Discipline.query.all()) == 0:
        disciplines = add_disciplines_data()[0]
    else:
        disciplines = Discipline.query.all()

    if len(Indicator.query.all()) == 0:
        indicators = add_indicators()
    else:
        indicators = Indicator.query.all()

    links = [
        IndicatorDiscipline(indicator_id=indicators[0].id,
                            discipline_id=disciplines[0].id),
        IndicatorDiscipline(indicator_id=indicators[1].id,
                            discipline_id=disciplines[1].id),
        IndicatorDiscipline(indicator_id=indicators[2].id,
                            discipline_id=disciplines[1].id),
        IndicatorDiscipline(indicator_id=indicators[3].id,
                            discipline_id=disciplines[1].id),
        IndicatorDiscipline(indicator_id=indicators[4].id,
                            discipline_id=disciplines[2].id),
    ]

    db.session.add_all(links)
    db.session.commit()

    return links


def add_all():
    competences = add_competence_data()
    disciplines = add_disciplines_data()[0]
    competence_disciplines = add_competence_discipline_links()
    indicator_disciplines = add_indicator_discipline_links()

    return competences, disciplines, competence_disciplines, indicator_disciplines # noqa E501
