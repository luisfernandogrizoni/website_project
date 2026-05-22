from flask_login import UserMixin
from wtforms import DateField

from root.flask import database, login_manager
from root.flask.recursos.models import (BaseModel, PersonMixin, ActiveMixin)

@login_manager.user_loader
def load_user(id_funcionario):
    """Carrega o usuário logado na sessão do Flask a partir do seu ID."""
    return Funcionario.query.get(int(id_funcionario))
class AppDateField(DateField):
    """
        Padroniza o formato de data (Ano-Mês-Dia) para todo o sistema.
        Garante que a comunicação entre o input <type="date"> do HTML5 e o backend não quebre.
    """
    def __init__(self, label=None, validators=None, format="%Y-%m-%d", **kwargs):
        super(AppDateField, self).__init__(label, validators, format=format, **kwargs)


# ------------------- TABELAS REAIS (Entidades) ------------------- #

class Cargo(BaseModel):
    """Tabela de controle de acessos (Roles)."""
    nome = database.Column(database.String(100), nullable=False)
    # Relação 1:N (Um cargo para muitos funcionários)
    funcionarios = database.relationship("Funcionario", backref='cargo_obj', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cargo {self.nome}>"

class Funcionario(PersonMixin, BaseModel, UserMixin, ActiveMixin):
    """Usuários do sistema. Herda Soft Delete (ActiveMixin) e Funções de Login (UserMixin)."""
    contratacao = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    cargo_id = database.Column(database.Integer, database.ForeignKey('cargo.id'), nullable=False)

    @property
    def cargo_nome(self):
        """Atalho para pegar a string do nome do cargo através da chave estrangeira."""
        return self.cargo_obj.nome if self.cargo_obj else None

    def is_admin(self):
        """Validador rápido de privilégio máximo."""
        return self.cargo_nome == 'Admin'