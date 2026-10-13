from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from apps.users.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST, require_http_methods
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q


def _is_superuser(user):
    return user.is_superuser


def _regular_users():
    return User.objects.filter(is_superuser=False)


# ---------- PROFILE / PASSWORD (sidebar popup) ----------
def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def profile_edit(request):
    if request.method == 'POST':
        section = request.POST.get('section')
        ajax = _is_ajax(request)

        if section == 'profile':
            email = request.POST.get('email', '').strip()
            username = request.POST.get('username', '').strip()

            if not username:
                error = 'Username is required.'
            elif not email:
                error = 'Email is required.'
            elif User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                error = 'That username is already taken.'
            elif User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                error = 'That email is already in use.'
            else:
                error = None
                user = request.user
                user.username = username
                user.email = email
                user.first_name = request.POST.get('first_name', '').strip()
                user.middle_name = request.POST.get('middle_name', '').strip()
                user.last_name = request.POST.get('last_name', '').strip()
                bd = request.POST.get('birthday') or None
                user.birthday = bd
                user.save()
                user.refresh_from_db()

            if ajax:
                if error:
                    return JsonResponse({'status': 'error', 'error': error}, status=400)
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profile updated successfully.',
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'middle_name': user.middle_name,
                        'last_name': user.last_name,
                        'birthday': user.birthday.strftime('%Y-%m-%d') if user.birthday else '',
                    },
                })
            if error:
                messages.error(request, error)
            else:
                messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')

        if section == 'password':
            current = request.POST.get('current_password', '')
            new = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')

            if not request.user.check_password(current):
                error = 'Current password is incorrect.'
            elif len(new) < 8:
                error = 'New password must be at least 8 characters.'
            elif new != confirm:
                error = 'New passwords do not match.'
            else:
                error = None
                request.user.set_password(new)
                request.user.save()
                update_session_auth_hash(request, request.user)

            if ajax:
                if error:
                    return JsonResponse({'status': 'error', 'error': error}, status=400)
                return JsonResponse({'status': 'success', 'message': 'Password changed successfully.'})
            if error:
                messages.error(request, error)
            else:
                messages.success(request, 'Password changed successfully.')
            return redirect('dashboard')

    return redirect('dashboard')


# PAGE
@login_required(login_url='login')
@user_passes_test(_is_superuser, login_url='dashboard')
def user_list_page(request):
    query = request.GET.get('q', '').strip()

    users_list = _regular_users().order_by('-date_joined')

    if query:
        users_list = users_list.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page', 1)
    users = paginator.get_page(page_number)

    return render(request, 'users/list.html', {
        'users': users,
        'query': query,
    })


# LIST USERS (AJAX)
@login_required(login_url='login')
@user_passes_test(_is_superuser, login_url='dashboard')
def user_list_ajax(request):
    users_list = _regular_users().order_by('-date_joined')
    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page', 1)
    users = paginator.get_page(page_number)
    data = list(users.object_list.values(
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
    ))
    return JsonResponse({
        "data":     data,
        "has_next": users.has_next(),
        "has_prev": users.has_previous(),
        "page":     users.number,
        "pages":    users.paginator.num_pages,
        "total":    users.paginator.count,
    })


# GET SINGLE USER (AJAX)
@login_required(login_url='login')
@user_passes_test(_is_superuser, login_url='dashboard')
def user_get_ajax(request, pk):
    user = get_object_or_404(_regular_users(), pk=pk)
    return JsonResponse({
        "id":         user.id,
        "username":   user.username,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "email":      user.email,
        "is_staff":   user.is_staff,
        "is_active":  user.is_active,
    })


# CREATE / UPDATE USER (AJAX)
@login_required(login_url='login')
@user_passes_test(_is_superuser, login_url='dashboard')
@require_POST
def user_save_ajax(request):
    user_id = request.POST.get("id")

    if user_id:
        user = get_object_or_404(_regular_users(), pk=user_id)
        is_update = True
    else:
        user = User()
        is_update = False

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()

    if not username:
        return JsonResponse({"error": "Username is required."}, status=400)

    dup_qs = User.objects.filter(Q(username=username) | (Q(email=email) & ~Q(email="")))
    if user_id:
        dup_qs = dup_qs.exclude(pk=user_id)
    if dup_qs.filter(username=username).exists():
        return JsonResponse({"error": "That username is already taken."}, status=400)
    if email and dup_qs.filter(email=email).exists():
        return JsonResponse({"error": "That email is already in use."}, status=400)

    user.username   = username
    user.first_name = request.POST.get("first_name", "")
    user.last_name  = request.POST.get("last_name", "")
    user.email      = email
    user.is_staff   = request.POST.get("is_staff") == "true"
    user.is_active  = request.POST.get("is_active") == "true"

    password = request.POST.get("password")
    if password:
        user.set_password(password)
    elif not user_id:
        return JsonResponse({"error": "Password is required for new users."}, status=400)

    try:
        user.save()
    except IntegrityError:
        return JsonResponse({"error": "Could not save user due to a conflict (duplicate username/email)."}, status=400)

    messages.success(
        request,
        f'User "{user.username}" has been {"updated" if is_update else "saved"} successfully.'
    )

    return JsonResponse({
        "status": "success",
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
    })


# DELETE USER (AJAX)
@login_required(login_url='login')
@user_passes_test(_is_superuser, login_url='dashboard')
@require_POST
def user_delete_ajax(request, pk):
    user = get_object_or_404(_regular_users(), pk=pk)
    if request.user == user:
        return JsonResponse({"error": "You cannot delete yourself"}, status=400)
    username = user.username
    user.delete()
    return JsonResponse({
        "status": "deleted",
        "message": f'User "{username}" has been deleted successfully.',
    })