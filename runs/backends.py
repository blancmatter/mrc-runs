import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

logger = logging.getLogger(__name__)


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with either
    their username or email address.

    This provides flexibility for both legacy users (with separate usernames)
    and new users (where email is the username).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using either username or email.

        Args:
            request: The HTTP request object
            username: The username or email provided by the user
            password: The password provided by the user
            **kwargs: Additional keyword arguments

        Returns:
            User object if authentication successful, None otherwise
        """
        if username is None or password is None:
            return None

        try:
            # Try to find user by username or email
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )

            # Check if the password is correct
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Edge case: Multiple users share the same email address
            # This should be rare as we validate unique emails during registration
            # Try exact username match as fallback
            logger.warning(
                f'Multiple users found for email: {username}. '
                'Attempting exact username match. '
                'Note: This assumes usernames remain unique in the database.'
            )
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
            except User.MultipleObjectsReturned:
                # This should never happen as username is unique by default
                logger.error(f'Multiple users found with username: {username}')
                return None

        return None
