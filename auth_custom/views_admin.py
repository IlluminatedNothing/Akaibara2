from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.conf import settings

import secrets
import string

from .forms import AdminAccountCreateForm
from .models import Profile
from .views import role_required


def _generate_temp_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@login_required
@role_required(['admin'])  # Superusers bypass this anyway
def admin_create_user(request):
    if request.method == 'POST':
        form = AdminAccountCreateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            first_name = form.cleaned_data.get('first_name') or ''
            last_name = form.cleaned_data.get('last_name') or ''
            role = form.cleaned_data['role']

            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
            else:
                username = email
                temp_password = _generate_temp_password()

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=temp_password,
                    first_name=first_name,
                    last_name=last_name,
                )
                Profile.objects.create(user=user, role=role)

                messages.success(
                    request,
                    f"User created successfully. Temporary password: {temp_password}",
                )
                return redirect('auth_admin_create_user')
    else:
        form = AdminAccountCreateForm()

    return render(request, 'auth_custom/admin_create_user.html', {'form': form})


@login_required
@role_required(['admin'])  # Superusers bypass this anyway
def users_list(request):
    """List all users for management"""
    users = User.objects.all().select_related('profile')
    context = {'users': users}
    return render(request, 'auth_custom/users.html', context)

