from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ssheepdog.models import Login, UserProfile
from django.contrib.auth.decorators import permission_required
from ssheepdog.forms import UserProfileForm


@permission_required('ssheepdog.can_view_access_summary')
def view_access_summary(request):
    users = User.objects.select_related('_profile_cache').order_by('_profile_cache__nickname')
    logins = Login.objects.all().order_by('username')

    for login in logins:
        login.entries = get_user_login_info(login,users)

    return render_to_response('view_grid.html',
        {'users' : users, 'logins' : logins},
        context_instance=RequestContext(request))

    
def get_user_login_info(login, users):
    """
    Return a dict of data for each user; it's important
    that the users remain in the same order.
    """
    login_is_active = login.is_active and login.machine.is_active
    return [{'is_active': user.is_active and login_is_active,
             'is_allowed': user in login.users.all(),
             'user': user}
            for user in users]


def user_admin_view(request,id=None):
    user = User.objects.select_related('_profile_cache').get(pk=id)
    form = UserProfileForm(initial={'public_key': user.get_profile().ssh_key})
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
            {'user': user, 'form': form},
            context_instance=RequestContext(request))


def login_admin_view(request,id=None):
    return render_to_response('login_view.html',
            {'login': Login.objects.get(pk=id)},
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
