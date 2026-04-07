import click
from flask.cli import with_appcontext


@click.command("popular-banco")
@with_appcontext
def popular_banco_command():
    """Popula o banco de dados com os cargos e o usuário Admin."""
    from root.flask.extensions import database, bcrypt
    from root.flask.models import Cargo, Funcionario

    print("--- Criando Cargos ---")
    c_admin = Cargo(nome='Admin')
    c_social = Cargo(nome='Assistente Social')
    c_adm = Cargo(nome='Administrativo')

    database.session.add_all([c_admin, c_social, c_adm])
    database.session.commit()
    print(f"✓ Cargos criados! ID Admin: {c_admin.id}")

    print("--- Criando Usuários ---")
    senha_padrao = bcrypt.generate_password_hash('123456').decode('utf-8')

    admin = Funcionario(
        nome='Administrador Supremo',
        cpf='000.000.000-00',
        rg='00.000.000-0',
        contratacao='CLT',
        email='admin@sistema.com',
        senha=senha_padrao,
        cargo_id=c_admin.id,
        ativo=True
    )

    try:
        database.session.add(admin)
        database.session.commit()
        print("Sucesso! Tabelas populadas.")
        print("Login Admin: admin@sistema.com | Senha: 123456")
    except Exception as e:
        database.session.rollback()
        print(f"Erro ao salvar: {e}")

def gerador_senha():
    import secrets
    import string
    from datetime import datetime


    def gerar_senha_segura():
        user = int(input("Digite o tamanho da senha (Token = 42): "))
        tamanho = user
        alfabeto = string.ascii_letters + string.digits + string.punctuation
        senha = ''.join(secrets.choice(alfabeto) for _ in range(tamanho))
        return senha


    def salvar_senha(senha, nome_arquivo="senhas.txt"):
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with open(nome_arquivo, 'a', encoding='utf-8') as arquivo:
                nome = input("Digite finalidade da senha: ")
                linha = f"[{data_hora}] | {nome} Senha: {senha}\n"
                arquivo.write(linha)
                print(f"Senha salva com sucesso em '{nome_arquivo}'")

        except IOError as e:
            print(f"Erro ao salvar o arquivo: {e}")


    if __name__ == "__main__":
        print("--- Gerador de Senhas Seguro ---")

        while True:
            resposta = input("Pressione ENTER para gerar uma senha (ou digite 'sair'): ")
            if resposta.lower() == 'sair':
                break

            nova_senha = gerar_senha_segura()
            print(f"Senha Gerada: {nova_senha}")

            salvar_senha(nova_senha)


def limpar_numeros(valor: str | None) -> str | None:
    import re
    if not valor:
        return None
    return re.sub(r'\D', '', str(valor))

def roles_required(lista_cargos_permitidos):
    from functools import wraps

    from flask import flash, redirect, url_for
    from flask_login import current_user

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Acesso negado. Você precisa estar logado.", "warning")
                return redirect(url_for("main.login"))
            if not current_user.cargo_obj or current_user.cargo_obj.nome not in lista_cargos_permitidos:
                flash(f'Acesso negado. Esta página é restrita.', "danger")
                return redirect(url_for("main.inicio", id_func=current_user.id))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return roles_required(['Admin'])(f)

def db_persist(objeto, msg_sucesso="Operação realizada com sucesso!", action='add'):
    from flask import flash, current_app
    from root.flask import database

    try:
        if action == 'add':
            database.session.add(objeto)
        elif action == 'delete':
            database.session.delete(objeto)

        database.session.commit()
        flash(msg_sucesso, 'success')
        return True

    except Exception as e:
        database.session.rollback()
        current_app.logger.error(f"Erro no banco de dados: {str(e)}")
        flash('Ocorreu um erro interno. Tente novamente.', 'danger')
        return False

