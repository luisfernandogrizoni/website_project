import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, DateTimeField, TextAreaField, FloatField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from root.flask.models import Funcionario, Prontuario, Cargo
from .constants import ESTADO_CIVIL, CONVENIO, UF,ESCOLARIDADE

# ------------------- CAMPOS PERSONALIZADOS (Overrides) ------------------- #

class AppDateField(DateField):
    """
        Padroniza o formato de data (Ano-Mês-Dia) para todo o sistema.
        Garante que a comunicação entre o input <type="date"> do HTML5 e o backend não quebre.
    """
    def __init__(self, label=None, validators=None, format="%Y-%m-%d", **kwargs):
        super(AppDateField, self).__init__(label, validators, format=format, **kwargs)

class AppDateTimeField(DateTimeField):
    """
        Padroniza o formato de data e hora (Ano-Mês-Dia T Hora:Minuto).
        Essencial para campos como o <input type="datetime-local">.
    """
    def __init__(self, label=None, validators=None, format="%Y-%m-%dT%H:%M", **kwargs):
        super(AppDateTimeField, self).__init__(label, validators, format=format, **kwargs)

# ------------------- VALIDADORES CUSTOMIZADOS ------------------- #

class Unique(object):
    """
        Validador para checar se um dado já existe no Banco de Dados.
        resolve o problema de colisão em Edições e lida com as máscaras do front-end.
    """
    def __init__(self, model, field, message="Este dado já está cadastrado."):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        # 1. LIMPEZA: Se for CPF ou RG, remove pontos e traços antes de buscar no banco.
        limpar_numericos = re.sub(r'\D', '', field.data) if 'cpf' in field.name or 'rg' in field.name else field.data

        # 2. CONSULTA: Procura no banco se a string existe.
        obj = self.model.query.filter(self.field == limpar_numericos).first()
        if obj:
            # 3. BYPASS DE EDIÇÃO: Se o formulário tiver um campo 'id' e for igual ao ID do banco, permitimos passar.
            if hasattr(form, 'id') and form.id.data and int(form.id.data) == str(obj.id):
                return
            # Se cair aqui, é porque o dado pertence a outra pessoa.
            raise ValidationError(self.message)

# ------------------- FORMULÁRIOS DE DOMÍNIO ------------------- #

class FormCargo(FlaskForm):
    """Cadastro de funções do sistema."""
    nome = StringField("Cargo", validators=[DataRequired(), Unique(Cargo, Cargo.nome)])
    botao_confirmacao = SubmitField("Salvar")

class FormFuncionario(FlaskForm):
    """
        Gerência de usuários do sistema.
        Usa o validador Unique para impedir emails, CPFs e RGs duplicados.
    """
    nome = StringField("Nome Completo", validators=[DataRequired()])
    cpf = StringField("CPF", validators=[DataRequired(), Unique(Funcionario, Funcionario.cpf)])
    rg = StringField("RG", validators=[DataRequired(), Unique(Funcionario, Funcionario.rg)])
    data_nascimento = AppDateField("Data de Nascimento", validators=[DataRequired()])

    cep = StringField("CEP", validators=[Optional(), Length(min=8, max=9)])
    cidade = StringField("Cidade", validators=[DataRequired()])
    estado = SelectField("Estado", choices=UF, validators=[DataRequired()])
    rua = StringField("Endereço", validators=[Optional()])
    num = StringField("Número", validators=[Optional()])
    bairro = StringField("Bairro", validators=[Optional()])

    contratacao = StringField("Tipo de Contratação", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Unique(Funcionario, Funcionario.email)])
    # coerce=int força a conversão do dado do HTML (string) para Integer (ID do banco)
    cargo = SelectField("Cargo", coerce=int, validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField("Confirmação de Senha", validators=[DataRequired(), EqualTo("senha")])
    botao_confirmacao = SubmitField("Cadastrar")

class FormLogin(FlaskForm):
    """Autenticação. Apenas validações básicas de formato."""
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_confirmacao = SubmitField("Entrar")

class FormProntuario(FlaskForm):
    """Validação de paciente e responsável."""
    data_internacao = AppDateField("Data de Internação", validators=[DataRequired()])
    data_nascimento = AppDateField("Data de Nascimento", validators=[DataRequired()])

    # Utilização de listas limpas vindas de constantes
    nome = StringField("Nome Completo", validators=[DataRequired()])
    cpf = StringField("Cadastro de Pessoa Física (CPF)", validators=[DataRequired(), Unique(Prontuario, Prontuario.cpf), Length(min=9, max=20)])
    rg = StringField("Registro Geral (RG)", validators=[DataRequired(), Unique(Prontuario, Prontuario.rg), Length(min=9, max=20)])
    cartao_sus = StringField("Cartao Sus", validators=[Optional(), Length(min=18, max=18)])

    convenio = SelectField("Convênio", choices=CONVENIO, validators=[DataRequired()])
    escolaridade = SelectField("Escolaridade", choices=ESCOLARIDADE, validators=[DataRequired()])
    profissao = StringField("Profissão", validators=[Optional()])
    religiao = StringField("Religião", validators=[Optional()])
    estado_civil = SelectField("Estado Civil", choices=ESTADO_CIVIL, validators=[DataRequired()])
    conjuge = StringField("Conjuge", validators=[Optional()])
    mae = StringField("Nome da Mãe", validators=[DataRequired()])

    cep = StringField("CEP", validators=[Optional(), Length(min=8, max=9)])
    cidade = StringField("Cidade", validators=[DataRequired()])
    estado = SelectField("Estado", choices=UF,validators=[DataRequired()])
    rua = StringField("Endereço", validators=[Optional()])
    num = StringField("Número", validators=[Optional()])
    bairro = StringField("Bairro", validators=[Optional()])


    responsavel = StringField("Nome Completo", validators=[DataRequired()])
    relacao = StringField("Relação/Parentesco", validators=[DataRequired()])
    cpf_resp = StringField("Cadastro de Pessoa Física (CPF)", validators=[DataRequired(), Unique(Prontuario, Prontuario.cpf_resp), Length(min=9, max=20)])
    rg_resp = StringField("Registro Geral (RG)", validators=[DataRequired(),  Unique(Prontuario, Prontuario.rg_resp), Length(min=9, max=20)])
    contrib = StringField("Contribuição Voluntária", validators=[Optional()])

    contato = StringField("Contato Principal", validators=[DataRequired()])
    contato_dois = StringField("Contato Secundário", validators=[Optional()])

    botao_confirmacao = SubmitField("Concluir")

class FormConsulta(FlaskForm):
    """Agendamentos. Relaciona dados temporais com as FKs (Profissional e Categoria)."""
    nome = StringField("Nome", validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[Optional()])
    # O AppDateTimeField facilita o parse do formato HTML5 local-datetime
    hora = AppDateTimeField("Horário", validators=[DataRequired()])
    triagem = AppDateTimeField("Triagem", validators=[Optional()])
    internacao = AppDateTimeField("Internação", validators=[Optional()])

    # Os choices destes SelectFields devem ser populados dinamicamente nas Rotas
    # (ex: form.funcionario.choices = [(f.id, f.nome) for f in Funcionario.query.all()])
    funcionario = SelectField("Profissional", coerce=int, validators=[DataRequired()])
    categoria= SelectField("Categoria", coerce=int, validators=[DataRequired()])

    botao_confirmacao = SubmitField("Agendar")



