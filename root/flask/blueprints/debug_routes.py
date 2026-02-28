import os
from flask import Blueprint, current_app, jsonify

from root.flask.utils import roles_required

debug_bp = Blueprint('debug', __name__)
url_prefix = '/debug'

@debug_bp.route('/static')
@roles_required(['Admin'])
def debug_arquivos():
    try:
        static_path = current_app.static_folder
        arvore = []

        for root, dirs, files in os.walk(static_path):
            pasta_atual = os.path.relpath(root, static_path)
            if pasta_atual == '.': pasta_atual = 'RAIZ (static)'

            arvore.append({
                'pasta': pasta_atual,
                'arquivos': files
            })

        return jsonify({
            'caminho_absoluto_static': static_path,
            'conteudo_encontrado': arvore
        })
    except Exception as e:
        return jsonify({'erro': str(e)})