from flask import Flask

from category_merger.app_blueprint import api_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/")
    return app


def main():
    app = create_app()
    app.run(debug=True)


"""
To run the Flask app in DEBUG mode execute:

python -m category_merger.main 
"""
if __name__ == "__main__":
    main()
