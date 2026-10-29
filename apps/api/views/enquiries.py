from django.utils import timezone
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.enquiries.models import EnquiryRoute, Enquiry, Opportunity, Subscription
from apps.enquiries.throttles import EnquiryIPThrottle, EnquiryEmailThrottle
from apps.enquiries.tasks import process_enquiry
from apps.api.serializers.enquiries import (
    EnquiryRouteSerializer, EnquiryCreateSerializer,
    OpportunityCreateSerializer, SubscriptionSerializer
)
from apps.core.utils import hash_ip
from apps.core.validators import validate_secure_file_upload

class EnquiryRoutesListView(generics.ListAPIView):
    """
    List available active enquiry routing destinations.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = EnquiryRouteSerializer
    queryset = EnquiryRoute.objects.filter(active=True)

class EnquiryCreateView(generics.CreateAPIView):
    """
    Submit a 'Partner With SKAD' or general contact enquiry.
    Includes honeypot detection, IP hashing, email & IP throttling, and unique reference assignment.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = EnquiryCreateSerializer
    throttle_classes = [EnquiryIPThrottle, EnquiryEmailThrottle]

    @extend_schema(summary="Submit Corporate Enquiry", responses={201: dict})
    def perform_create(self, serializer):
        request = self.request
        attachment = request.FILES.get("attachment")
        if attachment:
            validate_secure_file_upload(attachment, max_mb=10)

        hashed_client_ip = hash_ip(request)
        enquiry = serializer.save(
            ip_hash=hashed_client_ip,
            consent_at=timezone.now(),
            privacy_version=getattr(settings, "PRIVACY_POLICY_VERSION", "2026.1"),
        )

        # Trigger async routing pipeline per Page 13 ('Return 201 immediately; do heavy work in Celery')
        try:
            process_enquiry.delay(enquiry.id)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Celery task queueing deferred for enquiry %s: %s", enquiry.id, exc)

        return enquiry

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enquiry = self.perform_create(serializer)
        return Response(
            {
                "reference": enquiry.reference,
                "message": "Enquiry submitted successfully and routed to department owner.",
                "route": enquiry.route.label,
            },
            status=status.HTTP_201_CREATED,
        )

class OpportunityCreateView(generics.CreateAPIView):
    """
    Submit a business venture or founder partnership opportunity.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = OpportunityCreateSerializer
    throttle_classes = [EnquiryIPThrottle]

    def perform_create(self, serializer):
        attachment = self.request.FILES.get("attachment")
        if attachment:
            validate_secure_file_upload(attachment, max_mb=15)
        return serializer.save()

class SubscriptionCreateView(generics.CreateAPIView):
    """
    Newsletter double opt-in subscription submission.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SubscriptionSerializer
    throttle_classes = [EnquiryIPThrottle]

class SubscriptionConfirmView(APIView):
    """
    Confirm newsletter double opt-in subscription via token.
    Per page 11: GET /subscriptions/confirm/
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Confirm Newsletter Subscription",
        parameters=[
            OpenApiParameter(name="token", description="Double opt-in token", required=True, type=str)
        ],
        responses={200: dict, 400: dict},
    )
    def get(self, request):
        token = request.query_params.get("token", "").strip()
        if not token:
            return Response({"error": "Confirmation token is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        subscription = Subscription.objects.filter(opt_in_token=token).first()
        if not subscription:
            return Response({"error": "Invalid or expired confirmation token."}, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.confirmed = True
        subscription.save()
        return Response({"message": "Subscription confirmed successfully. Welcome to SKAD Insights."})
