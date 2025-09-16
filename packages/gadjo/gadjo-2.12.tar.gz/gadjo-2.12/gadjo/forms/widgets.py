from django import forms


class MultiSelectWidget(forms.MultiWidget):
    template_name = 'gadjo/widgets/multiselectwidget.html'

    class Media:
        js = ('js/gadjo.multiselectwidget.js',)
        css = {'all': ('css/gadjo.multiselectwidget.css',)}

    def __init__(self, attrs=None, form_field=None, max_choices=None):
        self.attrs = attrs
        self.form_field = form_field or forms.Select
        self.max_choices = max_choices
        widgets = [self.form_field(attrs=attrs)]
        super().__init__(widgets, attrs)

    def get_context(self, name, value, attrs):
        if not isinstance(value, list):
            value = [value]

        self.widgets = []
        for _ in range(max(len(value), 1)):
            self.widgets.append(self.form_field(attrs=self.attrs, choices=self.choices))

        # all subwidgets must have the same name
        self.widgets_names = [''] * len(self.widgets)

        context = super().get_context(name, value, attrs)
        context['widget']['max_choices'] = self.max_choices

        return context

    def decompress(self, value):
        return value or []

    def value_from_datadict(self, data, files, name):
        values = [x for x in data.getlist(name) if x]

        # remove duplicates while keeping order
        return list(dict.fromkeys(values))

    def id_for_label(self, id_):
        return id_

    def value_omitted_from_data(self, *args, **kwargs):
        return super(forms.MultiWidget, self).value_omitted_from_data(*args, **kwargs)
