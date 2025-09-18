from functools import partial

from crum import get_current_request
from django.contrib import admin
from django_object_actions import DjangoObjectActions
from import_export import fields, resources
from import_export.admin import ImportExportMixin

from novadata_utils.functions import get_prop, transform_field


class NovadataModelAdmin(
    ImportExportMixin,
    DjangoObjectActions,
    admin.ModelAdmin,
):
    """
    Classe para realizar funcionalidades default em todas as classes do admin.

    A mesma adiciona todos os campos possíveis nas seguintes propriedades:
    - list_display
    - list_filter
    - autocomplete_fields
    - filter_horizontal
    """

    list_display: list = []

    search_fields: list = []

    list_filter: list = []

    autocomplete_fields: list = []

    list_select_related: list = []

    auto_search_fields: bool = True

    filter_horizontal: list = []

    exclude: list = []

    def remove_fields_of_prop(self, list_props: list, request=None):
        """Remove os campos de uma propriedade com base no exclude."""
        if not request:
            request = get_current_request()
        exclude_fields = self.get_exclude(request)
        list_props_copy = list_props.copy()

        for field in list_props_copy:
            if field in exclude_fields:
                list_props.remove(field)

            is_tuple = isinstance(field, tuple)
            if is_tuple and field[0] in exclude_fields:
                list_props.remove(field)

        return list_props

    def get_list_display(self, request):
        """Retorna a lista de campos que estarão na listagem."""
        super().get_list_display(request)

        if not self.list_display:
            model = self.model
            list_display = get_prop(model, "list_display")

            return self.remove_fields_of_prop(list_display, request)
        else:
            return self.list_display

    def get_search_fields(self, request):
        """Retorna a lista de campos que estarão no campo de busca."""
        super().get_search_fields(request)

        if self.auto_search_fields and not self.search_fields:
            model = self.model
            search_fields = get_prop(model, "search_fields")

            return self.remove_fields_of_prop(search_fields, request)
        else:
            return self.search_fields

    def get_list_filter(self, request):
        """Retorna a lista de campos que estarão no filtro."""
        super().get_list_filter(request)

        if not self.list_filter:
            model = self.model
            foreign_keys = get_prop(model, "foreign_keys")
            choices_fields = get_prop(model, "choices_fields")
            date_fields = get_prop(model, "dates")
            numeric_fields = get_prop(model, "numerics")

            list_filter_fields = get_prop(model, "list_filter")

            transform_foreign_keys = partial(
                transform_field,
                foreign_keys,
                "foreign_keys",
            )
            transform_choices_fields = partial(
                transform_field,
                choices_fields,
                "choices_fields",
            )
            transform_dates = partial(
                transform_field,
                date_fields,
                "dates",
            )
            transform_numerics = partial(
                transform_field,
                numeric_fields,
                "numerics",
            )

            list_filter = list(map(transform_foreign_keys, list_filter_fields))
            list_filter = list(map(transform_choices_fields, list_filter))
            list_filter = list(map(transform_dates, list_filter))
            list_filter = list(map(transform_numerics, list_filter))
            concat_list_filter = list(self.list_filter) + list_filter

            return self.remove_fields_of_prop(concat_list_filter, request)
        return self.list_filter

    def get_autocomplete_fields(self, request):
        """Retorna a lista de campos que estarão no autocomplete."""
        super().get_autocomplete_fields(request)

        if not self.autocomplete_fields:
            model = self.model
            autocomplete_fields = get_prop(model, "autocomplete_fields")

            return self.remove_fields_of_prop(autocomplete_fields, request)
        else:
            return self.autocomplete_fields

    def get_list_select_related(self, request):
        """Retorna a lista de campos que estarão no select_related."""
        super().get_list_select_related(request)

        if not self.list_select_related:
            model = self.model
            list_select_related = get_prop(model, "list_select_related")

            return self.remove_fields_of_prop(list_select_related, request)
        else:
            return self.list_select_related

    def get_filter_horizontal(self):
        """Retorna a lista de campos que estarão no filtro horizontal."""
        if not self.filter_horizontal:
            model = self.model
            filter_horizontal = get_prop(model, "filter_horizontal")

            return self.remove_fields_of_prop(filter_horizontal)
        else:
            return self.filter_horizontal

    def get_exclude(self, request, obj=None):
        """Retorna a lista de campos que estarão no exclude."""
        exclude_fields = [super().get_exclude(request, obj)]
        exclude_fields += self.exclude
        exclude_fields += [
            "usuario_criacao",
            "usuario_atualizacao",
            "created_by",
            "updated_by",
        ]

        return exclude_fields

    def get_resource_classes(self, request):
        """Retorna as classes de recursos para exportação."""
        if not hasattr(self, "export_widgets"):
            return super().get_resource_classes(request)

        Meta = {
            "Meta": type(
                "Meta",
                (),
                {
                    "model": self.model,
                    "name": "Com IDs",
                },
            )
        }

        ComIdsResource = type(
            "ComIdsResource",
            (resources.ModelResource,),
            Meta,
        )

        export_fields = {
            key: fields.Field(
                column_name=key,
                attribute=key,
                widget=self.export_widgets.get(key),
            )
            for key in self.export_widgets.keys()
        }

        ComNomesResource = type(
            "ComNomesResource",
            (ComIdsResource,),
            {
                "Meta": type(
                    "Meta",
                    (),
                    {
                        "name": "Com nomes",
                    },
                ),
                **export_fields,
            },
        )

        return [
            ComIdsResource,
            ComNomesResource,
        ]

    def __init__(self, *args, **kwargs):
        """Método para executarmos ações ao iniciar a classe."""
        super().__init__(*args, **kwargs)
        self.filter_horizontal = self.get_filter_horizontal()
