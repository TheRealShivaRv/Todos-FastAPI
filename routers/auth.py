import models
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from database import SessionLocal, engine
from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from fastapi import FastAPI, Depends, status, APIRouter, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
import sys
sys.path.append("..")


SECRET_KEY = 'cpfqLUOewN146YX3hyCvn0ZMSQxo2rIA'
ALGORITHM = 'HS256'

models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

app = FastAPI()
router = APIRouter(
    prefix="/auth",
    tags=['auth'],
    responses={401: {"user": "Not Authorized"}}
)
templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# This function generates hashed password. Bcyrpt Context is the
# object which hashes the given password using its hash method
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password):
    return bcrypt_context.hash(password)


def verify_password(password, hashed_password):
    return bcrypt_context.verify(password, hashed_password)


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(
        models.Users.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User is not registered')
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Password')
    return user


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {'username': username, 'user_id': user_id}
    if expires_delta:
        encode.update({'exp': datetime.utcnow() + expires_delta})
    else:
        encode.update({'exp': datetime.utcnow() + timedelta(minutes=15)})
    print(encode)
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('username')
        user_id: int = payload.get('user_id')
        if username is None or user_id is None:
            logout(request)
        return {
            'username': username,
            'id': user_id
        }
    except JWTError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not a registered user',
        )


class LoginForm:
    def __init__(self, request: Request):
        self.request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_login_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        # Step 1 - Create form object
        form = LoginForm(request)
        await form.create_login_form()

        # Step 2- Create a desired response object
        response = RedirectResponse(
            "/todos", status_code=status.HTTP_302_FOUND)

        # Step 3 - Send form data to create access token handler and validate it
        try:
            await login_using_access_token(response=response, form_data=form, db=db)
            return response

        except:
            msg = "Invalid username and password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    except:
        msg = "Authentication Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.post("/token")
async def login_using_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # Step - 1 Authenticate user
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Authentication error")
    # Step - 2 Create Acces Token and set the client's cookie
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, token_expires)
    response.set_cookie(key="token", value=token, httponly=True)
    return True


@router.get("/register", response_class=HTMLResponse)
async def create_new_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def create_new_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), password2: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), db: Session = Depends(get_db)):
    validation1 = db.query(models.Users).filter(
        models.Users.username == username).first()
    validation2 = db.query(models.Users).filter(
        models.Users.email == email).first()
    if password != password2 or validation1 is not None or validation2 is not None:
        msg = 'Invalid Registration request'
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    hashed_password = get_hashed_password(password)
    user_model.hashed_password = hashed_password
    user_model.first_name = first_name
    user_model.last_name = last_name

    db.add(user_model)
    db.commit()
    return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = 'Logout successfull'
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="token")
    return response
