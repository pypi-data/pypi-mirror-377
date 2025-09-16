import html
import urllib

from django import forms
from django.template import Context, Template
from django.test.client import RequestFactory
from pyquery import PyQuery


def test_start_timestamp():
    t = Template('{% start_timestamp %}')
    assert t.render(Context())


def test_querystring():
    t = Template('{% querystring "name"="Ayers" "age"=20 %}')
    ctx = Context({'request': RequestFactory().get('/')})
    assert urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(t.render(ctx))).query) == {
        'age': ['20'],
        'name': ['Ayers'],
    }
    ctx = Context({'request': RequestFactory().get('/?age=10')})
    assert urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(t.render(ctx))).query) == {
        'age': ['20'],
        'name': ['Ayers'],
    }

    t = Template('{% querystring "name"="Ayers" without "gender" %}')
    ctx = Context({'request': RequestFactory().get('/')})
    assert urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(t.render(ctx))).query) == {
        'name': ['Ayers']
    }
    ctx = Context({'request': RequestFactory().get('/?gender=male')})
    assert urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(t.render(ctx))).query) == {
        'name': ['Ayers']
    }


def test_with_template():
    class ExampleForm1(forms.Form):
        text = forms.CharField(label='Text', max_length=50)

    request = RequestFactory().get('/')
    t = Template('{{ form|with_template }}')
    ctx = Context({'request': request, 'form': ExampleForm1()})
    rendered = t.render(ctx)
    assert PyQuery(rendered).find('input[type=text]')
    assert not PyQuery(rendered).find('input[type=text]').attr['aria-invalid']
    assert PyQuery(rendered).find('input[type=text]').attr['aria-required']

    ctx = Context({'request': request, 'form': ExampleForm1(data=request.GET)})
    rendered = t.render(ctx)
    assert (
        PyQuery(rendered).find('input[type=text][aria-describedby]').attr['aria-describedby']
        == 'error_id_text'
    )
    assert PyQuery(rendered).find('input[type=text]').attr['aria-invalid']

    class ExampleForm2(forms.Form):
        text = forms.CharField(label='Text', max_length=50, help_text='Help text')

    ctx = Context({'request': request, 'form': ExampleForm2()})
    rendered = t.render(ctx)
    assert (
        PyQuery(rendered).find('input[type=text][aria-describedby]').attr['aria-describedby']
        == 'help_text_id_text'
    )

    ctx = Context({'request': request, 'form': ExampleForm2(data=request.GET)})
    rendered = t.render(ctx)
    assert (
        PyQuery(rendered).find('input[type=text][aria-describedby]').attr['aria-describedby']
        == 'help_text_id_text error_id_text'
    )

    class ExampleForm3(forms.Form):
        text = forms.CharField(label='Text', max_length=50, required=False)

    ctx = Context({'request': request, 'form': ExampleForm3(data=request.GET)})
    rendered = t.render(ctx)
    assert not PyQuery(rendered).find('input[type=text]').attr['aria-required']
