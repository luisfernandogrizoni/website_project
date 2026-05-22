import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional

from root.flask.main.models import Funcionario, Cargo, AppDateField
from root.flask.constants import UF

# ------------------- CAMPOS PERSONALIZADOS (Overrides) ------------------- #
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