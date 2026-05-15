from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Profile


def akaibara_login(request):
    return render(request, 'auth_custom/akaibara_login.html')



def akaibara_login_submit(request):
    # POST: authenticate + login.
    if request.method != 'POST':
        return redirect('auth_login')

    email = (request.POST.get('email') or '').strip().lower()
    password = request.POST.get('password') or ''

    if not email or not password:
        messages.error(request, 'Email and password are required.')
        return render(request, 'auth_custom/akaibara_login.html')

    user = None
    try:
        from django.contrib.auth.models import User
        u = User.objects.get(email=email)
        user = authenticate(request, username=u.username, password=password)
    except Exception:
        user = None

    if user is None:
        user = authenticate(request, username=email, password=password)

    if user is None:
        messages.error(request, 'Invalid email or password.')
        return render(request, 'auth_custom/akaibara_login.html')

    # ADMIN FIRST LOGIN: only superuser can initially log in.
    # Prototype interpretation from requirements: after admin creates accounts,
    # non-superusers created by admin may login normally.
    # So we only block non-superusers if they do NOT yet have a Profile role.
    if not getattr(user, 'is_superuser', False):
        try:
            Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            messages.error(request, 'Account is not active yet. Ask an admin to create your profile.')
            return render(request, 'auth_custom/akaibara_login.html')

    login(request, user)

    # SUPERUSER BYPASS: superusers skip role check and go straight to dashboard
    if getattr(user, 'is_superuser', False):
        return redirect('/dashboard/')

    # ROLE BASED REDIRECT for regular users
    try:
        profile = Profile.objects.get(user=user)
        role = profile.role
    except Profile.DoesNotExist:
        messages.error(request, 'No role found for your account.')
        return render(request, 'auth_custom/akaibara_login.html')

    if role == 'admin':
        return redirect('/dashboard/')
    if role == 'cashier':
        return redirect('/cashier/')
    if role == 'inspector':
        return redirect('/item-inspection/')

    messages.error(request, 'No role found for your account.')
    return render(request, 'auth_custom/akaibara_login.html')


def akaibara_logout(request):
    logout(request)
    return redirect('auth_login')


# Role-based access decorator

def role_required(allowed_roles):
    def decorator(view_func):
        @login_required
        def _wrapped(request, *args, **kwargs):
            # SUPERUSER BYPASS: Allow unrestricted access for superusers
            if getattr(request.user, 'is_superuser', False):
                return view_func(request, *args, **kwargs)

            try:
                profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return HttpResponseForbidden('No role found.')

            if profile.role not in allowed_roles:
                return HttpResponseForbidden('You do not have access to this page.')

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator




def akaibara_login_orig(request):
    # Kept for reference / rollback.
    return render(request, 'auth_custom/akaibara_login_orig.html')

