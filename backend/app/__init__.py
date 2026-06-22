"""
MiroFish Backend - Flask应用工厂
"""

import os
import warnings

# 抑制 multiprocessing resource_tracker 的警告（来自第三方库如 transformers）
# 需要在所有其他导入之前设置
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request, jsonify
from flask_cors import CORS

from .config import Config
from .utils.logger import setup_logger, get_logger


# Orígenes permitidos (constante a nivel de módulo para acceso desde error handlers)
ALLOWED_ORIGINS = [
    "https://mirofish-tan.vercel.app",
    "https://mirofish.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Métodos y headers CORS permitidos
CORS_METHODS = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
CORS_HEADERS = "Content-Type, Authorization, X-Requested-With, Accept"


def _add_cors_to_response(response, origin=None):
    """Agrega headers CORS a una respuesta. Segura: nunca lanza excepción."""
    try:
        # Determinar el origin a usar
        if not origin:
            try:
                origin = request.headers.get('Origin', '')
            except Exception:
                origin = ''

        if origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS[0]

        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = CORS_METHODS
        response.headers['Access-Control-Allow-Headers'] = CORS_HEADERS
        response.headers['Access-Control-Max-Age'] = '86400'
        response.headers['Vary'] = 'Origin'
    except Exception:
        # Si falla por cualquier razón, al menos poner el origin de producción
        try:
            response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS[0]
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = CORS_METHODS
            response.headers['Access-Control-Allow-Headers'] = CORS_HEADERS
        except Exception:
            pass
    return response


def create_app(config_class=Config):
    """Flask应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 设置JSON编码：确保中文直接显示（而不是 \uXXXX 格式）
    # Flask >= 2.3 使用 app.json.ensure_ascii，旧版本使用 JSON_AS_ASCII 配置
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False

    # 设置日志
    logger = setup_logger('mirofish')

    # 只在 reloader 子进程中打印启动信息（避免 debug 模式下打印两次）
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process

    if should_log_startup:
        logger.info("=" * 50)
        logger.info("MiroFish Backend 启动中...")
        logger.info("=" * 50)

    # ========================================================================
    # CORS — estrategia multicapa (de más prioridad a menos):
    #   1. before_request: intercepta OPTIONS preflight antes de cualquier ruta
    #   2. Flask-CORS: maneja el caso normal para rutas bajo /api/*
    #   3. after_request: safety net para TODAS las respuestas
    #   4. errorhandler: safety net para errores 500 y excepciones no capturadas
    # ========================================================================

    # --- Capa 1: Interceptar OPTIONS preflight antes de todo ---
    @app.before_request
    def handle_cors_preflight():
        if request.method == 'OPTIONS':
            # Crear respuesta vacía con headers CORS
            origin = request.headers.get('Origin', '')
            allowed_origin = origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]

            # Construir respuesta manual para evitar cualquier procesamiento
            response = app.make_response(('', 204))
            response.headers['Access-Control-Allow-Origin'] = allowed_origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = CORS_METHODS
            response.headers['Access-Control-Allow-Headers'] = CORS_HEADERS
            response.headers['Access-Control-Max-Age'] = '86400'
            response.headers['Vary'] = 'Origin'
            return response

    # --- Capa 2: Flask-CORS para el caso normal ---
    CORS(app, resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "supports_credentials": True,
            "max_age": 86400,
        }
    })
    if should_log_startup:
        logger.info(f"CORS: Orígenes permitidos: {ALLOWED_ORIGINS}")

    # --- Capa 3: Safety net after_request para TODAS las respuestas ---
    @app.after_request
    def add_cors_headers(response):
        return _add_cors_to_response(response)

    # --- Capa 4: Error handlers con CORS ---
    @app.errorhandler(500)
    def handle_500(error):
        """Error 500 con headers CORS explícitos."""
        origin = None
        try:
            origin = request.headers.get('Origin', '')
        except Exception:
            pass

        # Usar jsonify para respuesta JSON, no HTML
        resp = jsonify({
            "success": False,
            "error": "Error interno del servidor"
        })
        resp.status_code = 500
        return _add_cors_to_response(resp, origin=origin)

    @app.errorhandler(Exception)
    def handle_all_exceptions(error):
        """Catch-all: asegura que cualquier excepción tenga CORS headers."""
        origin = None
        try:
            origin = request.headers.get('Origin', '')
        except Exception:
            pass

        # Si es un HTTPException, usar su código
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            resp = error.get_response()
            return _add_cors_to_response(resp, origin=origin)

        # Para otras excepciones, devolver 500 JSON
        resp = jsonify({
            "success": False,
            "error": "Error interno del servidor"
        })
        resp.status_code = 500
        return _add_cors_to_response(resp, origin=origin)

    # 注册模拟进程清理函数（确保服务器关闭时终止所有模拟进程）
    from .services.simulation_runner import SimulationRunner
    SimulationRunner.register_cleanup()
    if should_log_startup:
        logger.info("已注册模拟进程清理函数")

    # 请求日志中间件
    @app.before_request
    def log_request():
        # Skip logging for OPTIONS (preflight) to reduce noise
        if request.method == 'OPTIONS':
            return
        logger = get_logger('mirofish.request')
        logger.debug(f"请求: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        logger = get_logger('mirofish.request')
        logger.debug(f"响应: {response.status_code}")
        return response

    # 注册蓝图
    from .api import graph_bp, simulation_bp, report_bp
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(report_bp, url_prefix='/api/report')

    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'MiroFish Backend'}

    if should_log_startup:
        logger.info("MiroFish Backend 启动完成")

    return app
