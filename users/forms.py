import sys
import os
from django import forms

from .models import Profile
from .models import Upload

class AccountCreationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname']

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['file']