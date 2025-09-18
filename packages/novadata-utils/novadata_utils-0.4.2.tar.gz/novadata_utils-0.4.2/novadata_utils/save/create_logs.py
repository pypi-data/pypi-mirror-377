from pyclbr import Class

from crum import get_current_user


def create_logs(
    parent_object: object,
    back_update_fields: list,
    old_and_new_object: dict,
    log_class: Class,
    fk_name: str,
) -> list:
    """
    Função para criar objetos log para diferentes tipos de objetos pais.

    Parâmetros:
        parent_object: Objeto pai do log.
        back_update_fields: Lista de campos que foram alterados.
        old_and_new_object: Dicionário com os valores:
            old_object: Objeto antes do save.
            new_object: Objeto durante o save.
        log_class: Classe do log.
        fk_name: Nome do campo FK que está apontando para o pai no log.
    Retorna:
        Lista de objetos log criados.
    """

    def create_log_instance(field):
        """Cria uma instância de log para cada campo alterado."""
        valor_anterior = get_value(old_and_new_object["old_object"], field)
        valor_posterior = get_value(old_and_new_object["new_object"], field)

        instance = log_class(
            usuario=get_current_user(),
            campo_back=field.name,
            campo_front=field.verbose_name,
            valor_anterior=valor_anterior,
            valor_posterior=valor_posterior,
        )

        setattr(instance, fk_name, parent_object)
        return instance.save()

    return list(map(create_log_instance, back_update_fields))


def get_value(object, field):
    """Retorna o valor do campo do objeto."""
    display_name = f"get_{field.name}_display"
    has_display_name = hasattr(object, display_name)

    if has_display_name:
        return getattr(object, display_name)()
    else:
        return getattr(object, field.name)
