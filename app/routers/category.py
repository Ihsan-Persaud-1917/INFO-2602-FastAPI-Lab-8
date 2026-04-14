from sqlmodel import select
from fastapi import APIRouter, HTTPException, status

from app.database import SessionDep
from app.models import *
from app.auth import AuthDep

category_router = APIRouter(tags = ["Category Management"])

def get_todo(todo_id: int, db: SessionDep, user: AuthDep) -> Todo:
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or access denied"
        )
    return todo

def get_category(cat_id: int, db: SessionDep, user: AuthDep) -> Category:
    category = db.exec(
        select(Category).where(
            Category.id == cat_id,
            Category.user_id == user.id
        )
    ).one_or_none()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found or access denied"
        )

    return category

@category_router.post("/category", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
def create_category(db:SessionDep, user: AuthDep, category_data: CategoryCreate):
    new_category = Category(user_id=user.id, text=category_data.text)
    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to perform request"
        )
        
@category_router.post("/todo/{todo_id}/category/{cat_id}", status_code=status.HTTP_202_ACCEPTED, response_model=TodoResponse)
def add_category_to_todo(todo_id:int, cat_id:int, db:SessionDep, user:AuthDep):
    todo = get_todo(todo_id, db, user)
    
    category = get_category(cat_id, db, user)
    
    if category not in todo.categories:
        todo.categories.append(category)
        db.commit()
        
    return todo
    
@category_router.delete("/todo/{todo_id}/category/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_from_todo(todo_id:int, cat_id:int, db:SessionDep, user:AuthDep):
    todo = get_todo(todo_id, db, user)
    
    category = get_category(cat_id, db, user)
    
    if category in todo.categories:
        todo.categories.remove(category)
        db.commit()
    
@category_router.get("/category/{cat_id}/todos", status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
def list_all_todos_in_category(cat_id:int, db:SessionDep, user:AuthDep):
    category = get_category(cat_id, db, user)
        
    return category.todos