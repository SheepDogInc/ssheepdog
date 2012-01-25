from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ssheepdog.models import Login, UserProfile, Machine, ApplicationKey, Client
from django.contrib.auth.decorators import permission_required

@permission_required('ssheepdog.can_view_access_summary')
def view_access_summary(request):
    users = User.objects.select_related('_profile_cache').order_by('_profile_cache__nickname')
    logins = Login.objects.all().order_by('username')
    for user in users:
        user.nickname = user.get_profile().nickname
    for login in logins:
        login.entries = []
        for user in users:
            all_active_bool = False
            allowed = False
            if user in login.users.all():
                allowed = True
            if user.is_active and login.is_active and login.machine.is_active:
                all_active_bool = True
            login.entries.append({'all_active': all_active_bool, 
                                  'is_allowed': allowed,
                                  'user': user})

    context_dict = {'users' : users, 'logins' : logins}

    return render_to_response('view_grid.html',
        context_dict,
        context_instance=RequestContext(request))  

def user_admin_view(request,id=None):
    user = User.objects.select_related('_profile_cache').get(pk=id)
    user.nickname = user.get_profile().nickname
    user.ssh_key = user.get_profile().ssh_key
    return render_to_response('user_view.html',
            {'user':user},
            context_instance=RequestContext(request))

def login_admin_view(request,id=None):
    login = Login.objects.get(pk=id)
    machines = Machine.objects.all()
    clients = Client.objects.all()
    app_keys = ApplicationKey.objects.all()
    latest_app_key = ApplicationKey.get_latest()
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
    return redirect(reverse('ssheepdog.views.view_access_summary'))

def edit_ssh(request):
    pk = request.POST.get('pk',None)
    pub_key = request.POST.get('pub_key',None)
    try:
        user = UserProfile.objects.get(user=pk)
        user.ssh_key = pub_key 
        user.save()
    except User.DoesNotExist:
        pass
    return redirect(reverse('ssheepdog.views.view_access_summary'))

@permission_required('ssheepdog.can_sync')
def generate_new_application_key(request):
    from ssheepdog.utils import generate_new_application_key
    generate_new_application_key()
    return redirect(reverse('ssheepdog.views.view_access_summary'))
