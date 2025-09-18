from novadata_utils.models import NovadataModel

from .props_dict import props_dict


def get_fields(model):
    """get_fields personalizado."""
    parents = model._meta.parents
    if parents:
        first_parent = next(iter(parents))
        is_subclass = issubclass(NovadataModel, first_parent)

        if is_subclass:
            super_fields_whinout_id = list(first_parent._meta.fields)[1:]
            fields = list(model._meta.get_fields())
            duplicated_fields = filter(
                lambda field: field in super_fields_whinout_id,
                super_fields_whinout_id,
            )
            list(map(lambda field: fields.remove(field), duplicated_fields))

            new_fields = fields + super_fields_whinout_id
            return new_fields

    return model._meta.get_fields()


def get_field_type(field):
    """Retorna o tipo de um campo."""
    field_type = field.get_internal_type()
    is_choices = (
        hasattr(field, "choices")
        and field.choices
        and field_type == "CharField"
    )

    if is_choices:
        field_type = "ChoicesField"

    return field_type


def get_prop(model, prop, str=False, annotate_type=False):
    """
    Retorna uma lista de campos de um model baseado em uma propriedade.

    Exemplo:
        get_prop(model, "list_display") retorna todos os campos que podem ser
        exibidos na listagem do admin. Que são:
            "BigAutoField",
            "BooleanField",
            "CharField",
            "DateField",
            "DateTimeField",
            "DecimalField",
            "OneToOneField",
            "ForeignKey",
            "IntegerField" e
            "PositiveIntegerField".
    """
    props = []
    fields = get_fields(model)
    for field in fields:
        field_type = get_field_type(field)

        is_original_field = not hasattr(field, "field")
        is_sub_id_field = "_ptr" in field.name
        if (
            field_type in props_dict[prop]
            and is_original_field
            and not is_sub_id_field
        ):
            if str:
                name = f'"{field.name}",'
            else:
                name = field.name

            if annotate_type:
                props.append({"name": name, "type": field_type})
            else:
                props.append(name)

    return props
