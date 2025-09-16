from django import forms
from django.template import Context, Template
from django.test.client import RequestFactory
from pyquery import PyQuery

from gadjo.forms.widgets import MultiSelectWidget


def test_multiselect_widget():
    class ExampleForm(forms.Form):
        choices = forms.MultipleChoiceField(
            label='choices', choices=[('a', 'Aa'), ('b', 'Bb'), ('c', 'Cc')], widget=MultiSelectWidget
        )

    request = RequestFactory().get('/')
    t = Template('{{ form|with_template }}')
    ctx = Context({'request': request, 'form': ExampleForm()})
    rendered = t.render(ctx)
    assert len(PyQuery(rendered).find('select')) == 1
    assert PyQuery(rendered).find('.gadjo-multi-select-widget--button-add')

    request = RequestFactory().get('/?choices=a&choices=b')
    t = Template('{{ form|with_template }}')
    ctx = Context({'request': request, 'form': ExampleForm(data=request.GET)})
    rendered = t.render(ctx)
    assert len(PyQuery(rendered).find('select')) == 2
    assert PyQuery(rendered).find('option[selected]').text() == 'Aa Bb'
    assert ctx['form'].cleaned_data == {'choices': ['a', 'b']}


def test_multiselect_widget_omitted_from_data():
    class ExampleForm(forms.Form):
        choices = forms.MultipleChoiceField(
            label='choices', choices=[('a', 'Aa'), ('b', 'Bb'), ('c', 'Cc')], widget=MultiSelectWidget
        )

    form = ExampleForm(data={})
    assert (
        form.fields['choices'].widget.value_omitted_from_data(
            form.data, form.files, form.add_prefix('choices')
        )
        is True
    )

    form = ExampleForm(data={'choices': 'a'})
    assert (
        form.fields['choices'].widget.value_omitted_from_data(
            form.data, form.files, form.add_prefix('choices')
        )
        is False
    )
