from django import forms


class AdminAccountCreateForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="First name", required=False, max_length=150)
    last_name = forms.CharField(label="Last name", required=False, max_length=150)


    role = forms.ChoiceField(
        label="Role",
        required=True,
        choices=[('admin', 'Admin'), ('cashier', 'Cashier'), ('inspector', 'Inspector')],
    )


