from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Bid, Award
from .forms import BidSubmissionForm
from procurements.models import Procurement
from audit.logger import log_event


@login_required
def submit_bid(request):
    procurement_pk = request.GET.get('procurement') or request.POST.get('procurement')
    procurement = get_object_or_404(Procurement, pk=procurement_pk)

    if not request.user.is_verified_vendor:
        if request.user.verification_status == 'REJECTED':
            messages.error(request, 'Your vendor account has been rejected. Please contact the administrator.')
        else:
            messages.error(request, 'Your account is pending verification. Please wait for admin approval.')
        return redirect('procurements:detail', pk=procurement.pk)

    if not procurement.is_open():
        messages.error(request, 'This procurement is no longer accepting bids.')
        return redirect('procurements:detail', pk=procurement.pk)

    if Bid.objects.filter(procurement=procurement, submitted_by=request.user).exists():
        messages.warning(request, 'You have already submitted a bid for this procurement.')
        return redirect('bids:my_bids')

    form = BidSubmissionForm(
        request.POST or None,
        request.FILES or None,
        procurement=procurement,
        user=request.user,
    )

    if request.method == 'POST' and form.is_valid():
        bid = form.save(commit=False)
        bid.procurement = procurement
        bid.submitted_by = request.user
        bid.save()

        log_event(
            event_type='BID_SUBMITTED',
            user=request.user,
            object_type='Bid',
            object_id=bid.pk,
            detail=f"Bid submitted for {procurement.reference_number}",
            request=request,
        )

        messages.success(request, 'Your bid has been submitted and sealed until the opening date.')
        return redirect('bids:my_bids')

    return render(request, 'bids/submit.html', {
        'form': form,
        'procurement': procurement,
    })


@login_required
def my_bids(request):
    if not request.user.is_vendor:
        messages.error(request, 'This page is for vendors only.')
        return redirect('procurements:list')

    bids = Bid.objects.filter(
        submitted_by=request.user
    ).select_related('procurement', 'procurement__agency')

    return render(request, 'bids/dashboard.html', {
        'bids': bids,
        'view': 'mine',
    })


@login_required
def all_bids(request):
    if not request.user.is_agency_admin:
        messages.error(request, 'Only agency admins can view all bids.')
        return redirect('procurements:list')

    procurement_pk = request.GET.get('procurement')
    procurement = get_object_or_404(Procurement, pk=procurement_pk) if procurement_pk else None

    bids = Bid.objects.select_related(
        'procurement', 'procurement__agency', 'submitted_by'
    )
    if procurement:
        bids = bids.filter(procurement=procurement)

    existing_award = None
    if procurement:
        existing_award = Award.objects.filter(procurement=procurement).first()

    return render(request, 'bids/dashboard.html', {
        'bids':           bids,
        'view':           'all',
        'procurement':    procurement,
        'existing_award': existing_award,
    })


@login_required
def award_bid(request, bid_pk):
    if not request.user.is_agency_admin:
        messages.error(request, 'Only agency admins can award contracts.')
        return redirect('procurements:list')

    bid = get_object_or_404(
        Bid.objects.select_related('procurement', 'submitted_by'),
        pk=bid_pk,
    )
    procurement = bid.procurement

    if procurement.posted_by != request.user:
        messages.error(request, 'You can only award contracts for your own procurements.')
        return redirect('bids:all_bids')

    if Award.objects.filter(procurement=procurement).exists():
        messages.warning(request, 'This procurement has already been awarded.')
        return redirect('bids:all_bids')

    if request.method == 'POST':
        Award.objects.create(
            procurement=procurement,
            winning_bid=bid,
            awarded_by=request.user,
        )

        procurement.status = Procurement.Status.AWARDED
        procurement.save()

        bid.status = Bid.Status.AWARDED
        bid.save()

        log_event(
            event_type='CONTRACT_AWARDED',
            user=request.user,
            object_type='Award',
            object_id=bid.pk,
            detail=f"Contract awarded to {bid.submitted_by.username} for {procurement.reference_number}",
            request=request,
        )

        messages.success(
            request,
            f'Contract awarded to {bid.submitted_by.organization or bid.submitted_by.username}.'
        )
        return redirect('bids:awarded')

    return render(request, 'bids/award_confirm.html', {
        'bid':         bid,
        'procurement': procurement,
    })


def awarded_contracts(request):
    awards = Award.objects.select_related(
        'procurement', 'procurement__agency',
        'winning_bid', 'winning_bid__submitted_by'
    ).order_by('-award_date')

    return render(request, 'bids/awarded.html', {'awards': awards})