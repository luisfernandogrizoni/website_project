import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from root.flask.extensions import database, login_manager
from flask_login import UserMixin

base = declarative_base()

@login_manager.user_loader
def load_user(id_funcionario):
    return Funcionario.query.get(int(id_funcionario))

class BaseModel(database.Model):
    __abstract__ = True
    id = database.Column(database.Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    @declared_attr
    def __table_args__(cls):
        return {'extend_existing': True}

    def __repr__(self):
        name_val = getattr(self, 'nome', getattr(self, 'descricao', ''))
        return f"<{self.__class__.__name__} {self.id} - {name_val}>"

class ActiveMixin:
    ativo = database.Column(database.Boolean, nullable=False, default=True)

    def desativar(self):
        self.ativo = False

    def ativar(self):
        self.ativo = True

class AddressMixin:
    cep = database.Column(database.String(9), nullable=True)
    cidade = database.Column(database.String(100), nullable=True)
    estado = database.Column(database.String(2), nullable=True)
    rua = database.Column(database.String(200), nullable=True)
    num = database.Column(database.String(20), nullable=True)
    bairro = database.Column(database.String(100), nullable=True)

    @property
    def endereco(self):
        return f'{self.cidade}, {self.estado}- Rua: {self.rua}, {self.num}.{self.bairro} - CEP: {self.cep}'

class PersonMixin:
    nome = database.Column(database.String(200), nullable=False)
    cpf = database.Column(database.String(11), nullable=False, unique=True)
    rg = database.Column(database.String(20), nullable=False, unique=True)
    data_nascimento = database.Column(database.Date, nullable=True)

    @property
    def primeiro_nome(self):
        return self.nome.split()[0] if self.nome else ""

class TimestampMixin:
    criado_em = database.Column(database.DateTime, default=datetime.now, nullable=False)
    atualizado_em = database.Column(database.DateTime, onupdate=datetime.now)

class Cargo(BaseModel):
    nome = database.Column(database.String(100), nullable=False)

    funcionarios = database.relationship("Funcionario", backref='cargo_obj', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cargo {self.nome}>"

class Funcionario(BaseModel, UserMixin, ActiveMixin, PersonMixin, TimestampMixin, AddressMixin):
    contratacao = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    cargo_id = database.Column(database.Integer, database.ForeignKey('cargo.id'), nullable=False)

    consulta = database.relationship('Consulta', backref='funcionario', lazy=True, cascade="all, delete-orphan")
    baixa = database.relationship('Prontuario', backref='funcionario', lazy=True, cascade="all, delete-orphan")

    @property
    def cargo_nome(self):
        return self.cargo_obj.nome if self.cargo_obj else None

    def is_admin(self):
        return self.cargo_nome == 'Admin'


class Prontuario(BaseModel, ActiveMixin, PersonMixin, AddressMixin, TimestampMixin):
    funcionario_id = database.Column(database.Integer, database.ForeignKey('funcionario.id'), nullable=False)

    data_internacao = database.Column(database.DateTime, nullable=False, default=datetime.now)
    data_saida = database.Column(database.Date, nullable=True)
    motivo_saida = database.Column(database.String, nullable=True)

    convenio = database.Column(database.String, nullable=False)
    escolaridade = database.Column(database.String, nullable=False)
    profissao = database.Column(database.String, nullable=True)
    religiao = database.Column(database.String, nullable=True)
    mae = database.Column(database.String, nullable=False)
    estado_civil = database.Column(database.String, nullable=False)
    conjuge = database.Column(database.String, nullable=True)

    cartao_sus = database.Column(database.String, nullable=True)

    responsavel = database.Column(database.String)
    relacao = database.Column(database.String, nullable=False, default='Não Informado')
    cpf_resp = database.Column(database.String(11), nullable=False, unique=True, default='Não Informado')
    rg_resp = database.Column(database.String(9), nullable=False, unique=True, default='Não Informado')
    contato = database.Column(database.String, nullable=False, default='Não Informado')
    contato_dois = database.Column(database.String, nullable=True, default='Não Informado')
    contrib = database.Column(database.String, nullable=True, default='SUS')

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        hoje = date.today()
        age = hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return age

    @property
    def tempo_permanencia(self):
        inicio = self.data_internacao.date() if isinstance(self.data_internacao, datetime) else self.data_internacao
        fim = self.data_saida if self.data_saida else date.today()

        delta = relativedelta(fim, inicio)

        texto = []
        if delta.years > 0: texto.append(f"{delta.years} anos")
        if delta.months > 0: texto.append(f"{delta.months} meses")
        if delta.days > 0: texto.append(f"{delta.days} dias")

        return ", ".join(texto) if texto else "Não ficou"

    @property
    def previsao_alta(self):
        if not self.data_internacao:
            return None
        return self.data_internacao + relativedelta(months=9)

    def to_dict(self):
        def fmt_date(d):
            return d.strftime('%Y-%m-%d') if d else ""
        def fmt_str(s):
            return s if s else '-'
        campos_texto = [
            'nome', 'cpf', 'rg', 'mae', 'cartao_sus', 'escolaridade',
            'profissao', 'religiao', 'estado_civil', 'conjuge', 'bairro',
            'cidade', 'estado', 'contato', 'contato_dois', 'responsavel',
            'cpf_resp', 'rg_resp', 'relacao', 'contrib', 'convenio',
            'motivo_saida'
        ]
        campos_data = [
            'data_nascimento', 'data_internacao'
        ]

        data = {campo: fmt_str(getattr(self, campo)) for campo in campos_texto}
        data.update({campo: fmt_date(getattr(self,campo)) for campo in campos_data})
        data.update({
            'id': self.id,
            'ativo': self.ativo,
            'idade': self.idade if self.data_nascimento else '-',
            'endereco_completo': f"{fmt_str(self.rua)}, {fmt_str(self.num)}",
            'previsao_alta': fmt_date(self.previsao_alta) if self.data_saida else None,
            'data_saida': fmt_date(self.data_saida) if self.data_saida else None,
            'tempo_permanencia': self.tempo_permanencia if self.tempo_permanencia else None,
        })
        return data

    def update_from_dict(self, data):
        campos_texto = [
            'nome', 'responsavel', 'relacao', 'religiao', 'escolaridade',
            'profissao', 'estado_civil', 'convenio', 'contrib', 'motivo_saida',
            'cidade', 'estado', 'rua', 'num', 'bairro', 'contato', 'contato_dois'
        ]
        for campo in campos_texto:
            if campo in data:
                setattr(self, campo, data.get(campo))

        campos_numericos = ['cpf', 'rg', 'cartao_sus', 'cpf_resp', 'rg_resp']
        for campo in campos_numericos:
            if campo in data:
                valor_bruto = data.get(campo)
                valor_limpo = re.sub(r'\D', '', str(valor_bruto)) if valor_bruto else None
                setattr(self, campo, valor_limpo)

        campos_data = ['data_nascimento', 'data_internacao', 'data_saida']
        for campo in campos_data:
            if campo in data:
                valor = data.get(campo)
                if valor:
                    setattr(self, campo, datetime.strptime(valor, '%Y-%m-%d').date())
                else:
                    setattr(self, campo, None)

class Categoria(BaseModel):

    tipo = database.Column(database.String(100), nullable=False, unique=True)
    consultas = database.relationship('Consulta', backref='categoria', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Categoria{self.tipo}"

class Consulta(BaseModel):
    nome = database.Column(database.String(200), nullable=False)
    descricao = database.Column(database.Text, nullable=True)
    triagem = database.Column(database.DateTime, nullable=True)
    internacao = database.Column(database.DateTime, nullable=True)
    hora = database.Column(database.DateTime, nullable=False, default=datetime.now)

    categoria_id = database.Column(database.Integer, database.ForeignKey('categoria.id'), nullable=False)
    funcionario_id = database.Column(database.Integer, database.ForeignKey('funcionario.id'), nullable=False)

    def __repr__(self):
        return f"Nome: {self.nome}, Triagem: {self.triagem}, Internação: {self.internacao}, Hora: {self.hora}, Categoria: {self.categoria_id})"

