from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user

from root.flask import bcrypt
from root.flask.forms import FormLogin
from root.flask.models import Funcionario

# ------------------- AUTENTICAÇÃO E ROTEAMENTO BASE ------------------- #

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@login_required
def inicio():
    """Renderiza a tela inicial. Protegido para garantir que apenas utilizadores logados acessem."""
    return render_template("components/inicio.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """
        Controlador de Autenticação (AuthN).
        Verifica a existência do utilizador, o status da conta (Soft Delete) e a criptografia da password.
    """
    form_login = FormLogin()
    if form_login.validate_on_submit():
        func = Funcionario.query.filter_by(email=form_login.email.data).first()

        if func:
            if func.is_active: # Validação de segurança: Impede o acesso de utilizadores desativados
                if bcrypt.check_password_hash(func.senha, form_login.senha.data):
                    login_user(func, remember=True)
                    flash(f"Bem-vindo, {func.nome.split()[0].capitalize()[0]}!", category="success")
                    return redirect(url_for('main.inicio'))
                else:
                    flash('Senha incorreta. Tente novamente!', category="danger")

            else:
                flash("Sua conta está desativada. Entre em contato com o administrador.", "warning")
                return redirect(url_for("main.login"))
        else:
            flash("E-mail não está cadastrado. Verifique suas credenciais ou entre em contato com o suporte.", "danger")
    return render_template("auth/login.html", form=form_login)

@main_bp.route("/logout")
@login_required
def logout():
    """Sai da sessão atual do utilizador de forma segura."""
    logout_user()
    return redirect(url_for("main.login",))

