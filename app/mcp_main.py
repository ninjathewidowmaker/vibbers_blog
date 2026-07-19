from fastmcp import FastMCP
import asyncio
import schemas
from database import AsyncSessionLocal
import helfun
from typing import List
from fastapi import Request, HTTPException
from fastmcp.dependencies import Depends, CurrentRequest
from fastmcp.server.dependencies import get_http_request




mcp = FastMCP("Blog Server") 

async def accept_api(request: Request = CurrentRequest()):
    '''picks api key from headers and verifies using helfun's verify_api_key fun'''
    
    api_key = request.headers.get('vb-mcp-api-key')
    
    if not api_key:
        raise HTTPException(status_code=401, detail='you are not authorised without API key')
    
    async with AsyncSessionLocal() as db:
        response = await helfun.verify_api_key(api_key, db)
    
    if not response:
        raise HTTPException(status_code=401, detail='invalid API key')
    
    return api_key
            
    
    




@mcp.tool(name="create_new_blog",description="Create a new Blog post using this tool.")
async def create_new_blog(payload: schemas.BlogCreate,accept_api:str = Depends(accept_api) ):
    """Creates a new blog post. And also If user asks for a specific template you can check it using the
    get_template tool otherwise template 1 would be default"""
    
    async with AsyncSessionLocal() as db:
        
        response = await helfun.create_new_blog(payload=payload, db=db)
        return response
        
        
@mcp.tool(name='edit_blogs', description = "Edit Blogs using this tool")
async def edit_blogs(slug:str,payload: schemas.BlogUpdate, accept_api:str = Depends(accept_api)):
    '''Use this tool to edit blogs and also before that ask a user if they hold a copy of the original version'''
    
    async with AsyncSessionLocal() as db:
        
        response = await helfun.edit_blogs(slug=slug, payload=payload, db=db)
        
        return response
        
    
@mcp.tool(name='del_blog', description = "Delete Blogs using this tool")
async def del_blog(slug:str,accept_api:str = Depends(accept_api)):
    '''Just pass the slug of the blog you want to delete Remember always ask twice before deleting the blog
    And also use get_blog for confirmation''' 
    
    async with AsyncSessionLocal() as db:
        
        response = await helfun.del_blog(slug, db)
        
        return response
    
@mcp.tool(name='get_blog_list', description = "Get all blogs with name and slug using this tool")
async def get_blog_list():
    '''get all the available blog slug(unq_id), name and template_id using this tool and if user asks to edit/delete particular tool
    use this tool to get the slug then edit/delete
    '''
   
    async with AsyncSessionLocal() as db:
        
        response = await helfun.get_blog_with_names(db)
        
        return response
    
    
@mcp.tool(name='get_blog', description = "Get a single Blog using this tool")
async def get_blog(slug:str):
    '''Use slug as the index to get the blog details.'''
    
    async with AsyncSessionLocal() as db:
        
        response = await helfun.get_blog(slug, db)
        
        return response
    
@mcp.tool(name='create_temp',description='create a new template')
async def create_temp(payload: schemas.InsertTemplate, accept_api:str = Depends(accept_api)):
    '''
    Templates are pure HTML files so according to user's request just create a pure HTML file with js sinppets embedded the HTMF file
    '''

    async with AsyncSessionLocal() as db:
        
        response = await helfun.create_temp(payload=payload, db=db)
        
        return response
    

    
@mcp.tool(name='edit_temp',description='edit a template')
async def edit_temp(id:int, payload: schemas.UpdateTemplate, accept_api:str = Depends(accept_api)):
    '''
    Ask user if they hold a copy of the original template
    ''' 
    async with AsyncSessionLocal() as db:
        
        response = await helfun.edit_temp(id=id, payload=payload, db=db)
        
        return response
    
@mcp.tool(name='delete_temp',description='delete a template')    
async def delete_temp(id:int, accept_api:str = Depends(accept_api)):
    '''Use this tool to delete a template
    schema :id: int
    Ask twice before deleting the template and check get_template tool for confirmation of the template
    '''
    
    async with AsyncSessionLocal() as db:
        
        response = await helfun.delete_temp(id, db)
        
        return response
    

@mcp.tool(name='get_all_template_names', description = 'get all template names to assign a blog with users request')
async def get_all_template_names():
    '''Use this tool to get all the template names with their id's'''
    
    async with AsyncSessionLocal() as db:
        
        response = await helfun.get_template_names_with_id(db)
            
        return response
 
@mcp.tool(name='get_template', description = 'Get the template in case a user asks to edit particular template')
async def get_template(id: int):
    async with AsyncSessionLocal() as db:
       response = await helfun.get_template(id, db=db)
       return response
    
        
        
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=6969)