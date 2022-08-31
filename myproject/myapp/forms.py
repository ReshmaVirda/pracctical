from django import forms
from django.db import models
from django.forms import fields
from myapp.models import Register,Login

class Registerform(forms.ModelForm):

    class Meta:

        model = Register
        fields = '__all__'


class Loginform(forms.ModelForm):

    class Meta:

        model = Login
        fields = '__all__'

