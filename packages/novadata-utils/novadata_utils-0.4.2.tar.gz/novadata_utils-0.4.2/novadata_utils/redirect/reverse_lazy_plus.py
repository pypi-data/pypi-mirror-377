from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode


def reverse_lazy_plus(
    url_name: str,
    url_params: list = [],
    get_params: dict = {},
    hash: str = "",
    just_uri: bool = False,
) -> HttpResponseRedirect:
    """
    Uma reverse_lazy 2.0.

    Aceita parâmetros GET e alguma #, Além de parâmetros de url.

    Caso desejse somente a url, ou seja, somente a string gerada
    (útil em funções como get_success_url), passe o último parâmetro
    (just_uri) como True.

    Usage::

        reverse_lazy_plus(
            'produto',
            url_params=[1, 'pedido_lente_contato'],
            get_params={'mensagem': 'Esta é uma mensagem'},
            '#aba-6',
        )
        # Output:
        # /produto/1/pedido_lente_contato?mensagem=Esta%20é%20uma%20mensagem#aba-6
    """
    url = reverse(url_name, args=url_params)
    params = urlencode(get_params).replace("+", " ")
    params = f"?{params}" if params else ""

    final_url = f"{url}{params}{hash}"
    return final_url if just_uri else HttpResponseRedirect(final_url)
