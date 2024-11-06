from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__, 
                template_folder='templates',  # 指定模板文件夹
                static_folder='static')       # 指定静态文件夹
    app.config.from_object(Config)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app 