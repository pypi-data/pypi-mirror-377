from wtforms import Form
import wtforms.validators as wtvalidators
from jinja2 import nodes
from jinja2.ext import Extension
from .form import TEMPLATE_FORM_FIELDS, FormMixin, FormDefinitionError, UnboundTemplateField


def extract_form_classes_from_template(env, template, *args, **kwargs):
    source, filename, _ = env.loader.get_source(env, template)
    tpl_node = env.parse(source, filename=filename)
    form_classes = extract_form_classes_from_node(tpl_node, *args, **kwargs)
    for form_class in form_classes:
        form_class.template = filename
    return form_classes


def extract_form_classes_from_node(node, class_name=None, var_name="form", base_cls=Form):
    if isinstance(var_name, (list, tuple)):
        form_defs = {v: {"meta": {}, "class_name": class_name[i] if isinstance(class_name, (list, tuple)) else class_name} for i, v in enumerate(var_name)}
    else:
        form_defs = {var_name: {"class_name": class_name, "meta": {}}}

    for form_node in node.find_all((nodes.Const)):
        if not hasattr(form_node, "form_var_name"):
            continue
        form_defs[form_node.form_var_name] = {"class_name": form_node.form_class_name, "meta": form_node.form_meta}

    forms = {}
    for call in node.find_all((nodes.Call,)):
        if not isinstance(call.node, nodes.Getattr) or not isinstance(call.node.node, nodes.Getattr):
            continue
        attrnode = call.node.node
        if not isinstance(attrnode.node, nodes.Name) or attrnode.node.name not in form_defs:
            continue
        var_name = attrnode.node.name
        fname = attrnode.attr
        forms.setdefault(var_name, {})[fname] = [call.node.attr, {}]

        if len(call.args) > 0:
            forms[var_name][fname][1]["label"] = jinja_node_to_python(call.args[0])

        for arg in call.kwargs:
            forms[var_name][fname][1][arg.key] = jinja_node_to_python(arg.value)

    form_classes = []
    for var_name, fields in forms.items():
        form_def = form_defs[var_name]
        form_class = type(form_def["class_name"] or "TemplateForm", (FormMixin, base_cls,), {"template_var_name": var_name})
        form_classes.append(form_class)

        if form_def["meta"]:
            form_class.Meta = type("Meta", tuple(), form_def["meta"])

        for fname, fopts in fields.items():
            ftype, kwargs = fopts
            if ftype not in TEMPLATE_FORM_FIELDS:
                raise FormDefinitionError("Unknown field type '%s'" % ftype)
            validators = []
            if "label" not in kwargs:
                kwargs["label"] = fname
            if kwargs.pop("required", False):
                validators.append(wtvalidators.DataRequired())
            if kwargs.pop("optional", False):
                validators.append(wtvalidators.Optional())
            if "range" in kwargs:
                min, max = kwargs.pop("range")
                validators.append(wtvalidators.NumberRange(min, max))
            if "length" in kwargs:
                min, max = kwargs.pop("length")
                validators.append(wtvalidators.Length(min, max))
            if "validators" in kwargs:
                for v in kwargs.pop("validators"):
                    validators.append(getattr(wtvalidators, v)())
            if "placeholder" in kwargs:
                kwargs.setdefault('render_kw', {})["placeholder"] = kwargs.pop("placeholder")
            setattr(form_class, fname, UnboundTemplateField(TEMPLATE_FORM_FIELDS[ftype](validators=validators, **kwargs)))

    return form_classes


class FormStmtExtension(Extension):
    tags = set(["form"])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        form_var_name = "form"
        form_meta = {}
        form_class_name = None
        if parser.stream.current.test("name"):
            form_class_name = next(parser.stream).value
        if parser.stream.current.test("lparen"):
            form_meta = {k.key: jinja_node_to_python(k.value) for k in parser.parse_call_args()[1]}
        if parser.stream.skip_if("assign"):
            form_var_name = parser.stream.expect("name").value
        
        auto_init = form_meta.pop("auto_init", True)
        node = nodes.Const("", lineno=lineno)
        node.form_class_name = form_class_name
        node.form_meta = form_meta
        node.form_var_name = form_var_name
        out = [nodes.Output([node])]

        if auto_init:
            out.append(
                nodes.If(nodes.Not(nodes.Test(nodes.Name(form_var_name, "load"), "defined", [], [], None, None)), [
                    nodes.Assign(nodes.Name(form_var_name, "store"), self.call_method("_init_form_obj", [nodes.ContextReference(), nodes.Const(form_var_name)], lineno=lineno))
                ], [], [], lineno=lineno)
            )

        return out
    
    def _init_form_obj(self, context, var_name):
        if not context.name:
            return
        forms = self.environment.forms.get(context.name)
        if not forms:
            return
        form_class = forms.get(var_name)
        return form_class() if form_class else None
    

JINJA_CALL_NODE_CONVERTERS = {}


def map_jinja_call_node_to_func(func, func_name=None):
    def converter(node):
        args = [jinja_node_to_python(arg) for arg in node.args]
        kwargs = {arg.key: jinja_node_to_python(arg.value) for arg in node.kwargs}
        return func(*args, **kwargs)
    JINJA_CALL_NODE_CONVERTERS[func_name or func.__name__] = converter
    return func


def jinja_node_to_python(node):
    """Converts a jinja node to its python equivalent
    """
    if isinstance(node, nodes.Const):
        return node.value
    if isinstance(node, nodes.Neg):
        return -jinja_node_to_python(node.node)
    if isinstance(node, nodes.Name):
        return node.name
    if isinstance(node, (nodes.List, nodes.Tuple)):
        value = []
        for i in node.items:
            value.append(jinja_node_to_python(i))
        return value
    if isinstance(node, nodes.Dict):
        value = {}
        for pair in node.items:
            value[pair.key.value] = jinja_node_to_python(pair.value)
        return value
    if isinstance(node, nodes.Call):
        if isinstance(node.node, nodes.Name) and node.node.name in JINJA_CALL_NODE_CONVERTERS:
            return JINJA_CALL_NODE_CONVERTERS[node.node.name](node)
        raise FormDefinitionError("Cannot convert function calls from jinja to python other than translation calls")
    raise Exception("Cannot convert jinja nodes to python")