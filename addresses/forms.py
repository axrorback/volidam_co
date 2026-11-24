from django import forms
from .models import Address


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address

        fields = [
            "title",
            "address_type",
            "region",
            "district",
            "mahalla",
            "street",
            "house",
            "apartment",
            "landmark",
            "latitude",
            "longitude",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Masalan: Uyim",
            }),

            "address_type": forms.Select(attrs={
                "class": "form-input",
            }),

            "region": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Viloyat",
            }),

            "district": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Tuman yoki shahar",
            }),

            "mahalla": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Mahalla nomi",
            }),

            "street": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Ko'cha nomi",
            }),

            "house": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Uy raqami",
            }),

            "apartment": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Xonadon raqami",
            }),

            "landmark": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Yaqin atrofdagi mo'ljal",
            }),

            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }