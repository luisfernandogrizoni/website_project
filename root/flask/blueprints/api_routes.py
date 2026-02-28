from datetime import datetime, date

from flask import jsonify, Blueprint, request, flash, url_for, redirect
from flask_login import login_required
from flask_wtf import csrf

from root.flask import database
from root.flask.forms import FormConsulta
from root.flask.models import Consulta, Funcionario, Categoria, Prontuario
from root.flask.utils import roles_required, limpar_numeros, db_persist

api_bp = Blueprint('api', __name__)
url_prefix = '/api'

@api_bp.route("/api/agendamentos")
@roles_required(['Admin', 'Social'])
def api_agendamentos():
    resultados = database.session.query(
        Consulta, Funcionario, Categoria
    ).join(
        Funcionario, Consulta.funcionario_id == Funcionario.id
    ).join(
        Categoria, Consulta.categoria_id == Categoria.id
    ).all()

    eventos = []
    for consulta, func, cat in resultados:
        cor = '#3788d8'
        if 'Triagem' in cat.tipo:
            cor = '#28a745'
        elif 'Internação' in cat.tipo:
            cor = '#dc3545'
        eventos.append({
            'id': consulta.id,
            'title': f"{consulta.nome} ({cat.tipo})",
            'start': consulta.hora.isoformat(),
            'extendedProps': {
                'funcionario': func.nome,
                'descricao': consulta.descricao,
                'categoria': cat.tipo
            },
            'color': cor
        })

    return jsonify(eventos)

@api_bp.route("/api/agendamentos/novo", methods=["POST"])
@roles_required(['Admin', 'Social'])
def api_criar_agendamento():
    form = FormConsulta()
    form.funcionario.choices = [(f.id, f.nome) for f in Funcionario.query.all()]
    form.categoria.choices = [(c.id, c.tipo) for c in Categoria.query.all()]

    if form.validate_on_submit():
        agendamento = Consulta()
        form.populate_obj(agendamento)
        agendamento.funcionario_id=form.funcionario.data
        agendamento.categoria_id=form.categoria.data

        database.session.add(agendamento)

        if db_persist(agendamento, f'Agendamento registrado com sucesso!', 'success'):
            return redirect(url_for("social.agenda"))

    elif request.method == "POST":
        flash('Houve um erro no formulário. Verifique os campos em vermelho.', 'danger')

    return jsonify({'status': 'error', 'errors': form.errors}), 400

@api_bp.route('/api/paciente/<int:id>', methods=['GET'])
@roles_required(['Admin', 'Social'])
def api_detalhes_paciente(id):
    try:
        prontuario = Prontuario.query.get_or_404(id)
        return jsonify(prontuario.to_dict())

    except Exception as e:
        print(f"Erro na API: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/paciente/<int:id>/edicao', methods=['PATCH'])
@roles_required(['Admin', 'Social'])
def edicao_prontuario(id):
    prontuario = Prontuario.query.get_or_404(id)
    data = request.get_json()

    try:
        prontuario.update_from_dict(data)

        database.session.commit()
        return jsonify({'message': 'Dados atualizados com sucesso!'}), 200

    except ValueError as ve:
        return jsonify({'error': 'Erro na API!'}), 400
    except Exception as e:
        database.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@api_bp.route('/api/paciente/<int:id>/baixa', methods=['PATCH'])
@roles_required(['Admin', 'Social'])
def inativar_prontuario(id):
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

