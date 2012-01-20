from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ssheepdog.models import Login

def view_page(request):
    users = User.objects.select_related('_profile_cache')  
    logins = Login.objects.all()
    for user in users:
        user.nickname = user.get_profile().nickname
    for login in logins:
        login.entries = []
        for user in users:
            all_active_bool = False
            allowed = False
            if user in login.users.all():
                allowed = True
            if user.get_profile().is_active and login.is_active and login.machine.is_active:
                all_active_bool = True
            login.entries.append({'all_active': all_active_bool, 
                                  'is_allowed': allowed,
                                  'user': user})
    context_dict = {'users' : users, 'logins' : logins}

    return render_to_response('view_grid.html',
        context_dict,
        context_instance=RequestContext(request))  

def sync_keys(request):
    Login.sync()
    return redirect(reverse('results'))

def results_page(request):
    return render_to_response('results.html',
            {'logins' : Login.objects.all()},
            context_instance=RequestContext(request))  

def generate_new_application_key(request):
    from ssheepdog.utils import generate_new_application_key
    generate_new_application_key()
    return redirect(reverse('results'))
