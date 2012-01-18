from ssheepdog.models import Login
from fabric.network import disconnect_all
from django.conf import settings


def test_sync():
    try:
        for login in Login.objects.all():
            try:
                login.update_keys()
            except SystemExit:
                pass 
    finally:
        disconnect_all()

    
