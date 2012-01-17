from ssheepdog.models import Login
from fabric.network import disconnect_all
from django.conf import settings


def test_sync():
    try:
        for login in Login.objects.all():
            login.update_keys()
    except:
        print 'failed bro'
    finally:
        disconnect_all
