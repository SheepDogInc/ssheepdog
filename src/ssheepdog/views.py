from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ssheepdog.models import Login, UserProfile, Machine, ApplicationKey, Client
from django.contrib.auth.decorators import permission_required
from ssheepdog.forms import UserProfileForm


@permission_required('ssheepdog.can_view_access_summary')
def view_access_summary(request):
    users = User.objects.select_related('_profile_cache').order_by('_profile_cache__nickname')
    logins = Login.objects.all().order_by('username')

    if not users or not logins:
        context_dict = {'users' : [], 'logins' : []}
    else:
        for user in users:
            user.nickname = user.get_profile().nickname
        for login in logins:
            login.entries = []
            get_user_login_info(login,users)
        context_dict = {'users' : users, 'logins' : logins}

    return render_to_response('view_grid.html',
        context_dict,
        context_instance=RequestContext(request))

    
def get_user_login_info(login,users): 
    for user in users:
        if user in login.users.all():
            allowed = True
        else:
            allowed = False
        if user.is_active and login.is_active and login.machine.is_active:
            all_active_bool = True
        else:
            all_active_bool = False
        login.entries.append({'all_active': all_active_bool,
                            'is_allowed': allowed,
                            'user': user})
    return login.entries


def user_admin_view(request,id=None):
    user = User.objects.select_related('_profile_cache').get(pk=id)
    user.nickname = user.get_profile().nickname
    user.ssh_key = user.get_profile().ssh_key
    user.fullname = user.get_full_name()
    form = UserProfileForm(initial={'public_key':user.ssh_key})
    if request.method == 'POST':
        if request.user.is_authenticated() and request.user == user:
            if request.POST.get('public_key'):
                form = UserProfileForm(request.POST)
                if form.is_valid():
                    user = UserProfile.objects.get(user=id)
                    new_key = form.cleaned_data['public_key']
                    user.ssh_key = new_key 
                    user.save()
                    return redirect('ssheepdog.views.view_access_summary')
        else: 
            return redirect('ssheepdog.views.view_access_summary')
    return render_to_response('user_view.html',
            {'user':user, 'form':form, 'request': request},
            context_instance=RequestContext(request))


def login_admin_view(request,id=None):
    login = Login.objects.get(pk=id)
    machines = Machine.objects.all()
    clients = Client.objects.all()
    app_keys = ApplicationKey.objects.all()
    latest_app_key = ApplicationKey.get_latest().public_key
    content = {'login':login, 'machines':machines, 'clients':clients,
                'app_keys':app_keys, 'latest_app_key':latest_app_key}
    return render_to_response('login_view.html',
            content,
            context_instance=RequestContext(request))


@permission_required('ssheepdog.can_sync')
def sync_keys(request):
    pk = request.POST.get('pk', None)
    if pk:
        try:
            login = Login.objects.get(pk=pk)
            login.sync()
        except Login.DoesNotExist:
            pass
    else:
        Login.sync_all()
    return redirect('ssheepdog.views.view_access_summary')


@permission_required('ssheepdog.can_sync')
def generate_new_application_key(request):
    from ssheepdog.utils import generate_new_application_key
    generate_new_application_key()
    return redirect('ssheepdog.views.view_access_summary')
