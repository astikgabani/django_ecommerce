from django import forms


class ContactForm(forms.Form):

    firstname = forms.CharField(widget=forms.TextInput(
            attrs={
                    "class": "form-control", 
                    "placeholder": "Your First Name"
                })
            )
    lastname = forms.CharField(widget=forms.TextInput(
            attrs={
                "class": "form-control", 
                "placeholder": "Your Last Name"
                })
            )
    email = forms.EmailField(widget=forms.EmailInput(
            attrs={
                "class": "form-control", 
                "placeholder": "abc@example.com"
                })
            )
    subject = forms.CharField(widget=forms.TextInput(
            attrs={
                "class": "form-control", 
                "placeholder": ""
                })
            )
    message = forms.CharField(widget=forms.Textarea(
            attrs={
                "class": "form-control", 
                "placeholder": "Your First Name"
                })
            )
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Email can't be Empty.")
        return email

