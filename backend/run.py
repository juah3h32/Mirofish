"""
MiroFish Backend 启动入口
"""

import os
import sys

# 解决 Windows 控制台中文乱码问题：在所有导入之前设置 UTF-8 编码
if sys.platform == 'win32':
    # 设置环境变量确保 Python 使用 UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    # 重新配置标准输出流为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config


def main():
    """主函数"""
    # 验证配置 (no bloquear el inicio — solo advertir)
    errors = Config.validate()
    if errors:
        print("⚠️  Advertencia: configuración incompleta:")
        for err in errors:
            print(f"  - {err}")
        print("   La app iniciará pero algunas funciones no estarán disponibles.\n")

    # 创建应用 (con captura de errores para diagnóstico)
    try:
        app = create_app()
        print("Flask app creada exitosamente")
    except Exception as e:
        print(f"ERROR FATAL al crear la app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 获取运行配置
    # IMPORTANTE: Flask SIEMPRE usa FLASK_PORT (default 5001).
    # En Render/Docker, PORT es el puerto externo de Render (ej. 10000).
    # Vite es el entry point externo (:3000 → PORT de Render) y
    # su proxy espera Flask en localhost:5001. Si Flask usa PORT,
    # Vite no puede encontrarlo y todas las requests /api fallan.
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    flask_port = int(os.environ.get('FLASK_PORT', '5001'))
    # Ignorar PORT — es para el servicio externo (Vite), no para Flask
    debug = Config.DEBUG

    print(f"Flask iniciando en {host}:{flask_port} (debug={debug})")
    # 启动服务
    app.run(host=host, port=flask_port, debug=debug, threaded=True)


if __name__ == '__main__':
    main()

