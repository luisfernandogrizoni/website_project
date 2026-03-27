from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from root.flask import database
from root.flask.models import Prontuario, Categoria, Funcionario, Consulta
from root.flask.forms import FormProntuario, FormConsulta
from root.flask.utils import limpar_numeros, roles_required, db_persist

# ------------------- OPERAÇÕES SOCIAIS (Apresentação) ------------------- #

social_bp = Blueprint('social', __name__)
url_prefix = '/social'

@social_bp.route("/prontuario", methods=["GET", "POST"])
@roles_required(['Social', 'Admin'])
def prontuario():
    form = FormProntuario()

    if form.validate_on_submit():
            prontuario = Prontuario(funcionario_id=current_user.id) # Rastreabilidade: Quem criou?
            form.populate_obj(prontuario)

            # Limpeza manual de dados críticos antes de persistir
            prontuario.cpf = limpar_numeros(form.cpf.data)
            prontuario.rg = limpar_numeros(form.rg.data)
            prontuario.cpf_resp = limpar_numeros(form.cpf_resp.data)
            prontuario.rg_resp = limpar_numeros(form.rg_resp.data)
            prontuario.cartao_sus = limpar_numeros(form.cartao_sus.data)

            database.session.add(prontuario)

            if db_persist(prontuario, f'Interno {prontuario.nome} cadastrado com sucesso!', 'success'):
                return redirect(url_for("social.dados"))

    elif request.method == 'POST':
        flash('Houve um erro no formulário. Verifique os campos em vermelho.', 'danger')

    return render_template("prontuario.html", form=form)

@social_bp.route("/dados", methods=["GET", "POST"])
@login_required
def dados():
    """
        Dashboard de Prontuários.
        Separa logicamente os pacientes ativos dos inativos para não sobrecarregar as tabelas do front-end.
    """
    ativos = Prontuario.query.filter_by(ativo=True).all()
    inativos = Prontuario.query.filter_by(ativo=False).order_by(Prontuario.data_saida.desc()).all()
    return render_template("dados.html", lista_ativos=ativos, lista_inativos=inativos)

@social_bp.route("/agenda")
@login_required
def agenda():
    form = FormConsulta()
    form.funcionario.choices = [(f.id, f.nome) for f in
    Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()]
    form.categoria.choices = [(c.id, c.tipo) for c in Categoria.query.order_by(Categoria.tipo).all()]

    return render_template('agenda.html', form=form)


