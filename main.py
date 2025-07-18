from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from app.routers import insights
from app.database.database import engine
from app.database.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="An API to fetch insights from Shopify stores",
    version="1.0.0"
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(insights.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)