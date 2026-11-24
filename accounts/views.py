import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import SMSLog
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import login, get_user_model
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import OTPVerification
from .otp import create_phone_otp
from .utils import get_user_dashboard_url

User = get_user_model()



@csrf_exempt
@require_POST
def eskiz_sms_callback(request):

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"},status=400)

    request_id = data.get("request_id")
    provider_status = data.get("status")

    if not request_id or not provider_status:
        return JsonResponse({"error": "Missing required fields"},status=400)

    try:
        sms = SMSLog.objects.get(request_id=request_id)

    except SMSLog.DoesNotExist:
        return JsonResponse({"error": "SMS not found"},status=404)

    status_mapping = {
        "DELIVRD": SMSLog.Status.DELIVERED,
        "UNDELIV": SMSLog.Status.FAILED,
        "EXPIRED": SMSLog.Status.EXPIRED,
        "REJECTD": SMSLog.Status.REJECTED,
    }

    sms.status = status_mapping.get(provider_status,SMSLog.Status.UNKNOWN)
    sms.provider_status = provider_status
    sms.message_id = data.get("message_id")
    sms.sms_count = int(data.get("sms_count") or 0)
    sms.callback_data = data

    if sms.status == SMSLog.Status.DELIVERED:
        sms.delivered_at = timezone.now()

    sms.save()

    return JsonResponse({"success": True,"message": "Callback processed"})


def phone_login(request):

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        phone = re.sub(r"\D", "", phone)

        if phone.startswith("998"):
            pass
        elif len(phone) == 9:
            phone = "998" + phone
        else:
            return render(request, "accounts/login.html", {
                "error": "Telefon raqami noto'g'ri."
            })

        if not re.fullmatch(r"998\d{9}", phone):
            return render(request, "accounts/login.html", {
                "error": "Telefon raqami noto'g'ri."
            })

        verification = create_phone_otp(phone)
        request.session["otp_phone"] = phone
        request.session["otp_verification_id"] = str(verification.id)

        return redirect("verify_phone")

    return render(request, "accounts/login.html")




def verify_phone(request):

    phone = request.session.get("otp_phone")
    verification_id = request.session.get(
        "otp_verification_id"
    )

    if not phone or not verification_id:
        return redirect("login")

    if request.method == "POST":

        code = request.POST.get("code", "").strip()

        if not code.isdigit() or len(code) != 6:
            return render(request, "accounts/verify.html", {
                "error": "6 xonali kodni kiriting.",
                "phone": phone
            })

        with transaction.atomic():

            verification = (
                OTPVerification.objects
                .select_for_update()
                .filter(
                    id=verification_id,
                    phone=phone,
                    status=OTPVerification.Status.PENDING
                )
                .first()
            )

            if not verification:
                return render(request, "accounts/verify.html", {
                    "error": "Tasdiqlash so'rovi topilmadi.",
                    "phone": phone
                })

            if verification.is_expired():

                verification.status = OTPVerification.Status.EXPIRED
                verification.save(update_fields=["status"])

                return render(request, "accounts/verify.html", {
                    "error": "OTP muddati tugagan.",
                    "phone": phone
                })

            if verification.attempts >= verification.max_attempts:

                verification.status = OTPVerification.Status.FAILED
                verification.save(update_fields=["status"])

                return render(request, "accounts/verify.html", {
                    "error": "Urinishlar soni tugadi.",
                    "phone": phone
                })

            verification.attempts += 1

            if not check_password(code, verification.otp_hash):

                verification.save(update_fields=["attempts"])

                return render(request, "accounts/verify.html", {
                    "error": "Tasdiqlash kodi noto'g'ri.",
                    "phone": phone
                })

            verification.status = OTPVerification.Status.VERIFIED
            verification.verified_at = timezone.now()

            verification.save(
                update_fields=[
                    "status",
                    "verified_at",
                    "attempts"
                ]
            )

        user = User.objects.filter(phone=phone).first()
        request.session.pop("otp_phone", None)
        request.session.pop("otp_verification_id", None)

        if user:
            login(request, user)
            return redirect(get_user_dashboard_url(user))

        request.session["verified_phone"] = phone

        return redirect("onboarding")

    return render(request, "accounts/verify.html", {
        "phone": phone
    })


def profile_onboarding(request):

    phone = request.session.get("verified_phone")

    if not phone:
        return redirect("login")

    user = User.objects.filter(phone=phone).first()

    if user:
        request.session.pop("verified_phone", None)

        if not user.is_phone_verified:
            user.is_phone_verified = True
            user.save(update_fields=["is_phone_verified"])

        login(request, user)

        return redirect("profile")

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()

        if not full_name:
            return render(request, "accounts/profile_onboarding.html", {
                "phone": phone,
                "error": "Ism va familiyangizni kiriting."
            })

        with transaction.atomic():

            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    "full_name": full_name,
                    "is_phone_verified": True,
                    "role": User.Role.CUSTOMER,
                }
            )

            if not created and not user.is_phone_verified:
                user.is_phone_verified = True
                user.save(update_fields=["is_phone_verified"])

            if not user.has_usable_password():
                user.set_unusable_password()
                user.save()

        request.session.pop("verified_phone", None)

        login(request, user)

        return redirect("profile")

    return render(request, "accounts/profile_onboarding.html", {
        "phone": phone
    })


@login_required
def profile(request):
    return render(request, "accounts/profile.html")