from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from .models import Procurement, Agency
from .forms import ProcurementForm
from users.permissions import require_agency_admin


# ── Public views ──────────────────────────────────────────────────────────────

def procurement_list(request):
    procurements = Procurement.objects.select_related('agency', 'posted_by').all()

    category = request.GET.get('category', '')
    status   = request.GET.get('status', '')
    search   = request.GET.get('search', '')

    if category:
        procurements = procurements.filter(category=category)
    if status:
        procurements = procurements.filter(status=status)
    if search:
        procurements = procurements.filter(title__icontains=search)

    paginator    = Paginator(procurements, 10)
    page         = request.GET.get('page')
    procurements = paginator.get_page(page)

    context = {
        'procurements':      procurements,
        'categories':        Procurement.Category.choices,
        'selected_category': category,
        'selected_status':   status,
        'search':            search,
        'total_open':        Procurement.objects.filter(status='OPEN').count(),
        'total_agencies':    Agency.objects.count(),
    }
    return render(request, 'procurements/list.html', context)


def procurement_detail(request, pk):
    procurement = get_object_or_404(
        Procurement.objects.select_related('agency', 'posted_by'),
        pk=pk,
    )
    bid_count = procurement.bids.count() if hasattr(procurement, 'bids') else 0

    context = {
        'procurement': procurement,
        'bid_count':   bid_count,
        'user_can_bid': (
            request.user.is_authenticated and
            request.user.is_verified_vendor and
            procurement.is_open()
        ),
    }
    return render(request, 'procurements/detail.html', context)


# ── Agency Admin dashboard ────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    require_agency_admin(request.user)

    procurements = (
        Procurement.objects
        .select_related('agency', 'posted_by')
        .filter(posted_by=request.user)
        .order_by('-created_at')
    )

    counts = {
        'total':     procurements.count(),
        'open':      procurements.filter(status='OPEN').count(),
        'awarded':   procurements.filter(status='AWARDED').count(),
        'closed':    procurements.filter(status='CLOSED').count(),
        'cancelled': procurements.filter(status='CANCELLED').count(),
    }

    context = {
        'procurements': procurements,
        'counts':       counts,
        'counts_display': [
            ('Total',     counts['total'],     'bi-grid-3x3-gap-fill', 'var(--navy)'),
            ('Open',      counts['open'],      'bi-door-open-fill',    'var(--green)'),
            ('Awarded',   counts['awarded'],   'bi-trophy-fill',       'var(--gold)'),
            ('Closed',    counts['closed'],    'bi-lock-fill',         'var(--gray-500)'),
            ('Cancelled', counts['cancelled'], 'bi-x-circle-fill',     'var(--red)'),
        ],
    }
    return render(request, 'procurements/dashboard.html', context)


@login_required
def procurement_create(request):
    require_agency_admin(request.user)

    if request.method == 'POST':
        form = ProcurementForm(request.POST)
        if form.is_valid():
            procurement = form.save(commit=False)
            procurement.posted_by = request.user
            procurement.save()
            messages.success(request, f'Procurement "{procurement.title}" created successfully.')
            return redirect('procurements:admin_dashboard')
    else:
        form = ProcurementForm()

    context = {'form': form, 'action': 'Create', 'page_title': 'New Procurement'}
    return render(request, 'procurements/procurement_form.html', context)


@login_required
def procurement_edit(request, pk):
    require_agency_admin(request.user)

    procurement = get_object_or_404(Procurement, pk=pk)

    if procurement.posted_by != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProcurementForm(request.POST, instance=procurement)
        if form.is_valid():
            form.save()
            messages.success(request, f'Procurement "{procurement.title}" updated.')
            return redirect('procurements:admin_dashboard')
    else:
        form = ProcurementForm(instance=procurement)

    context = {
        'form':        form,
        'action':      'Edit',
        'page_title':  f'Edit — {procurement.reference_number}',
        'procurement': procurement,
    }
    return render(request, 'procurements/procurement_form.html', context)


@login_required
def procurement_delete(request, pk):
    require_agency_admin(request.user)

    procurement = get_object_or_404(Procurement, pk=pk)

    if procurement.posted_by != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        # Block deletion if bids exist
        if procurement.bids.exists():
            messages.error(
                request,
                f'Cannot delete "{procurement.title}" — it has '
                f'{procurement.bids.count()} submitted bid(s). '
                f'Cancel the procurement instead.'
            )
            return redirect('procurements:admin_dashboard')

        title = procurement.title
        procurement.delete()
        messages.success(request, f'Procurement "{title}" deleted.')
        return redirect('procurements:admin_dashboard')

    context = {'procurement': procurement}
    return render(request, 'procurements/procurement_confirm_delete.html', context)