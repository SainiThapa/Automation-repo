from django import forms

class ImageTextForm(forms.Form):
    image = forms.ImageField(label="Upload Image")
    text = forms.CharField(max_length=255, label="Enter Caption", widget=forms.TextInput(attrs={"placeholder": "Enter text"}))
