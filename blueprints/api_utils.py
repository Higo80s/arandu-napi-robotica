from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required
from flask_wtf.csrf import generate_csrf

api_utils_bp = Blueprint('api_utils', __name__)

@api_utils_bp.route('/api/refresh_csrf', methods=['GET'])
@login_required # Garante que usuario esta logado na sessao (cookie)
def refresh_csrf():
    """
    Retorna um novo token CSRF.
    Usado pela pagina de recuperacao de erro CSRF para obter um token valido
    apos o usuario fazer login em outra aba.
    """
    token = generate_csrf()
    return jsonify({'csrf_token': token})
