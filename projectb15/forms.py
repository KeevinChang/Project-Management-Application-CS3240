from django import forms
from .models import Event, Upload, Message

class AddEventForm(forms.ModelForm):
    CHOICES = (
        ("1", "Public"),
        ("2", "Private"),
    )
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    visibility = forms.ChoiceField(choices=CHOICES)

    class Meta:
        model = Event
        fields = ['title', 'date', 'description', 'start_time', 'end_time', 'header_image', 'visibility']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def validate_times(self):
        """Validate start and end times."""
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

    def clean(self):
        """Run all validation methods."""
        self.validate_times()  # Validate start and end times
        return super().clean()
        
class FileUploadForm(forms.ModelForm):
    title = forms.CharField(max_length=100, required=False, label="Title")
    description = forms.CharField(widget=forms.Textarea, required=False, label="Description")
    keywords = forms.CharField(max_length=200, required=False, label="Keywords")
    #event= forms.IntegerField(widget=forms.HiddenInput(), initial=1) 

    class Meta:
        model = Upload
        fields = ['title', 'description', 'keywords', 'file']
        
class CreateMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
