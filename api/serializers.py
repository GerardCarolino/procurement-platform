from rest_framework import serializers
from django.utils import timezone
from procurements.models import Procurement, Agency
from bids.models import Bid, Award
from users.models import CustomUser


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Agency
        fields = ['id', 'name', 'department', 'address']


class ProcurementSerializer(serializers.ModelSerializer):
    agency          = AgencySerializer(read_only=True)
    status_display  = serializers.CharField(source='get_status_display',   read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_open         = serializers.SerializerMethodField()
    bid_count       = serializers.SerializerMethodField()

    class Meta:
        model  = Procurement
        fields = [
            'id', 'reference_number', 'title', 'description',
            'agency', 'category', 'category_display',
            'status', 'status_display',
            'approved_budget', 'bid_open_date',
            'is_open', 'bid_count',
            'created_at', 'updated_at',
        ]

    def get_is_open(self, obj):
        return obj.is_open()

    def get_bid_count(self, obj):
        return obj.bids.count()


class VendorPublicSerializer(serializers.ModelSerializer):
    """Safe public view of a vendor — no sensitive fields."""
    class Meta:
        model  = CustomUser
        fields = ['id', 'username', 'organization']


class BidSerializer(serializers.ModelSerializer):
    submitted_by   = VendorPublicSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    bid_amount     = serializers.SerializerMethodField()

    class Meta:
        model  = Bid
        fields = [
            'id', 'procurement', 'submitted_by',
            'bid_amount', 'technical_proposal',
            'status', 'status_display',
            'submitted_at',
        ]

    def get_bid_amount(self, obj):
        """
        Field masking: return amount only after bid_open_date.
        Returns None with a sealed flag before opening.
        """
        if obj.is_amount_visible():
            return str(obj.bid_amount)
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['bid_amount'] is None:
            data['sealed'] = True
            data['bid_amount'] = 'sealed'
        else:
            data['sealed'] = False
        return data


class AwardSerializer(serializers.ModelSerializer):
    procurement = ProcurementSerializer(read_only=True)
    winning_bid = BidSerializer(read_only=True)

    class Meta:
        model  = Award
        fields = ['id', 'procurement', 'winning_bid', 'award_date', 'remarks']