import json
from django import template
from django.template.context import Context
from django.template.loader import get_template
from typing import Dict, List, Any
from django_glide.config import Config

register = template.Library()


def normalize_value(value: Any) -> Any:
    """
    Convert string template args into proper Python types.
    Not the best code, but it will do the trick.
    """
    if isinstance(value, str):
        val = value.strip().lower()
        if val == "true":
            return True
        if val == "false":
            return False
        if val == "null" or val == "none":
            return None
        # try to parse numbers
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return value  # fallback: leave as string
    return value


def prepare_options(**options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check for the presence of the breakpoints field to parse it properly. Will throw an exception if invalid.
    """
    for key, value in options.items():
        if key in ("breakpoints", "peek", "classes"):
            try:
                options[key] = json.loads(str(value))
            except (TypeError, json.JSONDecodeError):
                options[key] = normalize_value(value)
        else:
            options[key] = normalize_value(value)

    return options


@register.simple_tag(takes_context=True)
def glide_carousel(
    context: Context,
    items: List[Any],
    carousel_id: str = "glide1",
    carousel_template: str | None = None,
    slide_template: str | None = None,
    arrows: bool = False,
    arrows_template: str | None = None,
    bullets: bool = False,
    bullets_template: str | None = None,
    **options: Dict[str, Any],
) -> str:
    """
    Render a Glide.js carousel.
    """
    config = Config()

    carousel_template_name = carousel_template or config.default_carousel_template
    slide_template_name = slide_template or config.default_slide_template

    carousel_template = get_template(carousel_template_name)

    ctx = {
        **context.flatten(),
        "items": items,
        "carousel_id": carousel_id,
        "options": json.dumps(prepare_options(**options)),
        "arrows": normalize_value(arrows),
        "arrows_template": arrows_template,
        "bullets": normalize_value(bullets),
        "bullets_template": bullets_template,
        "slide_template": slide_template_name,
    }

    return carousel_template.render(ctx)


@register.inclusion_tag("assets.html")
def glide_assets() -> Dict[str, Any]:
    """
    Render Glide.js assets (CSS + JS).
    Should be called once, usually in the <head> or before </body>.
    """
    config = Config()
    return {
        "js_url": config.js_url,
        "css_core_url": config.css_core_url,
        "css_theme_url": config.css_theme_url,
    }
