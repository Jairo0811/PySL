import pytest

from pysl.language import SLExecutor
from pysl.modules.course.lessons import LESSONS


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.title)
def test_every_lesson_example_runs_and_matches_its_documented_output(lesson) -> None:
    result = SLExecutor().execute(lesson.example, list(lesson.inputs))

    assert result.output == lesson.expected_output


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.title)
def test_every_challenge_has_a_working_reference_solution(lesson) -> None:
    result = SLExecutor().execute(lesson.challenge_solution, list(lesson.challenge_inputs))

    assert result.output == lesson.challenge_output


def test_the_six_original_units_are_kept_in_order() -> None:
    titles = [lesson.title for lesson in LESSONS]

    assert titles == [
        "1. Variables y tipos",
        "2. Condicionales",
        "3. Ciclos",
        "4. Vectores",
        "5. Funciones",
        "6. Proyecto final",
    ]


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.title)
def test_every_unit_is_complete_but_concise(lesson) -> None:
    for field in ("objective", "explanation", "syntax", "example", "challenge"):
        assert getattr(lesson, field).strip(), field
    assert lesson.expected_output
    assert len(lesson.render().splitlines()) <= 45  # one screen, not a chapter


def test_render_lists_every_section_in_teaching_order_without_leaking_the_solution() -> None:
    lesson = LESSONS[0]
    rendered = lesson.render()
    positions = [
        rendered.index(heading)
        for heading in (
            "OBJETIVO",
            "IDEA CLAVE",
            "SINTAXIS",
            "EJEMPLO",
            "SALIDA ESPERADA",
            "MINI RETO",
        )
    ]

    assert positions == sorted(positions)
    assert lesson.challenge_solution not in rendered
