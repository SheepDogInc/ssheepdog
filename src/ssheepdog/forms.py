from django import forms
from ssheepdog.models import UserProfile

class AccessFilterForm(forms.Form):
    user = forms.CharField(label="User", required=False)
    login = forms.CharField(label="Login/Machine", required=False)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('ssh_key',)
