class submit_access_form(forms.Form):
    selection = forms.ChoiceField(choices=[])

    def __init__(self, list_of_orgs, *args, **kwargs):
        super(submit_access_form,self).__init__(*args, **kwargs)
        self.fields['selection'].choices = [(org.pk,org.name) for org in list_of_orgs]
