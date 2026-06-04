from django.db import models
from django.contrib.auth.models import User


class ProposicaoFavorita(models.Model):
    """Projetos de lei favoritados por cada usuário."""
    usuario         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    id_proposicao   = models.IntegerField()
    sigla_tipo      = models.CharField(max_length=20, blank=True)
    numero          = models.IntegerField(null=True, blank=True)
    ano             = models.IntegerField(null=True, blank=True)
    ementa          = models.TextField(blank=True)
    situacao        = models.CharField(max_length=200, blank=True)
    criado_em       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'id_proposicao')
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.sigla_tipo} {self.numero}/{self.ano} – {self.usuario}"
