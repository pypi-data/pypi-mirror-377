import re
import time
from collections import OrderedDict

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms import BoundField
from django.template import TemplateSyntaxError
from django.utils.html import escape
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag
def xstatic(modname, filename):
    if settings.DEBUG:
        filename = filename.replace('.min.', '.')
    return settings.STATIC_URL + 'xstatic/' + filename


START_TIMESTAMP = time.strftime('%Y%m%d.%H%M')


@register.simple_tag
def start_timestamp():
    return START_TIMESTAMP


# {% querystring %} bits originally from django-tables2.
kwarg_re = re.compile(r'(?:(.+)=)?(.+)')


def token_kwargs(bits, parser):
    """
    Based on Django's `~django.template.defaulttags.token_kwargs`, but with a
    few changes:

    - No legacy mode.
    - Both keys and values are compiled as a filter
    """
    if not bits:
        return {}
    kwargs = OrderedDict()
    while bits:
        match = kwarg_re.match(bits[0])
        if not match or not match.group(1):
            return kwargs
        key, value = match.groups()
        del bits[:1]
        kwargs[parser.compile_filter(key)] = parser.compile_filter(value)
    return kwargs


class QuerystringNode(template.Node):
    def __init__(self, updates, removals):
        super().__init__()
        self.updates = updates
        self.removals = removals

    def render(self, context):
        if not 'request' in context:
            raise ImproperlyConfigured('Missing django.core.context_processors.request')
        params = dict(context['request'].GET)
        for key, value in self.updates.items():
            key = key.resolve(context)
            value = value.resolve(context)
            if key not in ('', None):
                params[key] = value
        for removal in self.removals:
            params.pop(removal.resolve(context), None)
        return escape('?' + urlencode(params, doseq=True))


@register.tag
def querystring(parser, token):
    """
    Creates a URL (containing only the querystring [including "?"]) derived
    from the current URL's querystring, by updating it with the provided
    keyword arguments.

    Example (imagine URL is ``/abc/?gender=male&name=Brad``)::

        {% querystring "name"="Ayers" "age"=20 %}
        ?name=Ayers&gender=male&age=20
        {% querystring "name"="Ayers" without "gender" %}
        ?name=Ayers

    """
    bits = token.split_contents()
    tag = bits.pop(0)
    updates = token_kwargs(bits, parser)
    # ``bits`` should now be empty of a=b pairs, it should either be empty, or
    # have ``without`` arguments.
    if bits and bits.pop(0) != 'without':
        raise TemplateSyntaxError("Malformed arguments to '%s'" % tag)
    removals = [parser.compile_filter(bit) for bit in bits]
    return QuerystringNode(updates, removals)


@register.filter
def with_template(form):
    form_template = template.loader.get_template('gadjo/form.html')
    fields_with_templates = []
    for field in form:
        widget = field.field.widget
        templates = ['gadjo/widget.html']
        if hasattr(widget, 'input_type'):
            templates.insert(0, 'gadjo/%s-widget.html' % widget.input_type)
        aria_described_by = []
        if field.field.help_text:
            aria_described_by.append(f'help_text_{field.id_for_label}')
        if field.errors:
            aria_described_by.append(f'error_{field.id_for_label}')
            field.field.widget.attrs['aria-invalid'] = 'true'
        if field.field.required:
            field.field.widget.attrs['aria-required'] = 'true'
        if aria_described_by:
            field.field.widget.attrs['aria-describedby'] = ' '.join(aria_described_by)
        fields_with_templates.append(
            (
                field,
                template.loader.select_template(templates),
            )
        )
    return form_template.render({'form': form, 'fields_with_templates': fields_with_templates})


# pattern to transform Django camel case class names to CSS class names with
# dashes. (CheckboxInput -> checkbox-input)
class_name_pattern = re.compile(r'(?<!^)(?=[A-Z])')


@register.filter
def field_class_name(field):
    if isinstance(field, BoundField):
        field = field.field
    return class_name_pattern.sub('-', field.widget.__class__.__name__).lower()
