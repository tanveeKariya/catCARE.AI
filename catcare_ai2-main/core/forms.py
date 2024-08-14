from django import forms
from .models import CustomUserModel
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput)
    last_name = forms.CharField(widget=forms.TextInput)
    email = forms.EmailField(widget=forms.EmailInput)
    # gender = forms.ChoiceField(
    #     choices=CustomUserModel.GENDER_CHOICES,
    #     widget=forms.RadioSelect,
    #     required=True
    # )
    username = forms.CharField(widget=forms.TextInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = CustomUserModel
        fields = ['first_name','last_name', 'email', 'username','password1','password2']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = CustomUserModel
        fields = ['username','password1']
