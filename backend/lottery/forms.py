from django import forms


class BallotPurchaseForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Number of ballots"}
        ),
        help_text="Choose between 1 and 10 ballots",
    )

    # Mock payment fields
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "1234 5678 9012 3456",
            }
        ),
        help_text="Enter your card number",
    )

    expiry_date = forms.CharField(
        max_length=5,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "MM/YY"}
        ),
        help_text="Card expiry date (MM/YY)",
    )

    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "123"}
        ),
        help_text="3 or 4 digit security code",
    )

    def clean_card_number(self):
        card_number = self.cleaned_data.get("card_number")
        # Remove spaces and validate basic format
        card_number = card_number.replace(" ", "")
        if (
            not card_number.isdigit()
            or len(card_number) < 13
            or len(card_number) > 19
        ):
            raise forms.ValidationError("Please enter a valid card number")
        return card_number

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get("expiry_date")
        if not expiry_date or "/" not in expiry_date:
            raise forms.ValidationError(
                "Please enter expiry date in MM/YY format"
            )
        return expiry_date

    def clean_cvv(self):
        cvv = self.cleaned_data.get("cvv")
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            raise forms.ValidationError("Please enter a valid CVV")
        return cvv
