from flask import Blueprint, flash, redirect, url_for, current_app, request, render_template

from root.flask import database, bcrypt
from root.flask.forms import FormFuncionario, FormCargo
from root.flask.models import Funcionario, Cargo
from root.flask.utils import roles_required, limpar_numeros, db_persist

# ------------------- ADMINISTRAÇÃO DO SISTEMA ------------------- #

admin_bp = Blueprint('admin', __name__)
url_prefix = ('/administrador') # Prefixo lógico para agrupar as rotas na URL

@admin_bp.route("/cargo/novo", methods=["GET", "POST"])
@roles_required(['Admin'])
def cargo_novo():
    """Gere a criação de novos níveis de acesso (Roles) no sistema."""
    form = FormCargo()
    if form.validate_on_submit():
        cargo = Cargo()
        cargo.nome = form.nome.data

        database.session.add(cargo)
        # db_persist lida com o commit e possíveis erros de banco centralizadamente
        if db_persist(cargo, f'Cargo {cargo.nome} cadastrado com sucesso!', 'sucess'):
            return redirect(url_for("admin.novo_funcionario"))

    elif request.method == 'POST':
        flash('Houve um erro no formulário. Verifique os campos em vermelho.', 'danger')
    return render_template("cadastro_cargos.html", form=form)

@admin_bp.route("/funcionario/novo", methods=["GET", "POST"])
@roles_required(['Admin'])
def novo_funcionario():
    """
        Criação de novos utilizadores.
        Aplica a limpeza de dados sensíveis (limpar_numeros) e encripta a password antes de persistir.
    """
    form = FormFuncionario()
    # Popula o SelectField dinamicamente consultando a tabela Cargo
    form.cargo.choices = [(c.id, c.nome) for c in Cargo.query.all()]

    if form.validate_on_submit():
        funcionario = Funcionario()
        form.populate_obj(funcionario)

        # Sobrescrita de dados limpos após o populate_obj automático
        funcionario.cargo_id = form.cargo.data
        funcionario.cpf = limpar_numeros(form.cpf.data)
        funcionario.rg = limpar_numeros(form.rg.data)
        funcionario.senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')

        database.session.add(funcionario)
        if db_persist(funcionario, f'Funcionário {funcionario.nome} cadastrado com sucesso!', 'success'):
                return redirect(url_for("main.inicio"))

    elif request.method == 'POST':
        flash('Houve um erro no formulário. Verifique os campos em vermelho.', 'danger')

    return render_template("cadastro_funcionario.html", form_funcionario=form)