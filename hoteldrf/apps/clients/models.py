from ..users.models import CustomUser


class Client(CustomUser):

    class Meta:
        proxy = True

