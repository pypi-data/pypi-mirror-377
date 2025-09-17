from wtforms import Form
from .extractor import extract_form_classes_from_template, FormStmtExtension
from jinja2 import TemplateNotFound, TemplateSyntaxError


class TemplateForms:
    def __init__(self, form_classes):
        self.form_classes = form_classes

    def get(self, name):
        for form_class in self.form_classes:
            if form_class.template_var_name == name or form_class.__name__ == name:
                return form_class

    def __getattr__(self, name):
        form_class = self.get(name)
        if form_class is None:
            raise AttributeError()
        return form_class
    
    def __call__(self, *args, **kwargs):
        if len(self.form_classes) == 1:
            return self.form_classes[0](*args, **kwargs)
        return getattr(self, "form")(*args, **kwargs)


class FormRegistry:
    def __init__(self, env):
        self.env = env
        self.forms = {}

    def register_all(self, filter_func=None, **extract_kwargs):
        for template in self.env.list_templates(filter_func=filter_func):
            self.register(template, **extract_kwargs)

    def register_from_loader(self, loader, remove_prefix=None, **extract_kwargs):
        for template in loader.list_templates():
            self.register(template, template[len(remove_prefix):].lstrip("/") if remove_prefix else template, **extract_kwargs)

    def register(self, template, alias=None, **extract_kwargs):
        try:
            form_classes = extract_form_classes_from_template(self.env, template, **dict({"base_cls": getattr(self.env, "form_base_cls", Form)}, **extract_kwargs))
        except TemplateSyntaxError:
            return
        
        self.forms[alias or template] = TemplateForms(form_classes)
        for form_class in form_classes:
            if form_class.__name__ != "TemplateForm":
                self.forms[form_class.__name__] = form_class

    def __getitem__(self, path):
        if path not in self.forms:
            self.register(path)
        return self.forms[path]
    
    def get(self, path):
        try:
            return self[path]
        except TemplateNotFound:
            return None
    

class WtformExtension(FormStmtExtension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.forms = FormRegistry(environment)