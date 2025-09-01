from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import pyotp
import qrcode
import base64
from io import BytesIO
from PIL import Image

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

def generate_mfa_secret():
    """Generate a new MFA secret for Google Authenticator"""
    return pyotp.random_base32()

def generate_qr_code(email: str, secret: str):
    """Generate QR code for Google Authenticator"""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=email,
        issuer_name="PyOTP App"
    )
    
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    # Convert PIL image to PNG format
    img = img.convert('RGB')
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_mfa_code(secret: str, code: str):
    """Verify MFA code from Google Authenticator"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
