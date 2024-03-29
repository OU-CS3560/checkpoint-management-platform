"""Collection of Create, Read, Update and Delete Operations."""
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from . import models


async def create_classroom(db: AsyncSession, classroom: schemas.ClassroomCreate):
    classroom_data = classroom.model_dump()
    db_obj = models.Classroom(**classroom_data)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_classrooms(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(models.Classroom).offset(skip).limit(limit)
    results = await db.execute(query)
    rows = results.scalars().all()
    return rows


async def get_classroom(db: AsyncSession, classroom_id: int):
    query = select(models.Classroom).where(models.Classroom.id == classroom_id)
    results = await db.execute(query)
    classroom = results.scalars().one()
    return classroom


async def update_classroom(
    db: AsyncSession, classroom_id: int, classroom: schemas.ClassroomUpdate
):
    classroom_db_obj = await get_classroom(db, classroom_id)
    if classroom.name is not None:
        classroom_db_obj.name = classroom.name
    if classroom.begin_date is not None:
        classroom_db_obj.begin_date = classroom.begin_date
    if classroom.end_date is not None:
        classroom_db_obj.end_date = classroom.end_date
    if classroom.github_classroom_link is not None:
        classroom_db_obj.github_classroom_link = classroom.github_classroom_link
    await db.commit()
    return classroom_db_obj


async def delete_classroom(db: AsyncSession, classroom_id: int):
    classroom_db_obj = await get_classroom(db, classroom_id)
    await db.delete(classroom_db_obj)
    await db.commit()


async def import_students_bb(
    db: AsyncSession, classroom_id: int, import_data: schemas.MembershipResult
):
    classroom_db_obj = await get_classroom(db, classroom_id)

    db_objs = []
    for item in import_data.results:
        if (
            item.courseRoleId == "Instructor"
            or item.courseRoleId == "TeachingAssistant"
        ):
            continue

        obj_data = {
            "classroom": classroom_db_obj,
            "first_name": item.user.name.given,
            "last_name": item.user.name.family,
            "username": item.user.userName,
        }
        db_obj = models.Student(**obj_data)
        db_objs.append(db_obj)

    db.add_all(db_objs)
    await db.commit()
    return {"count": len(db_objs)}


async def get_students(db: AsyncSession, classroom_id: int):
    query = select(models.Student).where(models.Student.classroom_id == classroom_id)
    results = await db.execute(query)
    students = results.scalars().all()
    return students


async def get_student(db: AsyncSession, classroom_id: int, student_id: int):
    query = select(models.Student).where(
        and_(
            models.Student.id == student_id,
            models.Student.classroom_id == classroom_id,
        )
    )
    results = await db.execute(query)
    student = results.scalars().one()
    return student
