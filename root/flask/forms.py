import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, DateTimeField, TextAreaField, FloatField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from root.flask.models import Funcionario, Prontuario, Categoria, Cargo
from .constants import ESTADO_CIVIL, CONVENIO, UF,ESCOLARIDADE

class AppDateField(DateField):
    def __init__(self, label=None, validators=None, format="%Y-%m-%d", **kwargs):
        super(AppDateField, self).__init__(label, validators, format=format, **kwargs)

class AppDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format="%Y-%m-%dT%H:%M", **kwargs):
        super(AppDateTimeField, self).__init__(label, validators, format=format, **kwargs)

class Unique(object):
    def __init__(self, model, field, message="Este dado já está cadastrado."):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        limpar_numericos = re.sub(r'\D', '', field.data) if 'cpf' in field.name or 'rg' in field.name else field.data
        obj = self.model.query.filter(self.field == limpar_numericos).first()
        if obj:
            if hasattr(form, 'id') and form.id.data and int(form.id.data) == str(obj.id):
                return
            raise ValidationError(self.message)



class FormCargo(FlaskForm):
    nome = StringField("Cargo", validators=[DataRequired(), Unique(Cargo, Cargo.nome)])
    botao_confirmacao = SubmitField("Salvar")


class FormFuncionario(FlaskForm):
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
    cargo = SelectField("Cargo", coerce=int, validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField("Confirmação de Senha", validators=[DataRequired(), EqualTo("senha")])
    botao_confirmacao = SubmitField("Cadastrar")

class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_confirmacao = SubmitField("Entrar")

class FormProntuario(FlaskForm):
    data_internacao = AppDateField("Data de Internação", validators=[DataRequired()])
    data_nascimento = AppDateField("Data de Nascimento", validators=[DataRequired()])


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


class FormCategoria(FlaskForm):
    tipo = StringField("Nome da Categoria", validators=[DataRequired(), Unique(Categoria, Categoria.tipo)])
    botao_confirmacao = SubmitField("Criar Categoria")


class FormConsulta(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[Optional()])
    hora = AppDateTimeField("Horário", validators=[DataRequired()])
    triagem = AppDateTimeField("Triagem", validators=[Optional()])
    internacao = AppDateTimeField("Internação", validators=[Optional()])

    funcionario = SelectField("Profissional", coerce=int, validators=[DataRequired()])
    categoria= SelectField("Categoria", coerce=int, validators=[DataRequired()])

    botao_confirmacao = SubmitField("Agendar")



