import base64
from django.db.models import TextField
from django.core import exceptions
from django.utils.translation import ugettext as _

class PublicKeyField(TextField):
    def validate(self, value, model_instance):
        """
        Confirm that each row is a valid ssh key
        """
        def _validate_key(value):
            """
            Just confirm that the first field is something like ssh-rsa or ssh-dss,
            and the second field is reasonably long and can be base64 decoded.
            """
            if value.strip() == "":
                return True
            try:
                type_, key_string = value.split()[:2]
                assert (type_[:4] == 'ssh-')
                assert (len(key_string) > 100)
                base64.decodestring(key_string)
                return True
            except:
                False

        super(PublicKeyField, self).validate(value, model_instance)
        keys = value.rstrip().split("\n")
        l = len(keys)
        i = 0
        for s in value.split("\n"):
            i += 1
            if not _validate_key(s):
                if l == 1:
                    message = _("This does not appear to be an ssh public key")
                else:
                    message = _("Row %d does not appear"
                                " to be an ssh public key") % i
                raise exceptions.ValidationError(message)

    def clean(self, value, model_instance):
        """
        Clean up any whitespace.
        """
        lines = value.strip().split("\n")
        lines = [" ".join(line.strip().split()) for line in lines]
        value = "\n".join([line for line in lines if line])
        return super(PublicKeyField, self).clean(value, model_instance)
