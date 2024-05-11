from app.models import db, Competence, Discipline, CompetenceDiscipline
from datetime import date


def connect_discipline_with_competence(competence_id, discipline_id):
    competence = Competence.query.get(competence_id)
    discipline = Discipline.query.get(discipline_id)

    if not competence:
        return None
    if not discipline:
        return None

    current_year = date.today().year
    comp_to_dis_ref = CompetenceDiscipline(competence_id=competence_id,
                                           discipline_id=discipline_id,
                                           year_created=current_year)
    try:
        db.session.add(comp_to_dis_ref)
        db.session.commit()
    except Exception:
        return None

    return comp_to_dis_ref
