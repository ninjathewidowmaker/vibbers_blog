import schemas
from sqlalchemy import select, update, delete
#from typing import List, Annotated, Optional
from database import get_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Cookie, Response, Request,HTTPException, status
from sqlalchemy.orm import Session
import models
import asyncio
from sqlalchemy import func
import auth
from jinja2 import Environment, DictLoader
#from temp_cache import template_cache
#from main import temp_cache
#from main import template_cache



template_cache = {}

env = Environment(
    loader=DictLoader(template_cache),
    cache_size=-1  
)

async def temp_cache(db: AsyncSession):
    '''clears old cache and re-writes new one after appending/deleting/updating/editing a template/blog'''
    query = select(models.Template.id, models.Template.page)
    result = await db.execute(query)
    
    if not result:
        raise HTTPException
    
    for id, page in result.all():
        template_cache[str(id)] = page
    
    return template_cache


async def create_new_blog(payload: schemas.BlogCreate, db: AsyncSession = Depends(get_db)):
    '''I know I know I should just use x = paylod.models_dump() and y = models.BlogCreate(**x) but hey this works too why bother change?
    '''
    db_blog = models.Blog(
        slug=payload.slug,
        title=payload.title,
        content=payload.content,
        tags=payload.tags,
        image_urls=payload.image_urls,
        author=payload.author,
        template=payload.template
    )
  
    db.add(db_blog)
    await db.commit()
    await db.refresh(db_blog) 
    
    return {"message": "Your Blog post created a successfully", "blog_id": db_blog.id}



async def edit_blogs(slug:str, payload: schemas.BlogUpdate, db: AsyncSession = Depends(get_db)):
    '''it works too'''
    db_update = select(models.Blog).where(models.Blog.slug == slug)
    
    blug = await db.execute(db_update)
    result = blug.scalar_one_or_none()
    
    if result is None:
        return "Blog not found"
    
    if payload.title is not None:
            result.title = payload.title
    if payload.content is not None:
        result.content = payload.content
    if payload.tags is not None:
        result.tags = payload.tags
    if payload.image_urls is not None:
        result.image_urls = payload.image_urls
    if payload.author is not None:
        result.author = payload.author
    if payload.template is not None:
            result.template = payload.template
    
    await db.commit()
    await db.refresh(result)   
    
    
    return f"Succesfully edited {result.slug}"


#used this dict to test the create blog fun
#raw_payload = {
#    "slug": "testis1", 
#    "title": 'title2', 
#    "content": 'content',
#    "tags": [], 
#    "image_urls": [], 
#    "author": 'author'
#}

