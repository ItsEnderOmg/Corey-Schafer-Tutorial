from fastapi.templating import Jinja2Templates # Frontend ZzzzzZZZZZZZ
from fastapi.staticfiles import StaticFiles # Pal CSS zZzZZZz

from fastapi import FastAPI, Request, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db, engine 
import schemas
import models

from typing import Annotated

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Corey is writing this in every endpoint idk why
db_dependency = Annotated[Session, Depends(get_db)]

app.mount("/static", StaticFiles(directory='static'), name='static') # Pal CSS zzzZzzZz
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory='templates')

# Una forma de hacer que el endpoint no aparezca en los '/docs', es cambiando el `include_in_schema` a `False`
@app.get('/', include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def root(request: Request):
    return templates.TemplateResponse(request, 'home.html', {"title": "Home"}) 

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# Function to read all the users     
@app.get('/users', response_model=list[schemas.UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(db: db_dependency):
    users = db.execute(select(models.User)).scalars().all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found.")
    return users

    
# Function to return a user by id
@app.get('/users/{user_id}', response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: db_dependency):
    user= db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
    return user


# Function to create a new user
"""
Corey en este caso usa una validacion de q el username y el email (ambos separados) no existan antes de crear el new_user,
yo simplemente lo encierro en un try except con IntegrityError, muchos websites tienen verificacion de email como paso final
para crear una cuenta, asi que a no ser q te hackeen o se te olvide q ya registraste tu email, el error muy probablemente
sea el username.
"""
@app.post('/user', response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: db_dependency):
    
    new_user = models.User(
        username = user.username,
        email = user.email,
        password = user.password
    )

    db.add(new_user)
    try: 
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or Username already in use.")
    db.refresh(new_user)
    db.close()
    return new_user
