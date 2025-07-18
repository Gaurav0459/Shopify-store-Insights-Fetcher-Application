from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List
import requests
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from app.models.insights import InsightRequest, ShopifyInsights
from app.services.shopify_service import ShopifyService
from app.services.competitor_service import CompetitorService
from app.database.database import get_db
from app.database.repository import InsightsRepository

router = APIRouter(
    prefix="/api/v1",
    tags=["insights"],
)


def validate_shopify_url(website_url: str) -> str:
    """Validate that the URL is a Shopify store"""
    # Normalize URL
    if not website_url.startswith(("http://", "https://")):
        website_url = "https://" + website_url
    
    try:
        # Check if the URL is valid
        response = requests.head(website_url, timeout=10)
        response.raise_for_status()
        
        # Check if it's a Shopify store
        is_shopify = False
        
        # Method 1: Check for Shopify in server headers
        server = response.headers.get("server", "").lower()
        if "shopify" in server:
            is_shopify = True
            
        # Method 2: Try to access products.json
        if not is_shopify:
            parsed_url = urlparse(website_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            products_url = f"{base_url}/products.json"
            
            try:
                products_response = requests.get(products_url, timeout=10)
                if products_response.status_code == 200 and "products" in products_response.json():
                    is_shopify = True
            except:
                pass
        
        if not is_shopify:
            raise HTTPException(status_code=400, detail="The provided URL is not a Shopify store")
            
        return website_url
        
    except requests.RequestException:
        raise HTTPException(status_code=404, detail="Website not found or not accessible")


@router.post("/insights", response_model=ShopifyInsights)
async def get_insights(request: InsightRequest, db: Session = Depends(get_db)):
    """
    Get insights from a Shopify store
    """
    try:
        # Validate the URL
        website_url = validate_shopify_url(str(request.website_url))
        
        # Create service and get insights
        service = ShopifyService(website_url)
        insights = service.get_all_insights()
        
        # Save insights to database
        repository = InsightsRepository(db)
        repository.save_insights(insights)
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/insights/competitors", response_model=List[ShopifyInsights])
async def get_competitor_insights(
    request: InsightRequest,
    limit: int = Query(3, description="Maximum number of competitors to analyze", ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    Get insights from a Shopify store and its competitors
    """
    try:
        # Validate the URL
        website_url = validate_shopify_url(str(request.website_url))
        
        # Get competitor insights
        competitor_service = CompetitorService(website_url)
        competitor_insights = competitor_service.get_competitors_insights(limit=limit)
        
        # Save competitor insights to database
        repository = InsightsRepository(db)
        for insights in competitor_insights:
            repository.save_insights(insights)
        
        return competitor_insights
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")