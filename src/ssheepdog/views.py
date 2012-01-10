from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template import Context, loader
from src import ssheepdog
from ssheepdog.models import UserProfile, Machine, Login, Client
from django.shortcuts import render_to_response
from django.template import RequestContext

def view_page(request):
    #user_prof = get_object_or_404(UserProfile,pk = user_id)
    #login = get_object_or_404(UserProfile,pk = user_id)
    #context_dict = {'user' : user_prof,'login' : login}
    profile = User.objects.select_related('_profile_cache')  
    users = User.objects.all()
    user_profiles = UserProfile.objects.all()
    logins = Login.objects.all()
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
    context_dict = {'users' : users, 'logins' : logins, 'profiles' :
            user_profiles}


    return render_to_response('view_grid.html',
        context_dict,
        context_instance=RequestContext(request)) 
