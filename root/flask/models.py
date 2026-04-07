import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import declarative_base, backref
from sqlalchemy.ext.declarative import declared_attr
from root.flask.extensions import database, login_manager
from flask_login import UserMixin

base = declarative_base()
#todo: adicionar captação de id de funcionário automaticamente em todas as tabelas
# ------------------- UTILIDADES E BASE ------------------- #

@login_manager.user_loader
def load_user(id_funcionario):
    """Carrega o usuário logado na sessão do Flask a partir do seu ID."""
    return Funcionario.query.get(int(id_funcionario))

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

    consulta = database.relationship('Consulta', backref='funcionario', lazy=True, cascade="all, delete-orphan")
    baixa = database.relationship('Prontuario', backref='funcionario', lazy=True, cascade="all, delete-orphan")

    @property
    def cargo_nome(self):
        """Atalho para pegar a string do nome do cargo através da chave estrangeira."""
        return self.cargo_obj.nome if self.cargo_obj else None

    def is_admin(self):
        """Validador rápido de privilégio máximo."""
        return self.cargo_nome == 'Admin'

class Convenios(BaseModel, ActiveMixin, TimestampMixin):
    nome = database.Column(database.String, nullable=False)
    internos = database.relationship("Prontuario", backref='convenio_obj', lazy=True, cascade="all, delete-orphan")

class Consulta(BaseModel):
    primeiro_contato = database.Column(database.DateTime, nullable=False, default=datetime.now)
    triagem = database.Column(database.DateTime, nullable=True)
    modalidade = database.Column(database.String(100), nullable=False)
    descricao = database.Column(database.Text, nullable=True)

    prontuario_id = database.Column(database.Integer, database.ForeignKey('prontuario.id'), nullable=False)
    funcionario_id = database.Column(database.Integer, database.ForeignKey('funcionario.id'), nullable=False)

class Prontuario(BaseModel, ActiveMixin, PersonMixin, AddressMixin, TimestampMixin):
    funcionario_id = database.Column(database.Integer, database.ForeignKey('funcionario.id'), nullable=False)
    convenio_id = database.Column(database.Integer, database.ForeignKey('convenios.id'), nullable=False)
    consulta_id = database.relationship('Consulta', backref='consulta', lazy=True, cascade="all, delete-orphan")

    internacao = database.Column(database.DateTime, nullable=False, default=datetime.now)
    data_saida = database.Column(database.Date, nullable=True)
    motivo_saida = database.Column(database.String, nullable=True)

    escolaridade = database.Column(database.String, nullable=False)
    profissao = database.Column(database.String, nullable=True)
    religiao = database.Column(database.String, nullable=True)
    mae = database.Column(database.String, nullable=False)
    estado_civil = database.Column(database.String, nullable=False)
    conjuge = database.Column(database.String, nullable=True)

    cartao_sus = database.Column(database.String, nullable=True)

    responsavel = database.Column(database.String)
    relacao = database.Column(database.String, nullable=False, default='Não Informado')
    cpf_resp = database.Column(database.String(11), nullable=False, unique=True)
    rg_resp = database.Column(database.String(9), nullable=False, unique=True)
    contato_resp = database.Column(database.String, nullable=False, default='Não Informado')
    contato_dois = database.Column(database.String, nullable=True, default='Não Informado')
    contrib = database.Column(database.String, nullable=True, default='SUS')

    @property
    def convenio_nome(self):
        """Atalho para pegar a string do nome do convenio através da chave estrangeira."""
        return self.convenio_obj.nome if self.convenio_obj else None

    @property
    def idade(self):
        """Calcula a idade baseada na data de nascimento e data atual."""
        if not self.data_nascimento:
            return None
        hoje = date.today()
        age = hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return age

    @property
    def tempo_permanencia(self):
        """Calcula o tempo de internação usando relativedelta (anos, meses, dias)."""
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
        """Calcula a previsão de alta usando relativedelta (anos, meses, dias)."""
        if not self.data_internacao:
            return None
        return self.data_internacao + relativedelta(months=9)

    # --- PARSERS E SERIALIZADORES (Comunicação com a API) ---

    def to_dict(self):
        """
            Converte o objeto complexo do SQLAlchemy em um Dicionário JSON-friendly.
            Útil para enviar os dados para o Front-end preencher formulários via fetch/API.
        """
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
        """
                Processa o JSON recebido do Front-end em edições (PATCH/PUT).
                Separa a lógica de atualização garantindo que campos numéricos sofram Regex
                e campos de data sejam convertidos corretamente (String para DateTime).
        """
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

