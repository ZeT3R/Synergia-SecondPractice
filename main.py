from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, auth, database, schemas

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
models.Base.metadata.create_all(bind=database.engine)

# AUTH API
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    hashed = auth.get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed)
    db.add(user)
    db.commit()
    return {"message": "User created"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong credentials")
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# POSTS API
@app.get("/", response_class=HTMLResponse)
def index(request: Request, tag: str = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Post).filter(models.Post.is_hidden == False)
    if tag:
        query = query.join(models.Post.tags).filter(models.models.Tag.name == tag)
    posts = query.order_by(models.models.Post.created_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.post("/posts")
def create_post(title: str = Form(...), content: str = Form(...), tags: str = Form(""), is_hidden: bool = Form(False), 
                user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    post = models.Post(title=title, content=content, is_hidden=is_hidden, author_id=user.id)
    for t_name in tags.split(","):
        if not t_name.strip(): continue
        tag = db.query(models.Tag).filter(models.Tag.name == t_name.strip()).first()
        if not tag: tag = models.Tag(name=t_name.strip())
        post.tags.append(tag)
    db.add(post)
    db.commit()
    return {"status": "ok"}

@app.post("/follow/{user_id}")
def follow(user_id: int, user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    user.following.append(target)
    db.commit()
    return {"status": "followed"}

@app.get("/feed")
def feed(user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    ids = [u.id for u in user.following]
    posts = db.query(models.Post).filter(models.Post.author_id.in_(ids)).all()
    return posts

@app.post("/posts/{post_id}/comment")
def add_comment(post_id: int, text: str = Form(...), user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    comment = models.Comment(text=text, post_id=post_id, author_id=user.id)
    db.add(comment)
    db.commit()
    return {"status": "ok"}

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.author_id == user.id).first()
    db.delete(post)
    db.commit()
    return {"status": "deleted"}
