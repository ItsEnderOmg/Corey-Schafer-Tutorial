from fastapi.templating import Jinja2Templates # Frontend ZzzzzZZZZZZZ
from fastapi.staticfiles import StaticFiles # Pal CSS zZzZZZz
# Request de fastrapi tmb es para FrontendzzzZZzZ

from fastapi import FastAPI, Request, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db, engine 
from typing import Annotated
import schemas
import models

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
def home(request: Request, db: db_dependency):

    """La ruta base donde estaran todos los posts, la 'root'. Se muestra el home.html """

    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: db_dependency):

    """Pagina individual de cada post al momento de hacer click. Se muestra el post.html"""

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


@app.get('/users/{user_id}/posts', include_in_schema=False)
def user_posts_page(request: Request, user_id: int, db: db_dependency):

    """Muestra todos los posts de X usuario en el 'user_posts.html'."""

    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


# Function to read all the users     
@app.get('/api/users', response_model=list[schemas.UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(db: db_dependency):
    users = db.execute(select(models.User)).scalars().all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found.")
    return users

    
# Function to return a user by id
@app.get('/api/users/{user_id}', response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
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
@app.post('/api/users', response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
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

# Create a post.
@app.post('/api/posts', response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_new_post(post_data: schemas.PostCreate, db: db_dependency):

    validate_user = db.execute(select(models.User).where(models.User.id == post_data.user_id)).scalars().first()
    if  not validate_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Heeey, that user id doesnt exist.')
        
    new_post = models.Post(
        title = post_data.title,
        content = post_data.content,
        user_id = post_data.user_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# Get all the posts
@app.get('/api/posts', response_model=list[schemas.PostResponse], status_code=status.HTTP_200_OK)
async def get_all_posts(db: db_dependency):
    posts = db.execute(select(models.Post)).scalars().all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No posts found')
    return posts

# Get a specific post by post id
@app.get('/api/posts/{post_id}', response_model=schemas.PostResponse, status_code=status.HTTP_200_OK)
async def get_post_by_id(post_id: int, db: db_dependency):
    query = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = query.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    return post


# Get all the posts of a user
@app.get('/api/posts/{user_id}', response_model=list[schemas.PostResponse], status_code=status.HTTP_200_OK)
async def get_user_posts(user_id: int, db: db_dependency):

    posts_list = db.execute(select(models.Post).where(models.Post.user_id == user_id)).scalars().all()
    if not posts_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return posts_list
    