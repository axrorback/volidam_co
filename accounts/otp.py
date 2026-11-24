import secrets
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from accounts.models import OTPVerification
from accounts.tasks import send_otp
from django.db import transaction

def create_phone_otp(phone: str):

    otp = str(secrets.randbelow(900000) + 100000)

    with transaction.atomic():

        verification = OTPVerification.objects.create(
            phone=phone,
            otp_hash=make_password(otp),
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        transaction.on_commit(
            lambda: send_otp.delay(
                phone=phone,
                otp=otp,
                verification_id=str(verification.id)
            )
        )

    return verification