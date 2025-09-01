from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os

from database import get_db, User
from auth import (
    get_password_hash, verify_password, create_access_token, 
    verify_token, generate_mfa_secret, generate_qr_code, verify_mfa_code
)
from models import UserCreate, UserLogin, MFAVerify, Token, MFASetup

app = FastAPI(title="PyOTP App", description="Simple MFA application")

# Templates
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(
    email: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        name=name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verify user credentials
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # If MFA is enabled, redirect to MFA verification
    if user.mfa_enabled:
        # Create a temporary token for MFA verification
        temp_token = create_access_token(data={"sub": user.email, "temp": True})
        return RedirectResponse(
            url=f"/mfa-verify?token={temp_token}", 
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # If no MFA, create access token and redirect to dashboard
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/mfa-verify", response_class=HTMLResponse)
async def mfa_verify_page(request: Request, token: str):
    return templates.TemplateResponse("mfa_verify.html", {"request": request, "token": token})

@app.post("/mfa-verify")
async def mfa_verify(
    code: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verify temporary token
    email = verify_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled for this user"
        )
    
    # Verify MFA code
    if not verify_mfa_code(user.mfa_secret, code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    # Create access token and redirect to dashboard
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    email = verify_token(token)
    if not email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/setup-mfa", response_class=HTMLResponse)
async def setup_mfa_page(request: Request, db: Session = Depends(get_db)):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    email = verify_token(token)
    if not email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    if user.mfa_enabled:
        return templates.TemplateResponse("mfa_already_setup.html", {"request": request, "user": user})
    
    # Generate new MFA secret and QR code
    secret = generate_mfa_secret()
    qr_code = generate_qr_code(user.email, secret)
    
    return templates.TemplateResponse("setup_mfa.html", {
        "request": request, 
        "user": user, 
        "secret": secret, 
        "qr_code": qr_code
    })

@app.post("/enable-mfa")
async def enable_mfa(
    request: Request,
    secret: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db)
):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    email = verify_token(token)
    if not email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Verify the MFA code
    if not verify_mfa_code(secret, code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    # Enable MFA for user
    user.mfa_secret = secret
    user.mfa_enabled = True
    db.commit()
    
    return RedirectResponse(url="/dashboard?mfa_enabled=true", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/disable-mfa", response_class=HTMLResponse)
async def disable_mfa_page(request: Request, db: Session = Depends(get_db)):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    email = verify_token(token)
    if not email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    if not user.mfa_enabled:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("disable_mfa.html", {"request": request, "user": user})

@app.post("/disable-mfa")
async def disable_mfa(
    request: Request,
    code: str = Form(...),
    db: Session = Depends(get_db)
):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    email = verify_token(token)
    if not email:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    if not user.mfa_enabled:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    # Verify the MFA code before disabling
    if not verify_mfa_code(user.mfa_secret, code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    # Disable MFA for user
    user.mfa_secret = None
    user.mfa_enabled = False
    db.commit()
    
    return RedirectResponse(url="/dashboard?mfa_disabled=true", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
