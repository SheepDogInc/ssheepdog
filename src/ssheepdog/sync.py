from ssheepdog.models import Login
from fabric.network import disconnect_all

def test_sync():
    try:
        for login in Login.objects.all():
            login.update_keys()
    finally:
        disconnect_all()
