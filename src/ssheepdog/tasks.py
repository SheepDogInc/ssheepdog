from celery.decorators import task
from models import Login


@task()
def sync():
    Login.sync_all()
