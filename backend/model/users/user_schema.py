from pydantic import EmailStr,BaseModel,Field


class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserResponse(BaseModel):
    id:int
    username:str
    email:str                                       

class RefreshRequest(BaseModel):
    refreshtoken:str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str








                                                        