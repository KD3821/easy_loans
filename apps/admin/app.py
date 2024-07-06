from db import Base
from flask import Flask, url_for
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from settings import (APP_ADMIN_NAME, DB_HOST, DB_NAME, DB_PASS, DB_PORT,
                      DB_USER, JWT_SECRET_KEY)

from .forms import CustomLoginForm
from .models import FlaskAdminUser

app = Flask(__name__)

# Configurations of Flask application
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
app.config["SECURITY_REGISTERABLE"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = JWT_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Make db connection
db = SQLAlchemy(app)

# Extention of SQLAlchemy base
# To make flask-security (login) work
# https://github.com/mattupstate/flask-security/issues/766#issuecomment-393567456
Base.query = db.session.query_property()

# Create Flask Admin
admin = Admin(app, name=APP_ADMIN_NAME, template_mode="bootstrap3")

# Import View to attach them to Flask app
import apps.admin.views  # noqa # pylint: disable=unused-import

# Setup Flask-Security (Login)
user_datastore = SQLAlchemyUserDatastore(db, FlaskAdminUser, None)
security = Security(app, user_datastore, login_form=CustomLoginForm)


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
    )
