from django.db.models.query import QuerySet
from rest_framework import serializers
from rest_framework.fields import empty


class NovadataModelSerializer(serializers.ModelSerializer):
    representation_fields: list = []

    def to_representation(self, instance):
        """Função para definir os campos de representação."""
        if (
            instance
            and not isinstance(instance, list)
            and not isinstance(instance, QuerySet)
        ):
            default_return = super(
                NovadataModelSerializer, self
            ).to_representation(instance)

            if self.representation_fields:
                only_fields_representation = filter(
                    lambda field: field[0] in self.fields,
                    self.representation_fields,
                )

                for field_name, serializer in only_fields_representation:
                    default_return[field_name] = serializer(
                        getattr(instance, field_name)
                    ).data

            return default_return

    def get_fields(self):
        """
        Função para retornar só uma parte dos campos.

        Se o usuário passar a propriedade fields na querystring, ele vai
        retornar só os campos que foram passados.
        """
        fields = super().get_fields()
        request = self.context.get("request", None)
        if not request or not request.query_params:
            return fields

        param_fields = request.query_params.get("fields", None)

        if param_fields:
            list_param_fields = param_fields.split(",")
            trated_param_fields = [
                field_name.strip() for field_name in list_param_fields
            ]

            fields = {
                field_name: field
                for field_name, field in fields.items()
                if field_name in trated_param_fields
            }

        return fields

    def __init__(self, instance=None, data=empty, **kwargs):
        """Método para executarmos ações ao iniciar a classe."""
        super(NovadataModelSerializer, self).__init__(instance, data, **kwargs)
        self.to_representation(instance)
