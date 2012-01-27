from django import forms
from ssheepdog.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('ssh_key',)
