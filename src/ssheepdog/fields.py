import base64
from django.db.models import TextField
from django.core import exceptions
from django.utils.translation import ugettext as _

class PublicKeyField(TextField):
    def validate(self, value, model_instance):
        """
        Just confirm that the first field is something like ssh-rsa or ssh-dss,
        and the second field is reasonably long and can be base64 decoded.
        """
        super(PublicKeyField, self).validate(value, model_instance)
        try:
            type_, key_string = value.split()[:2]
            assert (type_[:4] == 'ssh-')
            assert (len(key_string) > 100)
            base64.decodestring(key_string)
        except:
            raise exceptions.ValidationError(_("Does not appear to be an ssh public key"))
        
    def clean(self, value, model_instance):
        """
        Clean up any whitespace.
        """
        value = " ".join(value.strip().split())
        return super(PublicKeyField, self).clean(value, model_instance)
