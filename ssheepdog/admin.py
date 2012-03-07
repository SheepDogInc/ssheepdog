from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User
from ssheepdog import models, forms
from django.utils.translation import ugettext_lazy as _

admin.site.register(models.Client)

def unregister(Model):
    try:
        admin.site.unregister(Model)
    except:
        pass

def reregister(Model, AdminModel):
    unregister(Model)
    admin.site.register(Model, AdminModel)

class LoginAdmin(admin.ModelAdmin):
    model = models.Login
    form = forms.LoginForm
    exclude = ('application_key', 'is_dirty')
    filter_horizontal = ('users',)
admin.site.register(models.Login, LoginAdmin)

class LoginInline(admin.TabularInline):
    model = models.Login
    fields = ['username', 'is_active']

class MachineAdmin(admin.ModelAdmin):
    model = models.Machine
    inlines = [LoginInline]
admin.site.register(models.Machine, MachineAdmin)

class NamedApplicationKeyAdmin(admin.ModelAdmin):
    model = models.NamedApplicationKey
    fieldsets = (
        (None, {'fields': (),
                'description':
                "<br/>"
                """The reason to create a named key is if you want to
                   pre-select it as the start key for a Login.  For example,
                   perhaps you want to pre-configure a master VM with this
                   start key."""
                "<br/>&nbsp;"
                }),
        (None, {'fields': ('nickname', 'description')}),)
    exclude = ['application_key']
admin.site.register(models.NamedApplicationKey, NamedApplicationKeyAdmin)

class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False
    fk_name = 'user'

class SmartUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )

reregister(User, SmartUserAdmin)
