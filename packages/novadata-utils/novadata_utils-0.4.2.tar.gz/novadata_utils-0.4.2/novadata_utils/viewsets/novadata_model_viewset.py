from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from novadata_utils.functions import get_prop, props_dict

from .novadata_pagination import NovadataPagination


class NovadataModelViewSet(viewsets.ModelViewSet):
    pagination_class = NovadataPagination

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields: list = None

    ordering_fields: list = None

    search_fields: list = None

    auto_search_fields: bool = True

    list_select_related: list = None

    relation_fields = [
        "OneToOneField",
        "ForeignKey",
    ]

    def get_queryset(self):
        """Define o queryset."""
        model = self.serializer_class().Meta.model
        return model.objects.select_related(
            *self.list_select_related,
        ).all()

    def get_filterset_fields(self):
        """Retorna os campos de filtro."""
        model = self.serializer_class().Meta.model
        list_filterset_fields = get_prop(
            model,
            "filterset_fields",
            annotate_type=True,
        )

        dict_filterset_fields = {}
        for filterset_field in list_filterset_fields:
            name = filterset_field["name"]
            type = filterset_field["type"]

            sub_props = props_dict.get(type, [])
            dict_filterset_fields[name] = sub_props

        return dict_filterset_fields

    def get_ordering_fields(self):
        """Retorna os campos de ordenação."""
        model = self.serializer_class().Meta.model
        ordering_fields = get_prop(
            model,
            "ordering_fields",
        )

        return ordering_fields

    def get_search_fields(self):
        """Retorna os campos de busca."""
        model = self.serializer_class().Meta.model
        list_search_fields = get_prop(
            model,
            "search_fields",
            annotate_type=True,
        )

        dict_search_fields = {}
        for search_field in list_search_fields:
            name = search_field["name"]
            type = search_field["type"]

            sub_props = props_dict.get(type, [])
            dict_search_fields[name] = sub_props

        return dict_search_fields

    def get_list_select_related(self):
        """Retorna os campos do select_related."""
        model = self.serializer_class().Meta.model
        list_select_related = get_prop(
            model,
            "list_select_related",
        )

        return list_select_related

    def get_fk_fields(self):
        """Retorna os campos de relacionamento."""
        model = self.serializer_class().Meta.model
        fields = model._meta.get_fields()
        fk_fields = [
            (field.name, field.remote_field.model)
            for field in fields
            if field.get_internal_type() in self.relation_fields
        ]

        return fk_fields

    def get_data(self, request):
        """Retorna os dados da requisição de forma tratada."""
        if request.FILES:
            # Não faz `.copy()` para evitar erro com arquivos
            data = request.data
        else:
            # Mantém `.copy()` apenas quando seguro
            data = request.data.copy()

        for fk_field in self.get_fk_fields():
            field_name = fk_field[0]
            try:
                if isinstance(data[field_name], dict):
                    data[field_name] = data[field_name].get(
                        "id",
                        None,
                    )
            except KeyError:
                pass
                # print(f"Não passou {field_name}")

        return data

    def create(self, request, *args, **kwargs):
        """Realiza o create de um objeto."""
        serializer = self.get_serializer(data=self.get_data(request))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        """Realiza o update de um objeto."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = self.get_data(request)

        obj_datas = {}
        for field in self.get_fk_fields():
            field_name = field[0]
            obj_datas[field_name] = data.get(
                field_name,
                None,
            )

        serializer = self.get_serializer(
            instance,
            data=data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        for field in self.get_fk_fields():
            field_name = field[0]

            try:
                model = field[1]
                obj_data = obj_datas[field_name]
                if obj_data:
                    if isinstance(obj_data, dict):
                        fk_instance = model.objects.get(
                            pk=obj_data.get("id", None)
                        )
                    elif isinstance(obj_data, list):
                        fk_instance = model.objects.get(pk=obj_data[0])
                    else:
                        fk_instance = model.objects.get(pk=obj_data)

                    setattr(serializer.instance, field_name, fk_instance)
            except model.DoesNotExist:
                pass
                # print(f"Não passou {field_name}")

        self.perform_update(serializer)

        # Estava salvando o objeto duas vezes.
        # serializer.instance.save()

        return Response(serializer.data)

    def __init__(self, **kwargs) -> None:
        """Método para executarmos ações ao iniciar a classe."""
        super().__init__(**kwargs)
        if not self.filterset_fields:
            self.filterset_fields = self.get_filterset_fields()

        if not self.ordering_fields:
            self.ordering_fields = self.get_ordering_fields()

        if self.auto_search_fields and not self.search_fields:
            self.search_fields = self.get_search_fields()

        if not self.list_select_related:
            self.list_select_related = self.get_list_select_related()