async def del_blog(slug:str, db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = delete(models.Blog).where(models.Blog.slug == slug)
    
    result = await db.execute(query)
    
    await db.commit()
    
    return f"blog deleted successufully with slug: {slug}"
    
async def create_temp(payload: schemas.InsertTemplate, db: AsyncSession = Depends(get_db)):
    '''I used the model_dump() method here'''
    data = payload.model_dump()
    
    templ_data = models.Template(**data)
    
    db.add(templ_data)
    await db.commit()
    await db.refresh(templ_data) 
    await temp_cache(db)
    
    #for id, page in templ_data:
    #    template_cache[str(id)] = page
    
    return f"templated createds successufully with id:{templ_data.id}"  

async def edit_temp(id:int ,payload: schemas.UpdateTemplate ,db: AsyncSession = Depends(get_db)):
    '''it works too'''
    db_update = select(models.Template).where(models.Template.id == id)
    
    blug = await db.execute(db_update)
    result = blug.scalar_one_or_none()
    
    if result is None:
        return "Template not found"
    
    if payload.name is not None:
        result.name = payload.name
    if payload.page is not None:
        result.page = payload.page
    if payload.description is not None:
        result.description = payload.description
     
    await db.commit()
    await db.refresh(result) 
    await temp_cache(db)
    
    return "Successfully edites the template"
    
    
async def delete_temp(id:int ,db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = delete(models.Template).where(models.Template.id == id)
    
    result = await db.execute(query)
    
    await db.commit()
    await temp_cache(db)
    
    
    return f"Deleted template successfully with id: {id}"


async def get_blogs(slug:str, db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = select(models.Blog).where(models.Blog.slug == slug)

    result = await db.execute(query)
    
    blog = result.scalar_one_or_none()
    
    return blog
    

async def get_blog_list(st:int ,end:int, db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = select(models.Blog).offset(st).limit(end)
    
    result = await db.execute(query)
    
    blogs = result.scalars().all()
    
    return blogs

async def get_template_list(st:int ,end:int, db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = select(models.Template).offset(st).limit(end)
    
    result = await db.execute(query)
    
    templates = result.scalars().all()
    
    return templates

async def get_blog_count(db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = select(func.count(models.Blog.id))
    
    result = await db.execute(query)
    
    return result.scalar()


async def get_template_names_with_id(db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = select(models.Template.id, models.Template.name)
    
    result = await db.execute(query)
    
    return result.all()




async def get_blog_with_names(db: AsyncSession = Depends(get_db)):
    '''it works too'''
    query = select(models.Blog.slug, models.Blog.title, models.Blog.template)
    
    result = await db.execute(query)
    
    temp = result.all()
    
    answer = {}
    
    for slug, title, template in temp:
        
        answer[slug] = [title, template]
    
    return answer

#IDK if this is how professionals do it? I'm just trying to do my own thing later review the code with Claude or gemini
async def get_hashed_password(username, db:AsyncSession = Depends(get_db)):
    '''Give a username and return a hashpassword. This is a helper function for 's verify_user.'''
    query = select(models.User.hashed_password).where(models.User.username == username)
    
    result = await db.execute(query)
    user_details = result.scalar_one_or_none()
    
    return user_details

#I have to make a function which will verify the username and password and gives a goood to go signal for user to login'
async def verify_user(payload:schemas.VerifyUser, db: AsyncSession = Depends(get_db)):
    '''Get user_details and verify if the details are valid or not. NEXT: check if user has a access token, if yes
    then pass or force to login or maybe just add this if yes or no in the main.py itself.'''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = payload.username
    password = payload.password
    query = (select(models.User.hashed_password)
    .where(models.User.username == username,
    models.User.is_active == True))
    
    result = await db.execute(query)
    user_details = result.scalar()
    if user_details is None:
        raise credentials_exception
    
    hashed_password = user_details
    
    if not auth.verify_password(password, hashed_password):       
        raise credentials_exception
    
    return True #Temoprary fix I should change it to something more reliable

async def create_user(payload:schemas.CreateUser, db: AsyncSession = Depends(get_db)):
    '''takes user_details and returns Success message thumps up'''
    password = payload.hashed_password
    hash_pass = auth.get_hash_pswd(password)
    
    user_data = models.User(
        username = payload.username,
        hashed_password = hash_pass,
        email = payload.email,
        role = 'view'        
    )
    
    db.add(user_data)
    await db.commit()
    await db.refresh(user_data)
    
    return f"User has been successfully created with id {user_data.id}"
        
        
async def cookie_get_verify(request: Request, db: AsyncSession = Depends(get_db)):
    '''Get token from cookie and verify it.'''
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ) 
    
    token = request.cookies.get("user_access")
    
    if not token: 
        raise credentials_exception
        
    
    verify = auth.verify_access_token(token)
    
    if not verify:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please login again",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify.get("username")
    
    if not username:
        raise credentials_exception
    
    query = (select(models.User)
    .where(models.User.username == username,models.User.is_active == True))
    
    in_there = await db.execute(query)
    user = in_there.scalar_one_or_none()
        
    if not user:
        raise credentials_exception
        
    return verify
    

    










#Done with this application no noticable bugs here might need a few more funs in future

