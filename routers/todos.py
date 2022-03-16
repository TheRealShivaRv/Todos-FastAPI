from re import L
from urllib import response
from fastapi import FastAPI, Depends, status, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from typing import Optional
# Creates all database schema
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
app = FastAPI()

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={
        404: {"todo": "Not found"}
    }
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


""" 
class Todo(BaseModel):
    title: str
    description: str
    priority: int
    is_done: bool = Field(default=False)
    user_id: int
 """


@router.get("/", response_class=HTMLResponse)
async def read_all_todos(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    print(user.get("id"))
    query = db.query(models.Todo).filter(
        models.Todo.user_id == user.get("id")).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": query, "user": user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...), priority: int = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = models.Todo()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.is_done = False
    todo_model.user_id = user.get("id")

    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_page(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    query = db.query(models.Todo).filter(models.Todo.id == todo_id).filter(
        models.Todo.user_id == user.get("id")).first()
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": query, "user": user})


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def update_todo_by_id(
    request: Request,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    target = db.query(models.Todo).filter(models.Todo.id == todo_id).filter(
        models.Todo.user_id == user.get("id")).first()
    target.title = title
    target.description = description
    target.priority = priority
    target.is_done = False
    target.user_id = 1

    db.add(target)
    db.commit()

    return RedirectResponse(url=f"/todos/edit-todo/{todo_id}", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo_by_id(request: Request, todo_id: int, db=Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    target = db.query(models.Todo).filter(models.Todo.id == todo_id).filter(
        models.Todo.user_id == user.get("id")).first()
    db.delete(target)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo_by_id(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    target = db.query(models.Todo).filter(models.Todo.id == todo_id).filter(
        models.Todo.user_id == user.get("id")).first()
    target.is_done = not target.is_done
    db.add(target)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
