"""Lab 5, Part D warm-up: talk to a database from Python with sqlite3."""

import sqlite3


def connect(path: str = "school.db") -> sqlite3.Connection:
    return sqlite3.connect(path)


def students_in_program(con: sqlite3.Connection, program: str) -> list[str]:
    """Names of students in `program`, sorted A→Z."""
    rows = con.execute(
        "SELECT name FROM students WHERE program = ? ORDER BY name",
        (program,),
    ).fetchall()
    return [name for (name,) in rows]


def add_student(
    con: sqlite3.Connection, name: str, year: int, program: str
) -> int:
    """Insert a student and return the new id."""
    cursor = con.execute(
        "INSERT INTO students (name, year, program) VALUES (?, ?, ?)",
        (name, year, program),
    )
    con.commit()
    return cursor.lastrowid


def average_grade(con: sqlite3.Connection, course_code: str) -> float | None:
    """Average grade in a course, rounded to 2 decimals; None if no grades."""
    row = con.execute(
        "SELECT AVG(grade) FROM enrollments WHERE course_code = ?",
        (course_code,),
    ).fetchone()
    average = row[0]
    return None if average is None else round(average, 2)


def transcript(
    con: sqlite3.Connection, student_id: int
) -> list[tuple[str, int, float | None]]:
    """Return (course title, credits, grade) for one student, sorted by title."""
    query = """
        SELECT c.title, c.credits, e.grade
        FROM enrollments AS e
        INNER JOIN courses AS c ON c.code = e.course_code
        WHERE e.student_id = ?
        ORDER BY c.title
    """
    return con.execute(query, (student_id,)).fetchall()
