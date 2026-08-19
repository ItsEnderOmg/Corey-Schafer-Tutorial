""" If you dont import this you'll get an error in line X when refering to the `Post` class because you create it later on the code,
that's called "Forward reference", in python 3.14 it's not neccesary, just in older versions """
from __future__ import annotations

from datetime import datetime, UTC

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
    __tablename__ = 'users'

    # Here, `primary_key=True` also makes it autoincrement
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Corey Schafer used `nullable=False` to make the field required, but that's not neccesary, because if you're using Mapped,
    nullable is set to False by default.

    Mapped[str] already sets nullable=False
    Mapped[str | None] is like nullable=True
    """
    username: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)

    image_file: Mapped[str | None] = mapped_column(String, default=None)

    """ 
    This IS NOT a column in the table, it's just a way to create relationships between tables, this way we can access to the posts
    as if they were class atributes, sqlalchemy does the query automatically for us. For ex:
    
    We want the posts for X user.
        user = db.query(models.User).filter(models.User.id == id).first()
        print(user.posts) 
    And that prints all the posts of the user

    If we weren't using `relationship`, to get the post we would have to do:
        #query the user xd
        posts = db.query(models.Post).filter(models.Post == user.id).all()
        print(posts)

    In short, `relationship` is for comodity, this way you write less code and it's more mantainable.
    """
    posts: Mapped[list[Post]] = relationship(back_populates="author")

    # idk what is this, i will study it later
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    """THIS is what links the post to a user, everytime you create a post, you need to specify to what user the posts belongs to
    by passing a valid `id` of the table `users`."""
    user_id: Mapped[int] = mapped_column(
        # ForeignKey just validates that the ID (the int you passed) is an actual id in the column 'id' of the table 'users'
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    """
    This is the same as the `posts` instance in the `User` class.
    If you have a post, then you can access all the information of the user by calling .author
    
    Example:
        # You already have the post
        post.author

    And post.author has .id, .username, .email, .password, and whatever you have for that user, so when you GET a post, you'll have a 
    nested JSON as the value of `author` with all the information of the user (actually, just the info that you wanted to return, you
    set that in schemas, `author` is an object of `UserResponse` in this case.)
    """
    author: Mapped[User] = relationship(back_populates="posts")

