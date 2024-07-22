# app/app.py
from flask import Flask
from flask_cors import CORS

from routes import users_blueprint, places_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(users_blueprint())
    app.register_blueprint(places_blueprint())

    @app.route('/')
    def wellcome():
        return "<center><h1> Wellcome to Teapon <h1></center>"
    
    return app
