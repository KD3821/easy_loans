from flask_security.forms import LoginForm
from flask_security.utils import _datastore, get_message
from apps.users.storages.users_storage import validate_password, hash_password


class CustomLoginForm(LoginForm):
    """
    Customization of default Login form to support the User model
    from the Fast API application and support password hashing that implemented there
    """
    def validate(self, extra_validators=None):
        # Put code here if you want to do stuff before login attempt
        self.user = _datastore.get_user(self.email.data)

        if self.user is None:
            self.email.errors += (get_message('USER_DOES_NOT_EXIST')[0], )
            # Reduce timing variation between existing and non-existung users
            hash_password(self.password.data)
            return False

        if not validate_password(self.password.data, self.user.hashed_password):
            self.password.errors += (get_message('INVALID_PASSWORD')[0], )
            # Reduce timing variation between existing and non-existung users
            hash_password(self.password.data)
            return False

        return True
