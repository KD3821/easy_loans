from apps.users.models import User


class FlaskAdminUser(User):
    """
    Extending of default User model
    and adding to is some specifc
    properties to make Flask Admin work
    """
    @property
    def is_authenticated(self):
        return True

    @property
    def active(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username
