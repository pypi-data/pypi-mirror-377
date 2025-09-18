from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class LoginUsernameEmail(ModelBackend):
    def authenticate(self, request, **kwargs):
        """Função para autenticar o usuário."""
        try:
            user = (
                get_user_model()
                .objects.filter(
                    Q(username=kwargs["username"])
                    | Q(email=kwargs["username"])
                )
                .first()
            )
            return (
                user
                if user and user.check_password(kwargs["password"])
                else None
            )
        except KeyError:
            return None
