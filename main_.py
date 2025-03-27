from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api import views, scraper, chat_endpoint
from services import agent
import time
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    app.state.css_version = int(time.time())
    print(f"CSS Version: {app.state.css_version}")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/how-it-works")
async def how_it_works(request: Request):
    return templates.TemplateResponse("how_it_works.html", {"request": request})

@app.get("/chat")
async def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Include routers
app.include_router(views.router)
app.include_router(scraper.router, prefix="/api")
app.include_router(chat_endpoint.router, prefix="/api")

app.state.ai_agent = agent.RAGAgent()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )