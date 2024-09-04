from fastapi import FastAPI, Response, status, HTTPException, Depends,APIRouter
from typing import List
from ..database import get_db
from sqlalchemy import func
from .. import models,schemas,Oauth2
from sqlalchemy.orm import Session

router=APIRouter(
    prefix="/posts",
    tags=['Posts']

)

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post: schemas.CreatePost,
                db:Session=Depends(get_db),
                current_user:int=Depends(Oauth2.get_curr_users)):
    # cursor.execute(
    #     "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING id",
    #     (post.title, post.content, post.published)
    # )
    # post_id = cursor.fetchone()['id']
    # conn.commit()
    print(current_user.email)
    new_post=models.Post(**post.dict(),owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return  new_post
@router.get("/",response_model=List[schemas.Post]) 
def get_posts(db:Session=Depends(get_db),current_user:int=Depends(Oauth2.get_curr_users),limit:int=10):
    
    print(limit)
    
    posts=db.query(models.Post).limit(limit).all()

    results=db.query(models.Post,func.count(models.Vote.post_id).label("Votes")).join(
        models.Vote, models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id)
    print(results)
    return posts
@router.get("/{id}",response_model=schemas.Post) 
def read_post(id: int,db:Session=Depends(get_db),current_user:int=Depends(Oauth2.get_curr_users)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    # post = cursor.fetchone()
    post=db.query(models.Post).filter(models.Post.id==id).first()
    print(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} not found"
        )
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db:Session=Depends(get_db),current_user:int=Depends(Oauth2.get_curr_users)):
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING id", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==current_user.id)
    post=post_query.first()

    if post==None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    if post.owner_id!=current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"not authorized with current performed request"
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.CreatePost,db:Session=Depends(get_db),current_user:int=Depends(Oauth2.get_curr_users)):

    # cursor.execute(
    #     "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING id",
    #     (post.title, post.content, post.published, id)
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    post=post_query.first()

    if post==None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} not found")
    
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()
