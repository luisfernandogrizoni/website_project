from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from root.flask.main.forms import AppDateTimeField, Unique
from root.flask.social.models import Prontuario
from root.flask.constants import ESTADO_CIVIL, CONVENIO, UF,ESCOLARIDADE
from root.flask.main.models import AppDateField

class FormProntuario(FlaskForm):
    """Validação de paciente e responsável."""
    data_internacao = AppDateField("Data de Internação", validators=[DataRequired()])
    data_nascimento = AppDateField("Data de Nascimento", validators=[DataRequired()])

    # Utilização de listas limpas vindas de constantes
    nome = StringField("Nome Completo", validators=[DataRequired()])
    cpf = StringField("CPF", validators=[DataRequired(), Unique(Prontuario, Prontuario.cpf), Length(min=9, max=20)])
    rg = StringField("RG", validators=[DataRequired(), Unique(Prontuario, Prontuario.rg), Length(min=9, max=20)])
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


    responsavel = StringField("Responsável", validators=[DataRequired()])
    relacao = StringField("Relação/Parentesco", validators=[DataRequired()])
    cpf_resp = StringField("CPF do Responsável", validators=[DataRequired(), Unique(Prontuario, Prontuario.cpf_resp), Length(min=9, max=20)])
    rg_resp = StringField("RG do Responsável", validators=[DataRequired(),  Unique(Prontuario, Prontuario.rg_resp), Length(min=9, max=20)])
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