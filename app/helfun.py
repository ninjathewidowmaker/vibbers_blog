import schemas
from sqlalchemy import select, update, delete
#from typing import List, Annotated, Optional
from database import get_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.orm import Session
import models
import asyncio
from sqlalchemy import func
#from temp_cache import template_cache
#from main import temp_cache
#from main import template_cache


template_cache = {}

async def temp_cache(db: AsyncSession):
    
    query = select(models.Template.id, models.Template.page)
    result = await db.execute(query)
    
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



#Done with this application no noticable bugs here might need a few more funs in future

