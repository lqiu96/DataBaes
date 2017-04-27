from django.db.models import Q
import datetime
from django.utils import timezone
from pinax.stripe import models

def has_active_subscription_with_plan(customer, plan_id):
    """
    Checks if the given customer has an active subscription with the given plan

    Args:
        customer: the customer to check
        plan: the plan to check

    Returns:
        True, if there is an active subscription with given plan, otherwise False
    """
    return models.Subscription.objects.filter(
        customer=customer,
        plan_id=plan_id
    ).filter(
        Q(ended_at__isnull=True) | Q(ended_at__gt=timezone.now())
    ).exists()