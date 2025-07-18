from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
import os
import logging

from app.routers import insights
from app.database.database import engine
from app.database.models import Base
from app.utils.error_handlers import setup_error_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("shopify_insights.log")
    ]
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShopInsight",
    description="Extract valuable insights from Shopify stores without using the official API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Set up custom error handlers
setup_error_handlers(app)

# Include routers
app.include_router(insights.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "version": "1.0.0"}

@app.exception_handler(404)
async def custom_404_handler(request: Request, _):
    """Custom 404 page handler"""
    with open(os.path.join(static_dir, "404.html"), "r") as f:
        content = f.read()
    return HTMLResponse(content=content, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)