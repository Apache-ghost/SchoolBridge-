from utils import send_otp
from params import from_email

if __name__ == "__main__":
    print("Sending test OTP email...")
    result = send_otp(from_email, otp_code="123456", purpose="Test OTP")
    print(result)
