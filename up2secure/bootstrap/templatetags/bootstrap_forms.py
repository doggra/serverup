from django import template
from django.template import Context
from django.template.loader import get_template

register = template.Library()

def _preprocess_fields(form):
    for field in form.fields:
        name = form.fields[field].widget.__class__.__name__.lower()
        if not name.startswith("radio") and not name.startswith("checkbox"):
            try:
                form.fields[field].widget.attrs["class"] += " form-control"
            except KeyError:
                form.fields[field].widget.attrs["class"] = " form-control"
    return form

@register.filter
def as_bootstrap(form):
    template = get_template("bootstrap/bootstrap_form.html")
    form = _preprocess_fields(form)

    c = {"form": form}
    return template.render(c)

@register.filter
def css_class(field):
    return field.field.widget.__class__.__name__.lower()
