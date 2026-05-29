from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from procurements.models import Procurement
from bids.models import Bid, Award
from .serializers import (
    ProcurementSerializer, BidSerializer, AwardSerializer
)


class IsAgencyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_agency_admin


class IsVerifiedVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified_vendor


# ── Procurements ──────────────────────────────────────────────────────────────

class ProcurementListView(generics.ListAPIView):
    """
    GET /api/procurements/
    Public — lists all procurements with filters.
    """
    serializer_class   = ProcurementSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Procurement.objects.select_related('agency', 'posted_by').all()
        status   = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category=category)
        return qs


class ProcurementDetailView(generics.RetrieveAPIView):
    """
    GET /api/procurements/<pk>/
    Public — single procurement detail.
    """
    serializer_class   = ProcurementSerializer
    permission_classes = [permissions.AllowAny]
    queryset           = Procurement.objects.select_related('agency', 'posted_by').all()


# ── Bids ──────────────────────────────────────────────────────────────────────

class BidListView(generics.ListAPIView):
    """
    GET /api/procurements/<pk>/bids/
    Agency admins see all bids.
    Vendors see only their own bid.
    """
    serializer_class   = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        procurement = get_object_or_404(Procurement, pk=self.kwargs['pk'])
        return Bid.objects.visible_to(self.request.user, procurement).select_related(
            'submitted_by', 'procurement'
        )


class BidSubmitView(generics.CreateAPIView):
    """
    POST /api/procurements/<pk>/bids/submit/
    Verified vendors only.
    """
    serializer_class   = BidSerializer
    permission_classes = [IsVerifiedVendor]

    def perform_create(self, serializer):
        procurement = get_object_or_404(Procurement, pk=self.kwargs['pk'])

        if not procurement.is_open():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('This procurement is not open for bidding.')

        if Bid.objects.filter(
            procurement=procurement, submitted_by=self.request.user
        ).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('You have already submitted a bid for this procurement.')

        serializer.save(
            procurement=procurement,
            submitted_by=self.request.user,
        )


class MyBidsView(generics.ListAPIView):
    """
    GET /api/bids/mine/
    Returns the authenticated vendor's own bids.
    """
    serializer_class   = BidSerializer
    permission_classes = [IsVerifiedVendor]

    def get_queryset(self):
        return Bid.objects.filter(
            submitted_by=self.request.user
        ).select_related('procurement', 'procurement__agency')


# ── Awards ────────────────────────────────────────────────────────────────────

class AwardListView(generics.ListAPIView):
    """
    GET /api/awards/
    Public — all awarded contracts.
    """
    serializer_class   = AwardSerializer
    permission_classes = [permissions.AllowAny]
    queryset           = Award.objects.select_related(
        'procurement', 'procurement__agency',
        'winning_bid', 'winning_bid__submitted_by',
    ).order_by('-award_date')


# ── Auth check ────────────────────────────────────────────────────────────────

class MeView(APIView):
    """
    GET /api/me/
    Returns the current authenticated user's info.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id':           user.id,
            'username':     user.username,
            'email':        user.email,
            'role':         user.role,
            'organization': user.organization,
            'is_verified':  user.is_verified,
        })