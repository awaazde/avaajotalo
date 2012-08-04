from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from otalo.ao.models import Forum

class CreateAcctForm(forms.Form):
    def validate_mobile(value):
        if len(value) != 10:
            raise ValidationError("Please enter a 10-digit number with no spaces or dashes.")
        try:
            int(value)
        except ValueError as err:
            raise ValidationError("Please enter a 10-digit number with no spaces or dashes.")
        
    name = forms.CharField(
        label = "Full Name",
        max_length = 128,
        required = True,
        help_text='e.g. Neil Patel'
    )

    number = forms.CharField(
        label = "Mobile",
        required = True,
        help_text='e.g. 9586550654',
        validators=[validate_mobile]
    )
    
    email = forms.EmailField(
        label = "Email",
        max_length = 80,
        required = True,
        help_text='e.g. neil@awaaz.de'
    )
    
    groupname = forms.CharField(
        label = "Group Name",
        max_length = 24,
        required = True,
        help_text='e.g. Friends'
    )

    language = forms.ChoiceField(
        label = "Language",
        choices = (
                   ('hin', 'Hindi'),
                   ('guj', 'Gujarati'),
                   ('eng', 'English'),
                  ),
        required = True,
    )
    
    delivery = forms.ChoiceField(
        label = "Message Delivery",
        choices = (
                   (Forum.STATUS_BCAST_CALL_SMS, 'Call + SMS'),
                   (Forum.STATUS_BCAST_SMS, 'SMS Only'),
                  ),
        required = True,
    )
    
    tos = forms.BooleanField(
        label = "I agree to the Awaaz.De <a href='http://awaaz.de/TOS.pdf'>Terms of Service</a>",
        required = True,
    )
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Register', css_class='btn btn-primary'))
        
        super(CreateAcctForm, self).__init__(*args, **kwargs)