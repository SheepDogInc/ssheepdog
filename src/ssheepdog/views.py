from django.http import HttpResponse
from django.template import Context, loader
from src import ssheepdog
from models import UserProfile, Machine, Login, Client
from django.shortcuts import render_to_response
from django.template import RequestContext

def view_page(request):
	#user_prof = get_object_or_404(UserProfile,pk = user_id)
	#login = get_object_or_404(UserProfile,pk = user_id)
	#context_dict = {'user' : user_prof,'login' : login}
	userList = {'Travis', 'Garrett', 'Ian', 'Matt','David'}
	context_dict = {'users' : userList}
	return render_to_response('test_html.html',
		context_dict,
	 	context_instance=RequestContext(request)) 
