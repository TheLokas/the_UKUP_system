from app.models import db, Competence, Discipline, CompetenceDiscipline


def connect_discipline_with_competence(competence_id: int,
                                       discipline_id: int,
                                       year: int):
    competence = Competence.query.get(competence_id)
    discipline = Discipline.query.get(discipline_id)

    if not competence:
        return None
    if not discipline:
        return None

    comp_to_dis_ref = CompetenceDiscipline(competence_id=competence_id,
                                           discipline_id=discipline_id,
                                           year_created=year)
    try:
        db.session.add(comp_to_dis_ref)
        db.session.commit()
    except Exception:
        return None

    return comp_to_dis_ref


def edit_discipline_and_competence_connection(ref_id: int,
                                              new_discipline_id: int = None,
                                              new_competence_id: int = None,
                                              new_year: int = None):
    ref = CompetenceDiscipline.query.get(ref_id)
    if not ref:
        return None

    try:
        if new_discipline_id is not None:
            ref.discipline_id = new_discipline_id
            db.session.flush()

        if new_competence_id is not None:
            ref.competence_id = new_competence_id
            db.session.flush()

        if new_year is not None:
            ref.year_created = new_year
            db.session.flush()

        db.session.commit()
    except Exception:
        return None

    return ref
