from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import AkornUser

class AkornUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label = "Password",
        widget = forms.PasswordInput)
    password2 = forms.CharField(
        label = "Password confirmation",
        widget = forms.PasswordInput)

    class Meta:
        model = AkornUser
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return password2

    def save(self, commit=True):
        user = super(AkornUserCreationForm,
            self).save(commit=False)

        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AkornUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = AkornUser

    def clean_password(self):
        return self.initial["password"]
