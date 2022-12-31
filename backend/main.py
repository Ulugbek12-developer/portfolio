from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, Base, get_db
import models, schemas
from typing import List
from contact_utils import send_telegram_notification

app = FastAPI(title="Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed sample projects if empty
    async with AsyncSession(engine) as session:
        result = await session.execute(select(models.Project))
        if not result.scalars().all():
            sample_projects = [
                models.Project(title="E-Commerce Platform", description="Full-stack multi-vendor marketplace with real-time order tracking and Telegram notifications.", image_url="", tech_stack="Next.js,FastAPI,PostgreSQL,Tailwind", live_link="https://example.com", github_link="https://github.com", category="Web"),
                models.Project(title="Restaurant Admin Panel", description="Premium restaurant management with JWT auth, order management, and live bot notifications.", image_url="", tech_stack="Django,React,SQLite,aiogram", live_link="https://example.com", github_link="https://github.com", category="Web"),
                models.Project(title="AI Telegram Bot", description="Intelligent bot powered by OpenAI GPT for customer support and business workflow automation.", image_url="", tech_stack="Python,aiogram,OpenAI,Redis", live_link="https://t.me/example", github_link="https://github.com", category="Bots"),
                models.Project(title="Laptop Marketplace", description="Multi-vendor marketplace with multi-language support (Uzbek, Russian, English).", image_url="", tech_stack="React,FastAPI,i18next,PostgreSQL", live_link="https://example.com", github_link="https://github.com", category="Web"),
                models.Project(title="AI Content Generator", description="AI-powered tool that generates blog posts, captions, and marketing copy using LangChain.", image_url="", tech_stack="Next.js,LangChain,OpenAI,FastAPI", live_link="https://example.com", github_link="https://github.com", category="AI"),
                models.Project(title="Auto-Reply Bot", description="Telegram bot that classifies and responds to customer inquiries using NLP and custom rules.", image_url="", tech_stack="Python,aiogram,spaCy,SQLite", live_link="https://t.me/example", github_link="https://github.com", category="Bots"),
            ]
            session.add_all(sample_projects)
            await session.commit()

@app.get("/", tags=["Health"])
async def root():
    return {"status": "Portfolio API is running"}

@app.get("/api/projects", response_model=List[schemas.Project], tags=["Projects"])
async def get_projects(category: str = None, db: AsyncSession = Depends(get_db)):
    query = select(models.Project)
    if category and category != "All":
        query = query.where(models.Project.category == category)
    result = await db.execute(query)
    return result.scalars().all()

@app.post("/api/projects", response_model=schemas.Project, tags=["Projects"])
async def create_project(project: schemas.ProjectCreate, db: AsyncSession = Depends(get_db)):
    new_project = models.Project(**project.dict())
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project

@app.delete("/api/projects/{project_id}", tags=["Projects"])
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Project).where(models.Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()
    return {"message": "Deleted successfully"}

@app.post("/api/contact", response_model=schemas.ContactMessage, tags=["Contact"])
async def send_contact(contact: schemas.ContactMessageCreate, db: AsyncSession = Depends(get_db)):
    new_msg = models.ContactMessage(**contact.dict())
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    try:
        await send_telegram_notification(contact.name, contact.email, contact.message)
    except Exception as e:
        print(f"Telegram error: {e}")
    return new_msg
