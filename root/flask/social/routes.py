from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from root.flask import database
from root.flask.main.models import Funcionario
from root.flask.social.forms import FormProntuario, FormConsulta
from root.flask.social.models import Prontuario
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

    return render_template("social/prontuario.html", form=form)

@social_bp.route("/dados", methods=["GET", "POST"])
@login_required
def dados():
    """
        Dashboard de Prontuários.
        Separa logicamente os pacientes ativos dos inativos para não sobrecarregar as tabelas do front-end.
    """
    page_ativos = request.args.get('page_ativos', 1, type=int)
    page_inativos = request.args.get('page_inativos', 1, type=int)

    ativos = Prontuario.query.filter_by(ativo=True).paginate(page=page_ativos, per_page=15, error_out=False)
    inativos = Prontuario.query.filter_by(ativo=False).order_by(Prontuario.data_saida.desc()).paginate(page=page_inativos, per_page=15, error_out=False)
    return render_template("social/dados.html", lista_ativos=ativos, lista_inativos=inativos)

@social_bp.route("/agenda")
@login_required
def agenda():
    form = FormConsulta()
    form.funcionario.choices = [(f.id, f.nome) for f in
    Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()]
    form.categoria.choices = [(c.id, c.tipo) for c in Categoria.query.order_by(Categoria.tipo).all()]

    return render_template('social/agenda.html', form=form)


@social_bp.route('/api/paciente/<int:id>', methods=['GET'])
@roles_required(['Admin', 'Social'])
def api_detalhes_paciente(id):
    try:
        prontuario = Prontuario.query.get_or_404(id)
        return jsonify(prontuario.to_dict())

    except Exception as e:
        print(f"Erro na API: {e}")
        return jsonify({'error': str(e)}), 500

@social_bp.route('/api/paciente/<int:id>/edicao', methods=['PATCH'])
@roles_required(['Admin', 'Social'])
def edicao_prontuario(id):
    """
        Endpoint de Atualização Parcial (PATCH).
        Aplica a lógica de 'Early Return' para validar unicidade no banco
        antes de tentar atualizar o objeto.
    """
    prontuario = Prontuario.query.get_or_404(id)
    data = request.get_json()

    try:
        # 1. Validação Dinâmica de Colisões (Evita duplicar CPFs de outras pessoas)
        dados_sensiveis = ['cpf', 'rg', 'cpf_resp', 'rg_resp']
        for dicionario in dados_sensiveis:
            dado = data.get(dicionario)
            if dado:
                coluna_sql = getattr(Prontuario, dicionario)
                conflito = Prontuario.query.filter(
                    coluna_sql == dado,
                    Prontuario.id != id
                ).first()

                if conflito:
                    database.session.rollback()
                    # Early Return com status 409 (Conflict)
                    return jsonify(
                        {'error': f'O dado {dado.upper()} inserido já existe no banco. Por favor, verifique.'}), 409

        # 2. Persistência
        prontuario.update_from_dict(data)

        database.session.commit()
        return jsonify({'message': 'Dados atualizados com sucesso!'}), 200

    except ValueError as ve:
        return jsonify({'error': 'Erro na API!'}), 400
    except Exception as e:
        database.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@social_bp.route('/api/paciente/<int:id>/baixa', methods=['PATCH'])
@roles_required(['Admin', 'Social'])
def inativar_prontuario(id):
    """
        Implementação prática do padrão 'Soft Delete'.
        Não faz 'delete' no banco, apenas inativa e regista o motivo e data da saída (Auditoria).
    """
    prontuario = Prontuario.query.get_or_404(id)
    data = request.get_json()

    print(f"[LOG] Tentativa de baixa - ID: {id} | Motivo: {data.get('motivo')} | Data: {data.get('data_saida')}")
    if not isinstance(data.get('motivo'), str):
        print("[WARNING] Motivo recebido não é uma string válida.")

    motivo = data.get('motivo')
    data_saida_str = data.get('data_saida')

    if not motivo or not data_saida_str:
        return jsonify({'error': 'Motivo e Data de Saída são obrigatórios.'}), 400
    try:
        prontuario.ativo = False
        prontuario.motivo_saida = motivo
        prontuario.data_saida = datetime.strptime(data_saida_str, '%Y-%m-%d').date()

        database.session.commit()
        return jsonify({'message': 'Prontuário inativado com sucesso.'}), 200

    except Exception as e:
            database.session.rollback()
            return jsonify({'error': str(e)}), 500


@social_bp.route('/api/pacientes', methods=['GET'])
@roles_required(['Admin', 'Social'])
def api_pacientes(id):
    """
        [API Rest] Rota exclusiva para consumo do Front-End Moderno (CSR).
        Retorna a lista completa de pacientes convertida em dicionários (JSON).
        O filtro entre Ativos/Inativos será feito no JavaScript.
    """
    try:
        pacientes = Prontuario.query.all()
        dados_json = [p.to_dict() for p in pacientes]
        return jsonify(dados_json)

    except Exception as e:
        # Registre o erro no log do servidor
        print(f"Erro na API de Pacientes: {e}")
        return jsonify({"erro": "Falha ao buscar dados no servidor."}), 500

