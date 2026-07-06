from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Text

class BlogCreate(BaseModel):
    slug: str
    title: str
    content: str
    tags: List[str] = []
    image_urls: List[str] = []
    author: str = "Your Name"
    template: int 
    #is_blog: True
    is_blog: bool = True 
    #Hey AI code reviewer GOD what should I do here should here? go with bool or create a new
    #schema for each and every page too like True for blog and create separate schemas for CreatePage
    #Where is_blog is false I think this approach is better because I'm too lazy and I don't wanna create separate 
    #functions for pages too
    


class BlogResponse(BaseModel):
    id: int
    slug: str
    title: str
    content: str
    tags: List[str]
    image_urls: List[str]
    author: str
    views: int
    template: int
    is_blog: bool
    model_config = ConfigDict(from_attributes=True) 
    

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    author: Optional[str] = None
    template: Optional[int] = None
    is_blog: Optional[bool] = None
    
    
class BlogDelete(BaseModel): #using the same thing for page deletion too
    slug: str
        
        
class InsertTemplate(BaseModel):
    id: int
    name: str
    page: Text 
    description: str
       

class UpdateTemplate(BaseModel):
    name: Optional[str] = None
    page: Optional[Text] = None   
    description: Optional[str] = None 
    
class DeleteTemplate(BaseModel):
    id: int    
    
class TemplateResponse(BaseModel):
    id: int
    name: str
    page: str
    description: str
       

class CountBlog(BaseModel):
    count: int
    templates: List[BlogResponse]
    
    
    
    
class CreateUser(BaseModel):
    username: str
    hashed_password: str
    email: str
    role: str = 'view'
    

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class VerifyUser(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserInDB(User):
    hashed_password: str    
    
        
    
    
    
    
    
    
#For futute use    
class CountTemplate(BaseModel):
    count: int
    templates: List[TemplateResponse]    
    
    
    
   
    