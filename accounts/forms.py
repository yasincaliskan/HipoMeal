from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from accounts.models import Profile
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=80, label="Username")
    password = forms.CharField(max_length=80, label="Password", widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Username or password is wrong!')
        return super(LoginForm, self).clean()
#
#
# class RegisterForm(forms.ModelForm):
#     username = forms.CharField(max_length=80, label="Username")
#     email = forms.EmailField()
#     password1 = forms.CharField(max_length=80, label="Password", widget=forms.PasswordInput)
#     password2 = forms.CharField(max_length=80, label="Verify Password", widget=forms.PasswordInput)
#
#     class Meta:
#         model = User
#         fields = [
#             'username',
#             'email',
#             'password1',
#             'password2'
#         ]
#
#     def clean_password2(self):
#         password1 = self.cleaned_data.get('password1')
#         password2 = self.cleaned_data.get('password2')
#         if password2 and password1 and password2 != password1:
#             raise forms.ValidationError('Passwords do not match!')
#         return password2


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

