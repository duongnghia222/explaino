"""
In-Memory Storage for Courses
"""

from src.models.course import CourseRecord

_courses: dict[str, CourseRecord] = {}


def save_course(record: CourseRecord) -> None:
    """Save a course record."""
    _courses[record.id] = record


def get_course(id: str) -> CourseRecord | None:
    """Retrieve a course by ID."""
    return _courses.get(id)


def get_all_courses() -> list[CourseRecord]:
    """Get all courses, ordered by creation time descending."""
    return sorted(_courses.values(), key=lambda c: c.created_at, reverse=True)
