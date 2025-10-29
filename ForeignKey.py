from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select
from typing import List, Optional

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI()

# ---- ПРОМЕЖУТОЧНЫЕ ТАБЛИЦЫ ----

class PostTag(SQLModel, table=True):
    post_id: Optional[int] = Field(default=None, foreign_key="post.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

# ---- МОДЕЛИ ----

class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    follower_id: int = Field(foreign_key="user.id")
    followed_id: int = Field(foreign_key="user.id")
    
    follower: "User" = Relationship(
        back_populates="following",
        sa_relationship_kwargs={"foreign_keys": "[Subscription.follower_id]"}
    )
    followed: "User" = Relationship(
        back_populates="followers", 
        sa_relationship_kwargs={"foreign_keys": "[Subscription.followed_id]"}
    )

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    posts: List["Post"] = Relationship(back_populates="author")
    likes: List["Like"] = Relationship(back_populates="user")
    following: List["Subscription"] = Relationship(
        back_populates="follower",
        sa_relationship_kwargs={"foreign_keys": "[Subscription.follower_id]"}
    )
    followers: List["Subscription"] = Relationship(
        back_populates="followed",
        sa_relationship_kwargs={"foreign_keys": "[Subscription.followed_id]"}
    )

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    user_id: int = Field(foreign_key="user.id")

    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    tags: List["Tag"] = Relationship(back_populates="posts", link_model=PostTag)
    likes: List["Like"] = Relationship(back_populates="post")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    post_id: int = Field(foreign_key="post.id")

    post: Post = Relationship(back_populates="comments")

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    posts: List["Post"] = Relationship(back_populates="tags", link_model=PostTag)

class Like(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

    user: User = Relationship(back_populates="likes")
    post: Post = Relationship(back_populates="likes")

# Создаем таблицы
SQLModel.metadata.create_all(engine)

# ---- УТИЛИТЫ ----

def get_db():
    with Session(engine) as session:
        yield session

# ---- ЭНДПОИНТЫ ----

@app.post("/users/", tags=["Authentication"])
def create_user(name: str, db: Session = Depends(get_db)):
    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Tags endpoints
@app.post("/tags/", tags=["Tags"])
def create_tag(name: str, db: Session = Depends(get_db)):
    existing_tag = db.exec(select(Tag).where(Tag.name == name)).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    tag = Tag(name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@app.get("/tags/", tags=["Tags"])
def get_all_tags(db: Session = Depends(get_db)):
    tags = db.exec(select(Tag)).all()
    return tags

@app.get("/tags/{tag_id}/posts/", tags=["Tags"])
def get_posts_by_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag.posts

# Posts endpoints
@app.post("/posts/", tags=["Posts"])
def create_post(title: str, content: str, user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    post = Post(title=title, content=content, user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@app.post("/posts/{post_id}/tags/", tags=["Posts"])
def add_tags_to_post(post_id: int, tag_ids: List[int], db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    tags = db.exec(select(Tag).where(Tag.id.in_(tag_ids))).all()
    if len(tags) != len(tag_ids):
        raise HTTPException(status_code=404, detail="Some tags not found")
    
    for tag in tags:
        if tag not in post.tags:
            post.tags.append(tag)
    
    db.commit()
    db.refresh(post)
    return post

@app.get("/posts/{post_id}/tags/", tags=["Posts"])
def get_post_tags(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.tags

# Comments endpoints
@app.post("/comments/", tags=["Comments"])
def create_comment(content: str, post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = Comment(content=content, post_id=post_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@app.get("/posts/{post_id}/comments/", tags=["Comments"])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.comments

# Likes endpoints
@app.post("/posts/{post_id}/like/", tags=["Likes"])
def like(post_id: int, user_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_like = db.exec(
        select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="User already liked this post")
    
    new_like = Like(user_id=user_id, post_id=post_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return {"message": "Post liked successfully"}

@app.get("/posts/{post_id}/likes/", tags=["Likes"])
def likes_users(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    likes_count = len(post.likes)
    users_who_liked = [like.user.name for like in post.likes]
    
    return {
        "post_id": post_id,
        "likes": likes_count,
        "users": users_who_liked
    }

# Follow/Subscription endpoints
@app.post("/users/{user_id}/follow/{target_id}/", tags=["Social"])
def follow(user_id: int, target_id: int, db: Session = Depends(get_db)):
    if user_id == target_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    follower = db.get(User, user_id)
    followed = db.get(User, target_id)
    if not follower or not followed:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db.exec(select(Subscription).where(Subscription.follower_id == user_id, Subscription.followed_id == target_id)).first():
        raise HTTPException(status_code=400, detail="Already following this user")
    
    db.add(Subscription(follower_id=user_id, followed_id=target_id))
    db.commit()
    
    return {"message": f"User {user_id} now follows user {target_id}"}

@app.get("/users/{user_id}/followers/", tags=["Social"])
def get_followers(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    followers = [subscription.follower for subscription in user.followers]
    return [{"id": follower.id, "name": follower.name} for follower in followers]

@app.get("/users/{user_id}/following/", tags=["Social"])
def get_following(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    following = [subscription.followed for subscription in user.following]
    return [{"id": followed.id, "name": followed.name} for followed in following]

# User-related endpoints
@app.get("/users/{user_id}/posts/", tags=["Users"])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user.name, "posts": [p.title for p in user.posts]}

@app.get("/users/posts/count/", tags=["Users"])
def get_users_post_count(db: Session = Depends(get_db)):
    users = db.exec(select(User)).all()
    result = []
    for user in users:
        post_count = len(user.posts)
        result.append({
            "user": user.name,
            "post_count": post_count
        })
    return result

# Feed endpoint
@app.get("/feed/{user_id}/", tags=["Feed"])
def get_feed(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    following_users = db.exec(select(Subscription).where(Subscription.follower_id == user_id)).all()
    followed_ids = [s.followed_id for s in following_users]
    
    if not followed_ids:
        return {
            "user": user.name,
            "feed": []
        }
    
    posts = db.exec(select(Post, User.name).join(User, Post.user_id == User.id).where(Post.user_id.in_(followed_ids))).all()
    feed_items = []
    for post, author_name in posts:
        feed_items.append({
            "author": author_name,
            "title": post.title,
            "content": post.content
        })
    
    return {
        "user": user.name,
        "feed": feed_items
    }