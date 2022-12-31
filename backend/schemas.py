from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class ProjectBase(BaseModel):
    title: str
    description: str
    image_url: str
    tech_stack: str
    live_link: Optional[str] = None
    github_link: Optional[str] = None
    category: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    message: str

class ContactMessage(ContactMessageCreate):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True
