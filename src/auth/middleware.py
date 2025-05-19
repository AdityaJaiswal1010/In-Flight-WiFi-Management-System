from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_utils import decode_access_token

auth_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    user_data = decode_access_token(token)
    return user_data  # e.g., { "user_id": "abc123", "email": "xyz@abc.com" }
