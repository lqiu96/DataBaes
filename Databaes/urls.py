"""Databaes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

#from account.views import UserRegistrationFormView, LoginView, logout_view
from . import views
from user_profile.views import SignupView
from payment.views import customPaymentMethodCreateView

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^$', views.homepage, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^crate/', include('Crate.urls')),
    url(r"^account/signup/$", SignupView.as_view(), name="account_signup"),
    url(r"^payments/payment-methods/create/$", customPaymentMethodCreateView.as_view(), name="pinax_stripe_payment_method_create"),
    url(r"^account/", include("account.urls")),
    url(r'^payments/', include('pinax.stripe.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
