from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Enter Password"
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Confirm Password"
    }))

    class Meta:
        model = Account
        fields = ["first_name", "last_name",
                  "phone_number", "email", "password"]

    # function to modify clean function of the form so that password and confirm password
    # can be matched
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

    # we can add classes individually to each field by adding the "class" in attrs dictionary
    # as we mentioned the placeholder in the attrs above,
    # but below is a shorter way to add class to all the fields
    def __init__(self, *args, **kwargs):
        # getting access to constructor of the parent class of Registration Form
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # adding placeholder for first_name field in the form
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter First Name"

        # adding placeholder for last_name field in the form
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter Last Name"

        # adding placeholder for email field in the form
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email"

        # adding placeholder for phone_number field in the form
        self.fields["phone_number"].widget.attrs["placeholder"] = "Enter Phone Number"

        # adding class for all the fields in the form
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("first_name", "last_name", "phone_number")

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={
                                       'invalid': ("Image files only")}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ("address_line_1", "address_line_2", "city",
                  "state", "country", "profile_picture")

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
