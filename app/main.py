from fastapi import FastAPI, Depends, HTTPException, Request, Response
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from contextlib import asynccontextmanager
#from jinja2 import Template 
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, DictLoader
from fastapi.responses import HTMLResponse, RedirectResponse
import asyncio
import os
from database import get_db,  AsyncSessionLocal
import models
import schemas
import helfun
import auth
#from temp_cache import template_cache




directory = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory)



env = Environment(
    loader=DictLoader(helfun.template_cache),
    cache_size=-1  
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    
    try:
        print("Warming up template cache...")
        async with AsyncSessionLocal() as db:

            await helfun.temp_cache(db) 
        print(" Template cache loaded successfully into memory!")
    except Exception as e:
        print(f" Failed to warm up template cache: {e}")
        
    yield  
    print("VibbersBlog don't want to shut down but was forced to")
  
    
app = FastAPI(lifespan=lifespan)



@app.get("/is_token_verified")
async def token_verify_satisfaction_watch(request: Request, db:AsyncSession = Depends(get_db)):
    '''Just to verify if the token is valid or not(No real use just for satisfaction)'''
    satisfy = await helfun.cookie_get_verify(request,db)
    
    return satisfy
    


@app.post("/blogs/create")
async def create_new_blog(payload: schemas.BlogCreate, 
    current_user: models.User = Depends(helfun.cookie_get_verify),
    db: AsyncSession = Depends(get_db)):
    '''Uses helper function grom helfun to create a new blog post. Currently there is no page available
    to edit/change blogs on frontend like most of the CMS/blog sites give the option to. Because to do that
    I need to add auth/security users and passwords which is a pain in the ass I'll let it slide for now'''
        
    response = await helfun.create_new_blog(payload=payload, db=db) 
    
    return response
    #or just return await helfun.create_new_blog(payload,db) IDK which to use 



@app.get("/blog/{slug}")
async def get_blog_with_slug(request: Request, slug:str,db: AsyncSession = Depends(get_db)):
    
    query = select(models.Blog).where(models.Blog.slug == slug)
    
    result = await db.execute(query)
  
    
    
    blog = result.scalar_one_or_none()
    
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    curr_views = blog.views
    id = blog.template
    template_id = id
    
    await update_views(slug, curr_views, db)
    
    try:
        template = env.get_template(str(template_id))
    except Exception:
        raise HTTPException(status_code=500, detail="Template not found in cache")
        
    #Pending: if a new template is created it wont automatically append to the cache, only restarting the server does it
    rendered_content = template.render(post=blog)
    
    return HTMLResponse(content=rendered_content)



async def update_views(slug:str,views:int, db: AsyncSession):
    '''Views are not based on IP just refreshing the site will add new views but I'm focusing more on other funs
    for now, might change the views to IP based later(never)'''
    
    new_views = views + 1
    query2 = update(models.Blog).where(models.Blog.slug == slug).values(views = new_views)
    
    result = await db.execute(query2)
    await db.commit()
    return ""

@app.put("/blogs/update/{slug}")
async def Update_blog(slug:str, payload: schemas.BlogUpdate,current_user: models.User = Depends(helfun.cookie_get_verify), db: AsyncSession = Depends(get_db)):
    
    return await helfun.edit_blogs(slug=slug, payload=payload, db=db)
    

@app.delete("/blogs/delete/{slug}")
async def delete_blog(slug:str, 
    current_user: models.User = Depends(helfun.cookie_get_verify),                  
    db : AsyncSession = Depends(get_db)):
    
    return await helfun.del_blog(slug,db)

@app.get("/")
async def home_page(request: Request):
        
        
   return RedirectResponse(url="/home", status_code=307)
    

#@app.post("/blogs/template/create/{new_template}")
#async def create_template(payload: schemas.Template_create):
#    return "your page is ready"
    

#@app.get("/debug-cache")
#async def debug_cache():
#    '''Only used for testing purposes might need to comment out in prod'''
#    return {"cache_contents": template_cache}
 
 
@app.get("/blogs", response_model=schemas.CountBlog)
async def get_all_blogs(request: Request,st: int = 0, end: int = 12, db: AsyncSession = Depends(get_db)):
    '''This feature doesn't have a page LOL. But for future purpose I need this'''
    
    count, blog_list = await asyncio.gather(
        helfun.get_blog_count(db=db),
        helfun.get_blog_list(st=st, end=end, db=db)) 
    
    try:
        template = env.get_template("6")
    except Exception:
        raise HTTPException(status_code=500, detail="Blog list template not found in cache")
    
    rendered_content = template.render(
        count=count,
        blogs=blog_list,
        st=st,
        end=end
        )    
    
    return HTMLResponse(content=rendered_content)



@app.get("/templates", response_model=List[schemas.TemplateResponse])
async def get_templates(st: int, end:int,db:  AsyncSession = Depends(get_db)):
    '''I don't see why I need a templates page in the website. So no use apparently'''
    
    response = await helfun.get_template_list(st=st, end=end, db=db)
    return response







#user creation
@app.post("/create_user")
async def create_user(payload: schemas.CreateUser,
    current_user: models.User = Depends(helfun.cookie_get_verify),
    db: AsyncSession = Depends(get_db)):
    
    run = await helfun.create_user(payload,db)
    
    return run

@app.put("/login")
async def verify_login(response:Response, payload:schemas.VerifyUser, db: AsyncSession = Depends(get_db)):
    '''Login and automatically creates a token and a session id'''
    
    jama = schemas.TokenData(**payload.model_dump())
    
    confirm = await helfun.verify_user(payload,db)
    
    if confirm:
    
      gama = auth.create_access_token(jama.model_dump())
    
    if gama:
    
      response.set_cookie(
          key='user_access',
          value=gama,
          httponly=True,    
          secure=True,     
          samesite="lax",  
          max_age=86400     
      )
    
    return f"User with {payload.username} is verified"

@app.get("/{slug}")
async def extra_page(slug:str,db: AsyncSession = Depends(get_db)):
    '''The twister page. Instead of blogs you can have resume, about page, contacts and anything, sky is the limit'''
    
    query = select(models.Blog).where(models.Blog.is_blog==False, models.Blog.slug==slug)
    
    result = await db.execute(query)
    
    page = result.scalar_one_or_none()
    
    if page is None:
        raise HTTPException(status_code=404, detail="page post not found")
    
    temp_id = page.template
    
    try:
        template = env.get_template(str(temp_id))
    except Exception:
        raise HTTPException(status_code=500, detail="Template not found in cache")
        
    #Pending: if a new template is created it wont automatically append to the cache, only restarting the server does it
    rendered_content = template.render(post=page)
  
    
    return HTMLResponse(content=rendered_content)