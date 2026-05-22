import re
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from root.flask import database

base = declarative_base()

class BaseModel(database.Model):
    """
        Classe abstrata base (não vira tabela no banco).
        Todas as tabelas do sistema herdam dela para ganhar um ID padrão,
        nomenclatura automática (Snake Case) e evitar erros de importação circular.
    """
    __abstract__ = True
    id = database.Column(database.Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        # Converte NomeDaClasse para nome_da_classe automaticamente
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    @declared_attr
    def __table_args__(cls):
        # Evita erro de tabela duplicada quando o Flask recarrega no modo DEV
        return {'extend_existing': True}

    def __repr__(self):
        # Gera logs dinâmicos e legíveis no terminal (ex: <Funcionario 1 - Admin>)
        name_val = getattr(self, 'nome', getattr(self, 'descricao', ''))
        return f"<{self.__class__.__name__} {self.id} - {name_val}>"

# ------------------- MIXINS (Peças de Composição) ------------------- #

class ActiveMixin:
    """Adiciona o conceito de 'Soft Delete' (Exclusão Lógica). Dados nunca são apagados, apenas desativados."""
    ativo = database.Column(database.Boolean, nullable=False, default=True)

    def desativar(self):
        self.ativo = False

    def ativar(self):
        self.ativo = True

class AddressMixin:
    """Agrupa dados de endereço. Pode ser usado em Prontuario, Fornecedor, etc."""
    cep = database.Column(database.String(9), nullable=True)
    cidade = database.Column(database.String(100), nullable=True)
    estado = database.Column(database.String(2), nullable=True)
    rua = database.Column(database.String(200), nullable=True)
    num = database.Column(database.String(20), nullable=True)
    bairro = database.Column(database.String(100), nullable=True)

    @property
    def endereco(self):
        """Retorna o endereço completo formatado em uma única string."""
        return f'{self.cidade}, {self.estado}- Rua: {self.rua}, {self.num}.{self.bairro} - CEP: {self.cep}'

class PersonMixin:
    """Agrupa dados pessoais essenciais."""
    nome = database.Column(database.String(200), nullable=False)
    cpf = database.Column(database.String(11), nullable=False, unique=True)
    rg = database.Column(database.String(20), nullable=False, unique=True)
    data_nascimento = database.Column(database.Date, nullable=True)
    contato = database.Column(database.String(100), nullable=True)

    @property
    def primeiro_nome(self):
        """Extrai apenas o primeiro nome para uso na UI."""
        return self.nome.split()[0] if self.nome else ""

class TimestampMixin:
    """Rastreabilidade de auditoria: Registra automaticamente QUANDO foi criado e atualizado."""
    criado_em = database.Column(database.DateTime, default=datetime.now, nullable=False)
    atualizado_em = database.Column(database.DateTime, onupdate=datetime.now)