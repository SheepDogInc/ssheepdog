from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User
from django.contrib.auth.forms import UserChangeForm
import models

admin.site.register(models.Machine)
admin.site.register(models.Login)
admin.site.register(models.Client)

def unregister(Model):
    try:
        admin.site.unregister(Model)
    except:
        pass

def reregister(Model, AdminModel):
    unregister(Model)
    admin.site.register(Model, AdminModel)

class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False
    fk_name = 'user'

class SmartUserAdmin(UserAdmin):
    form = UserChangeForm
    inlines = [UserProfileInline]

reregister(User, SmartUserAdmin)
