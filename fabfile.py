import os
import sys
import datetime

from fabric.colors import red, green
from fabric.operations import local, prompt

PROJECT_NAME = 'ssheepdog'
APPS = ['ssheepdog']
TESTS = ' '.join(APPS)
COVERAGE_SOURCES = ','.join(APPS)
COVERAGE_PARAMS = "--omit='*migrations*,*tests*"
ENVS = {
    'dev': {
        'repo_url': 'git@heroku.com:sheltered-bastion-8737.git',
        'site_url': 'http://sheltered-bastion-8737.herokuapp.com'
    },
    'prod': {
        'repo_url': 'git@heroku.com:setsailforfail.git',
        'site_url': 'http://setsailforfail.herokuapp.com'
    },
}


def check_dest(fn):
    """
    Decorator that verifies whether kwarg 'dest' is present and is a valid
    environment name.
    """
    def validate_dest(input):
        if input not in ENVS:
            raise Exception('Invalid environment specified.')
        return input

    def wrapper(*args, **kwargs):
        dest = kwargs.get('dest', None)
        if dest:
            validate_dest(dest)
        else:
            kwargs['dest'] = prompt(
                "Enter one of the following destinations [%s]:"
                % ', '.join(ENVS),
                validate=validate_dest)
        return fn(*args, **kwargs)
    return wrapper


##### Git remote repo management #####

def get_repos():
    return local("git remote", capture=True).split("\n")


def _add_repo(repo, url, repos):
    if repo not in repos:
        local("git remote add %s %s" % (repo, url))


def _rm_repo(repo, url, repos):
    if repo in repos:
        local("git remote rm %s" % repo)


def _reset_repo(repo, url, repos):
    _rm_repo(repo, url, repos)
    _add_repo(repo, url, [])


def env_repos(action=None):
    """
    Perform an action on each environment repository, specified by action.
    """
    actions = {
        'add': _add_repo,
        'reset': _reset_repo,
        'rm': _rm_repo
    }

    def validate_action(input):
        if input not in actions:
            raise Exception('Invalid action specified.')
        return input

    if action:
        validate_action(action)
    else:
        action = prompt(
            "Enter one of the following actions: <%s>" % ", ".join(actions),
            validate=validate_action)

    repos = get_repos()
    for env, details in ENVS.iteritems():
        actions[action](env, details['repo_url'], repos)


def _get_local_branches():
    return [b.strip() for b in local("git branch", capture=True).split('\n')]


def _get_current_branch():
    selected = [b for b in _get_local_branches() if b.startswith('* ')]
    return selected[0].replace('* ', "") if len(selected) else None


@check_dest
def deploy(dest=''):
    """
    Deploy from current repo to respective environment
    """

    # Make sure our env repos are added as remotes
    env_repos('add')

    # Get the current branch
    current_branch = _get_current_branch()
    if current_branch == "(no branch)":
        current_branch = local("git rev-parse --short HEAD", capture=True)

    # Push to the destination
    local('git push %s %s:master --force' % (dest, current_branch))
    remote('syncdb --noinput', dest=dest)
    remote('migrate', dest=dest)
    deploy_static(dest=dest)
    check(dest=dest)


def run():
    local('./manage.py runserver 0.0.0.0:8000')


##### Static file management #####

@check_dest
def deploy_static(dest=''):
    """
    Compress and upload static files to S3.
    """
    local('./manage.py collectstatic --noinput'
          ' --settings=%s.settings.heroku.%s' % (PROJECT_NAME, dest))
    # local('./manage.py compress'
    #       ' --force --settings=%s.settings.heroku.%s' % (PROJECT_NAME, dest))


def _now():
    return datetime.now().strftime('%Y%m%s-%H%M')


##### Database management #####

def reset_local_db():
    local('dropdb %s' % PROJECT_NAME)
    local('createdb %s' % PROJECT_NAME)


def try_migrations():
    reset_local_db()
    local('./manage.py syncdb')
    local('./manage.py migrate')


def try_clean():
    reset_local_db()
    local('./manage.py syncdb --noinput')
    local('./manage.py migrate')


def reset_heroku_db():
    local('heroku pg:reset')


def load_db():
    """
    Populate empty Heroku database via json fixture
    """
    print red('This will drop all tables from the database.')
    print 'Please make sure you understand what this command does.'
    print 'Do you want to continue? [y/n]'
    answer = raw_input()
    if answer != 'y':
        print 'Aborting...'
        return

    commands = [
        './manage.py syncdb --noinput',
        './manage.py migrate',
        './manage.py droptables -y',
        './manage.py loaddata dump.json',
        ]
    local('heroku run "%s"' % '; '.join(commands))


def make_dump():
    local('./manage.py dumpdata | python -mjson.tool > dump.json')


##### Heroku specific helpers #####

@check_dest
def remote(cmd='', dest=''):
    """
    Run a manage.py command on Heroku using ``settings_heroku``

    Usage:

        $ fab remote:'sendtestemail adam@sheepdoginc.ca'
        $ fab remote:syncdb
    Or
        $ fab remote
        Command to run: syncdb

    """
    if not cmd:
        cmd = prompt('Command to run:')
    local("heroku run python manage.py %s \
            --settings=%s.settings.heroku.%s" % (cmd, PROJECT_NAME, dest))


##### Testing, coverage & site validation #####

def test():
    """
    Run unit tests for this Django Application
    """
    if len(APPS) == 0:
        return
    local('./manage.py test %s' % TESTS)


def coverage():
    """
    Generate Coverage report for this Django Application
    """
    if len(APPS) == 0:
        return
    local('coverage run --source=%s ./manage.py test %s' % COVERAGE_SOURCES, TESTS)
    print '============================================'
    print 'Coverage Results:'
    local('coverage report %s' % COVERAGE_PARAMS)
    local('rm .coverage')


@check_dest
def check(dest=''):
    """
    Check that the home page of the site returns an HTTP 200.
    """
    print 'Checking site status...'
    response = local('curl --silent -I "%s"' % ENVS[dest]['site_url'],
                     capture=True)
    if not '200 OK' in response:
        print(red('\nSomething seems to have gone wrong!\n'))
    else:
        print(green('\nLooks good from here!\n'))


##### Local utility tasks #####

def clean():
    """
    Remove all .pyc files
    """
    local('find . -name "*.pyc" -exec rm {} \;')


def debug():
    """
    Find files with debug symbols
    """
    clean()
    local('grep -ir "print" *')
    local('grep -ir "console.log" *')


def todo():
    """
    Find all TODO and XXX
    """
    clean()
    local('grep -ir "TODO" *')
    local('grep -ir "XXX" *')


def stats():
    """
    Show number of additions and deletions between 1.0 and now
    """
    local('git diff 1.0..HEAD --shortstat')


def freeze():
    """
    Generate a stable requirements.txt based on requirements.spec.txt.
    """
    local('pip freeze -r requirements.spec.txt > requirements.txt')


try:
    assert os.getcwd() == os.path.dirname(os.path.abspath(__file__))
except AssertionError:
    print red('You must run this from the root of the project.')
    sys.exit(1)
