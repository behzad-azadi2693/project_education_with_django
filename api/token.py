from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email)
        )

account_activation_token = AccountActivationTokenGenerator()

from django.core.mail import EmailMessage

def send_token(user, request):
    current_site = get_current_site(request)
    subject = 'Activate Your Education Account'
    message = render_to_string('rest_account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })

    email = EmailMessage(
            subject, message, to=[user.email]
        )

    email.send()
