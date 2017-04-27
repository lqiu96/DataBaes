# Create your views here.

from pinax.stripe.views import PaymentMethodCreateView
from pinax.stripe.actions import customers, sources
from pinax.stripe.mixins import LoginRequiredMixin, CustomerMixin, PaymentsContextMixin
from pinax.stripe.models import Card

class customPaymentMethodCreateView(PaymentMethodCreateView):
    def create_card(self, stripe_token):
        sources.create_card(self.customer, token=stripe_token)
        # Set default source as last added card
        card = Card.objects.filter(customer_id=self.customer.id).order_by("-created_at").first()

        source = card.stripe_id

        customers.set_default_source(self.customer, source)
        