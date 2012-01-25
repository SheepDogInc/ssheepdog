from django import forms

class UserProfileForm(forms.Form):
    public_key = forms.CharField()
