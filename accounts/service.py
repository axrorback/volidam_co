from django.db import transaction
import secrets
import hashlib
from eskiz import EskizSMS






class UserService:
    @staticmethod
    def generate_otp() -> str:
        return str(100_000 + secrets.randbelow(900_000))

    @staticmethod
    def hash_otp(otp: str) -> str:
        return hashlib.sha256(otp.encode()).hexdigest()

    @staticmethod
    def verify_otp_hash(otp: str, hashed_otp: str) -> bool:
        return UserService.hash_otp(otp) == hashed_otp

