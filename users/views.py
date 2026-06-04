from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import VendorRegistrationForm, LoginForm
from .models import CustomUser
from procurements.models import Agency
from procurements.forms import AgencyForm
from axes.models import AccessAttempt                       
from django.http import HttpResponse


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    form = VendorRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(
            request,
            'Account created! Please wait for admin verification before submitting bids.'
        )
        return redirect('users:login')

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


# ── Superuser Admin Panel ─────────────────────────────────────────────────────

def require_superuser(user):
    if not user.is_authenticated or not user.is_staff:
        raise PermissionDenied


@login_required
def vendor_admin_panel(request):
    require_superuser(request.user)

    tab = request.GET.get('tab', 'pending')

    pending  = CustomUser.objects.filter(role='VENDOR', verification_status='PENDING')
    verified = CustomUser.objects.filter(role='VENDOR', verification_status='VERIFIED')
    rejected = CustomUser.objects.filter(role='VENDOR', verification_status='REJECTED')

    # Locked accounts — axes AccessAttempt entries that hit the failure limit
    from django.conf import settings
    failure_limit = getattr(settings, 'AXES_FAILURE_LIMIT', 10)
    locked = AccessAttempt.objects.filter(
        failures_since_start__gte=failure_limit
    ).order_by('-attempt_time')

    context = {
        'tab':      tab,
        'pending':  pending,
        'verified': verified,
        'rejected': rejected,
        'locked':   locked,
        'counts': {
            'pending':  pending.count(),
            'verified': verified.count(),
            'rejected': rejected.count(),
            'locked':   locked.count(),
        },
    }
    return render(request, 'users/vendor_admin_panel.html', context)


@login_required
def vendor_verify(request, pk):
    require_superuser(request.user)
    vendor = get_object_or_404(CustomUser, pk=pk, role='VENDOR')

    if request.method == 'POST':
        vendor.is_verified = True
        vendor.verification_status = 'VERIFIED'
        vendor.save()
        messages.success(request, f'{vendor.organization or vendor.username} has been verified.')

    return redirect(f"{request.META.get('HTTP_REFERER', '/admin-panel/')}#vendor-{pk}")


@login_required
def vendor_reject(request, pk):
    require_superuser(request.user)
    vendor = get_object_or_404(CustomUser, pk=pk, role='VENDOR')

    if request.method == 'POST':
        vendor.is_verified = False
        vendor.verification_status = 'REJECTED'
        vendor.save()
        messages.warning(request, f'{vendor.organization or vendor.username} has been rejected.')

    return redirect(f"/admin-panel/?tab=pending")


@login_required
def vendor_revoke(request, pk):
    require_superuser(request.user)
    vendor = get_object_or_404(CustomUser, pk=pk, role='VENDOR')

    if request.method == 'POST':
        vendor.is_verified = False
        vendor.verification_status = 'PENDING'
        vendor.save()
        messages.warning(request, f'Verification revoked for {vendor.organization or vendor.username}.')

    return redirect('/admin-panel/?tab=verified')


@login_required
def vendor_delete(request, pk):
    require_superuser(request.user)
    vendor = get_object_or_404(CustomUser, pk=pk, role='VENDOR')

    if request.method == 'POST':
        name = vendor.organization or vendor.username
        vendor.delete()
        messages.success(request, f'Vendor account "{name}" has been deleted.')

    return redirect('/admin-panel/')


@login_required
def agency_admin_panel(request):
    require_superuser(request.user)
    agencies = Agency.objects.all().order_by('name')
    form = AgencyForm()
    context = {
        'agencies': agencies,
        'form':     form,
        'count':    agencies.count(),
    }
    return render(request, 'users/agency_admin_panel.html', context)


@login_required
def agency_create(request):
    require_superuser(request.user)
    if request.method == 'POST':
        form = AgencyForm(request.POST)
        if form.is_valid():
            agency = form.save()
            messages.success(request, f'Agency "{agency.name}" created.')
        else:
            messages.error(request, 'Please fix the errors below.')
    return redirect('/admin-panel/agencies/')


@login_required
def agency_edit(request, pk):
    require_superuser(request.user)
    agency = get_object_or_404(Agency, pk=pk)
    if request.method == 'POST':
        form = AgencyForm(request.POST, instance=agency)
        if form.is_valid():
            form.save()
            messages.success(request, f'Agency "{agency.name}" updated.')
        else:
            messages.error(request, 'Please fix the errors below.')
    return redirect('/admin-panel/agencies/')


@login_required
def agency_delete(request, pk):
    require_superuser(request.user)
    agency = get_object_or_404(Agency, pk=pk)
    if request.method == 'POST':
        try:
            name = agency.name
            agency.delete()
            messages.success(request, f'Agency "{name}" deleted.')
        except Exception:
            messages.error(
                request,
                f'Cannot delete "{agency.name}" — it has linked procurements. '
                f'Remove or reassign those procurements first.'
            )
    return redirect('/admin-panel/agencies/')


# ── Locked Accounts ───────────────────────────────────────────────────────────

@login_required
def unlock_account(request, attempt_pk):
    """Unlock a single locked account by deleting its AccessAttempt entry."""
    require_superuser(request.user)
    attempt = get_object_or_404(AccessAttempt, pk=attempt_pk)

    if request.method == 'POST':
        username = attempt.username
        attempt.delete()
        messages.success(request, f'Account "{username}" has been unlocked.')

    return redirect('/admin-panel/?tab=locked')


@login_required
def unlock_all_accounts(request):
    """Unlock all locked accounts at once."""
    require_superuser(request.user)

    if request.method == 'POST':
        count = AccessAttempt.objects.count()
        AccessAttempt.objects.all().delete()
        messages.success(request, f'All {count} locked account(s) have been unlocked.')

    return redirect('/admin-panel/?tab=locked')

def emergency_unlock(request):
    """Temporary emergency view — REMOVE AFTER USE."""
    from axes.models import AccessAttempt
    count = AccessAttempt.objects.count()
    AccessAttempt.objects.all().delete()
    return HttpResponse(f'Done. {count} access attempt(s) cleared.')