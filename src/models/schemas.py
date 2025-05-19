from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminCredentials(BaseModel):
    password: str

class ConvertRequest(BaseModel):
    amount: int
