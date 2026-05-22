import re
from datetime import datetime, date

from dateutil.relativedelta import relativedelta

from root.flask import database
from root.flask.recursos.models import BaseModel, ActiveMixin, PersonMixin, AddressMixin, TimestampMixin


class Consulta(BaseModel):
    funcionario = database.relationship('Funcionario', backref='consultas_realizadas')

    primeiro_contato = database.Column(database.DateTime, nullable=False, default=datetime.now)
    triagem = database.Column(database.DateTime, nullable=True)
    modalidade = database.Column(database.String(100), nullable=False)
    descricao = database.Column(database.Text, nullable=True)

    prontuario_id = database.Column(database.Integer, database.ForeignKey('prontuario.id'), nullable=False)
    funcionario_id = database.Column(database.Integer, database.ForeignKey('funcionario.id'), nullable=False)

class Prontuario(BaseModel, ActiveMixin, PersonMixin, AddressMixin, TimestampMixin):
    funcionario = database.relationship('Funcionario', backref='prontuarios_registados')
    consultas = database.relationship('Consulta', backref='prontuario_pai', lazy=True, cascade="all, delete-orphan")

    funcionario_id = database.Column(database.Integer, database.ForeignKey('funcionario.id'), nullable=False)
    internacao = database.Column(database.DateTime, nullable=False, default=datetime.now)
    data_saida = database.Column(database.Date, nullable=True)
    motivo_saida = database.Column(database.String, nullable=True)

    escolaridade = database.Column(database.String, nullable=False)
    profissao = database.Column(database.String, nullable=True)
    religiao = database.Column(database.String, nullable=True)
    mae = database.Column(database.String, nullable=False)
    estado_civil = database.Column(database.String, nullable=False)
    conjuge = database.Column(database.String, nullable=True)
    convenio = database.Column(database.String, nullable=False)

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
