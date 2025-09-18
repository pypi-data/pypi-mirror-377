from crum import get_current_user
from django.conf import settings
from django.db import models


class AbstractNovadataModel(models.Model):
    data_criacao = models.DateTimeField(
        verbose_name="Data de criação",
        auto_now_add=True,
    )

    data_atualizacao = models.DateTimeField(
        verbose_name="Data de atualização",
        auto_now=True,
    )

    usuario_criacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Usuário de criação",
        related_name="%(class)s_requests_created",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    usuario_atualizacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Usuário de atualização",
        related_name="%(class)s_requests_modified",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        """Sobrescrita do método save para realizarmos ações personalizadas."""
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.usuario_criacao = user
        self.usuario_atualizacao = user

        super(AbstractNovadataModel, self).save(*args, **kwargs)

    class Meta:
        """Sub classe para definir meta atributos da classe principal."""

        abstract = True
