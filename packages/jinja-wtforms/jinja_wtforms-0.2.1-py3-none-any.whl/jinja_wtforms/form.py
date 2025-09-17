import wtforms.fields as fields


TEMPLATE_FORM_FIELDS = {
    "checkbox": fields.BooleanField,
    "decimal": fields.DecimalField,
    "date": fields.DateField,
    "datetime": fields.DateTimeField,
    "float": fields.FloatField,
    "int": fields.IntegerField,
    "radio": fields.RadioField,
    "select": fields.SelectField,
    "selectmulti": fields.SelectMultipleField,
    "text": fields.StringField,
    "textarea": fields.TextAreaField,
    "password": fields.PasswordField,
    "hidden": fields.HiddenField,
    "datetimelocal": fields.DateTimeLocalField,
    "decimalrange": fields.DecimalRangeField,
    "email": fields.EmailField,
    "intrange": fields.IntegerRangeField,
    "search": fields.SearchField,
    "tel": fields.TelField,
    "url": fields.URLField,
    "file": fields.FileField,
    "files": fields.MultipleFileField
}


class FormMixin:
    @property
    def enctype(self):
        for f in self:
            if f.type == "FileField":
                return "multipart/form-data"
        return "application/x-www-form-urlencoded"


class TemplateField:
    _formfield = True

    def __init__(self, field):
        object.__setattr__(self, "_field", field)

    def __getattr__(self, name):
        if hasattr(self._field, name):
            return getattr(self._field, name)
        if name in TEMPLATE_FORM_FIELDS:
            return _fake_field_init(self._field)
        raise AttributeError()

    def __setattr__(self, name, value):
        setattr(self._field, name, value)

    def __call__(self, *args, **kwargs):
        return self._field(*args, **kwargs)


def _fake_field_init(field):
    def caller(*args, **kwargs):
        return field
    return caller


class UnboundTemplateField(TemplateField):
    def bind(self, *args, **kwargs):
        return TemplateField(self._field.bind(*args, **kwargs))


class FormDefinitionError(Exception):
    pass


class NoFormError(Exception):
    pass
