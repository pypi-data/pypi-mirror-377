"""Markdown to HTML."""
import importlib.resources

import emoji
from jinja2 import Template
from markdown2 import Markdown


def md_to_html(in_file, out_file, template_kargs):
    """Convert Markdown in ``in_file`` to HTML in ``out_file`` using ``template_kargs``.

    Yeah, it's "kargs" not "kwargs" for some reason 🤷.
    """
    with open(in_file, "r") as f_in:
        markdowner = Markdown()
        html_str = markdowner.convert(f_in.read())
        html_emojized_str = emoji.emojize(html_str, use_aliases=True)
        template_kargs["requirements_html"] = html_emojized_str

    template = Template(importlib.resources.files(__name__).joinpath("REQUIREMENTS.html.template").read_text())
    with open(out_file, "w") as f_out:
        html_str = template.render(template_kargs)
        f_out.write(html_str)
    return out_file
