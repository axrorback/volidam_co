from celery import shared_task
from django.conf import settings
from eskiz import EskizSMS
from .models import SMSLog , OTPVerification


@shared_task
def send_otp(phone: str, otp: str, verification_id: str):

    verification = OTPVerification.objects.get(id=verification_id)
    sms_log = SMSLog.objects.create(phone=phone,verification=verification,status=SMSLog.Status.PENDING)

    try:
        with EskizSMS(
            email=settings.ESKIZ_SMS_EMAIL,
            password=settings.ESKIZ_SMS_PASSWORD
        ) as client:

            result = client.sms.send(
                mobile_phone=phone,
                message=(
                    f"volidam.co.uz saytida ro'yxatdan o'tishni tasdiqlash uchun tasdiqlash kodi: {otp}. Kodni hech kimga bermang."
                ),
                from_whom="4546",
                #callback_url=settings.ESKIZ_SMS_CALLBACK_URL
            )

        sms_log.request_id = str(result.id)
        sms_log.provider_status = str(result.status)
        sms_log.status = SMSLog.Status.ACCEPTED
        sms_log.save()

        return str(result.id)

    except Exception as exc:
        sms_log.status = SMSLog.Status.FAILED
        sms_log.error_message = str(exc)
        sms_log.save()

        raise