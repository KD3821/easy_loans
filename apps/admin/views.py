from flask_admin.contrib import sqla
from flask_security import current_user
from flask import url_for, redirect, request, abort
from .app import app, db, admin
from core import OrmInternalService

# Create customized model view class


class MyModelView(sqla.ModelView):
    """
    The overridden general Model View for SQLAlchemy models.
    It adapted for the User model of this template and 
    can be modified for the project needs
    """

    def is_accessible(self):
        """
        This method check is the resource accessible
        for the current user. By using this method
        it is possible to restrict and access to specific views (models)
        based on users role, status, etc.
        By default, only home page (login) is accessible for not authorized
        user. For authorized user with role 'admin' all views (models) are 
        available
        """
        return (current_user.is_authenticated and
                current_user.role == current_user.ADMIN)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


# Flask views
@app.route('/')
def index():
    """
    Redirect user from the root page to login or home page
    """
    if current_user.is_authenticated:
        return redirect(url_for('admin.index', next=request.url))
    return redirect(url_for('security.login', next=request.url))


# Get all models in the app
# and add them to Flask Admin
models = OrmInternalService.get_models()

for model in models:
    if model.__str__ is object.__str__:
        def custom_method(self):
            return f"{self.__class__.__name__} {self.id}"

        model.__str__ = custom_method

    # the model can be added conditionally
    # for instance:
    # if model.for_admin:
    #   admin.add_view(MyModelView(model, db.session))

    admin.add_view(MyModelView(model, db.session))
