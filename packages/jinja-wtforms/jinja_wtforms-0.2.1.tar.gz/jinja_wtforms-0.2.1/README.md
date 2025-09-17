# Jinja-WTForms

Extract WTForms classes from jinja templates

## Installation

    pip install jinja-wtforms

## Setup

```py
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
env.add_extension('jinja_wtforms.WtformExtension')
```

## Defining forms in templates

Defining forms is almost like using a pre-defined form but with added information
on the type of the field.

To do so, you'll need to call a method named after the type of the field on each
field. So if you want to define a "firstname" field as a text field, you can
do `form.firstname.text()`.

Let's define a signup form:

```html
<form action="" method="post">
    {{ form.hidden_tags() }}
    <p><label>First name</label> {{ form.firstname.text() }}</p>
    <p><label>Last name</label> {{ form.lastname.text() }}</p>
    <p><label>Email</label> {{ form.email.email() }}</p>
    <p><label>Password</label> {{ form.password.password() }}</p>
</form>
```

The optional parameters of the field definition functions are:

 - *label*: the field's label (can also be define as the first argument)
 - *description*: the field's description
 - *placeholder*: the field's placeholder
 - *required*: boolean, default false
 - *optional*: boolean, default false
 - *range*: a tuple of (min, max), value should be a number in the range
 - *length*: a tuple of (min, max), value should be of string of length in the range
 - *validators*: a list of validator names from `wtforms.validators`

Available field types and their actual class:

 - *checkbox*: `wtforms.fields.BooleanField`
 - *decimal*: `wtforms.fields.DecimalField`
 - *date*: `wtforms.fields.DateField`
 - *datetime*: `wtforms.fields.DateTimeField`
 - *float*: `wtforms.fields.FloatField`
 - *int*: `wtforms.fields.IntegerField`
 - *radio*: `wtforms.fields.RadioField`
 - *select*: `wtforms.fields.SelectField`
 - *selectmulti*: `wtforms.fields.SelectMultipleField`
 - *text*: `wtforms.fields.StringField`
 - *textarea*: `wtforms.fields.TextAreaField`
 - *password*: `wtforms.fields.PasswordField`
 - *upload*: `wtforms.fields.FileField`
 - *hidden*: `wtforms.fields.HiddenField`
 - *datetimelocal*: `wtforms.fields.DateTimeLocalField`
 - *decimalrange*: `wtforms.fields.DecimalRangeField`
 - *email*: `wtforms.fields.EmailField`
 - *intrange*: `wtforms.fields.IntegerRangeField`
 - *search*: `wtforms.fields.SearchField`
 - *tel*: `wtforms.fields.TelField`
 - *url*: `wtforms.fields.URLField`

## Extracting forms

Use the form registry available through the `forms` property of the environment:

```py
form_class = env.forms["form.html"].form # where form.html is the template filename containing the form definition
form = form_class()

# can also be directly instantiated
form = env.forms["form.html"]()
```

Form classes are extracted on first call to a env.forms. You can pre-register all forms using `env.forms.register_all()`

## The form directive

The form directive can be used before any usage of the form object. It will ensure that a form object exists. It can also be used to define the class name.

As a way to ensure a form object is always available:

```html
{% form %}
<form action="" method="post">
    <p><label>First name</label> {{ form.firstname.text() }}</p>
</form>
```

To customize the class name:

```html
{% form MyForm %}
<form action="" method="post">
    <p><label>First name</label> {{ form.firstname.text() }}</p>
</form>
```

Class name with optional Meta property:

```html
{% form MyForm(csrf=True) %}
<form action="" method="post">
    {{form.hidden_tags()}}
    <p><label>First name</label> {{ form.firstname.text() }}</p>
</form>
```

To customize the form object variable name:

```html
{% form = f %}
<form action="" method="post">
    <p><label>First name</label> {{ f.firstname.text() }}</p>
</form>
```

With custom class name:

```html
{% form MyForm = f %}
<form action="" method="post">
    <p><label>First name</label> {{ f.firstname.text() }}</p>
</form>
```

You can disable auto instantiation of a form object when non is present by using `auto_init=False` as a Meta param.

## Multiple forms in a single template

Use multiple form directives to declare mutliple forms with different form object names.

```html
{% form %}
{% form = form2 %}
<form action="" method="post">
    <p><label>First name</label> {{ form.firstname.text() }}</p>
</form>
<form action="" method="post">
    <p><label>First name</label> {{ form2.email.email() }}</p>
</form>
```

Then access them from the registry:

```py
form_class = env.forms["form.html"].form
form2_class = env.forms["form.html"].form2
```