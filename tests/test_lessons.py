import pytest

from pysl.language import SLExecutor
from pysl.modules.course.lessons import LESSONS


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.title)
def test_every_lesson_example_runs_and_matches_its_documented_output(lesson) -> None:
    result = SLExecutor().execute(lesson.example, list(lesson.inputs))

    assert result.output == lesson.expected_output


def test_lessons_are_numbered_and_unique() -> None:
    titles = [lesson.title for lesson in LESSONS]

    assert len(set(titles)) == len(titles)
    assert [title.split(".")[0] for title in titles] == [str(n) for n in range(1, len(titles) + 1)]


def test_render_includes_example_and_expected_output() -> None:
    rendered = LESSONS[0].render()

    assert LESSONS[0].example in rendered
    assert "Salida esperada" in rendered
