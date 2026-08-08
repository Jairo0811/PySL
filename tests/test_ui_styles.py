from pysl.ui.styles import (
    DARK_THEME,
    LIGHT_THEME,
    get_stylesheet,
    normalize_font_size,
    normalize_theme,
    theme_colors,
)


def test_theme_normalization_and_stylesheets() -> None:
    assert normalize_theme("Claro") == LIGHT_THEME
    assert normalize_theme("claro") == LIGHT_THEME
    assert normalize_theme("desconocido") == DARK_THEME

    light_stylesheet = get_stylesheet(LIGHT_THEME, 16)
    dark_stylesheet = get_stylesheet(DARK_THEME, 16)

    assert theme_colors(LIGHT_THEME)["background"] in light_stylesheet
    assert theme_colors(DARK_THEME)["background"] in dark_stylesheet
    assert light_stylesheet != dark_stylesheet


def test_font_size_is_clamped_to_supported_range() -> None:
    assert normalize_font_size(8) == 11
    assert normalize_font_size(16) == 16
    assert normalize_font_size(30) == 24
    assert "font-size: 24px" in get_stylesheet(DARK_THEME, 30)
