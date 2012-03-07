from django import forms
from ssheepdog import models

class AccessFilterForm(forms.Form):
    user = forms.CharField(label="User", required=False)
    login = forms.CharField(label="Login/Machine", required=False)

class LoginForm(forms.ModelForm):
    named_application_key = forms.ModelChoiceField(
        required=False,
        label="Force reset to named key",
        queryset=models.NamedApplicationKey.objects.all(),
        help_text=
        """
        Usually leave this blank.  This can be useful when you just cloned a
        master VM which was already pre-configured with this start key.  This
        named key will be used to authenticate on the next key deployment, but
        SSHeepdog will overwrite the named key the latest SSHeepdog key on the
        next deployment.
        """)
    class Meta:
        model = models.Login

    def save(self, *args, **kwargs):
        commit = kwargs.get('commit', True)
        kwargs['commit'] = False
        obj = super(LoginForm, self).save(*args, **kwargs)
        key = self.cleaned_data['named_application_key']
        if key:
            obj.application_key = key.application_key
        if commit:
            obj.save()
        return obj

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ('ssh_key',)
