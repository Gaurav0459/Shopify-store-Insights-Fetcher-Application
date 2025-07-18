import re
import logging
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.services.shopify_service import ShopifyService
from app.models.insights import ShopifyInsights

logger = logging.getLogger(__name__)


class CompetitorService:
    def __init__(self, website_url: str):
        self.website_url = website_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get_domain_name(self, url: str) -> str:
        """Extract domain name from URL without TLD"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        # Remove www. and .com/.co etc.
        domain = domain.replace("www.", "")
        domain = re.sub(r'\.[a-z]{2,}$', '', domain)
        return domain
    
    def _search_competitors(self, brand_name: str, limit: int = 5) -> List[str]:
        """Search for competitors using a search engine"""
        search_queries = [
            f"{brand_name} competitors",
            f"brands like {brand_name}",
            f"alternatives to {brand_name}"
        ]
        
        competitors = []
        
        for query in search_queries:
            try:
                # Use DuckDuckGo as it's more API-friendly
                search_url = f"https://html.duckduckgo.com/html/?q={query}"
                response = self.session.get(search_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract search results
                results = soup.select(".result__title")
                for result in results:
                    link = result.find("a")
                    if not link:
                        continue
                        
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    
                    # Skip if it's the original brand
                    if brand_name.lower() in title.lower():
                        continue
                    
                    # Look for competitor indicators in title
                    competitor_indicators = [
                        "vs", "versus", "alternative", "competitor", "similar", "like", "compare"
                    ]
                    
                    if any(indicator in title.lower() for indicator in competitor_indicators):
                        # Extract potential competitor names
                        potential_competitors = re.split(r'\s+(?:vs|versus|alternative|competitor|similar|like|compare)\s+', title.lower())
                        for comp in potential_competitors:
                            if comp and comp != brand_name.lower():
                                competitors.append(comp.strip())
                
                if len(competitors) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error searching for competitors: {str(e)}")
                continue
        
        # Remove duplicates and limit results
        unique_competitors = list(set(competitors))
        return unique_competitors[:limit]
    
    def _find_shopify_store_url(self, competitor_name: str) -> str:
        """Find the Shopify store URL for a competitor"""
        try:
            # Search for the competitor's website
            search_url = f"https://html.duckduckgo.com/html/?q={competitor_name} official website"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract search results
            results = soup.select(".result__url")
            for result in results:
                url = result.get_text(strip=True)
                if not url:
                    continue
                
                # Normalize URL
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                
                try:
                    # Check if it's a Shopify store
                    check_response = requests.head(url, timeout=5)
                    server = check_response.headers.get("server", "").lower()
                    
                    if "shopify" in server:
                        return url
                        
                    # Try to access products.json
                    parsed_url = urlparse(url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    products_url = f"{base_url}/products.json"
                    
                    products_response = requests.get(products_url, timeout=5)
                    if products_response.status_code == 200 and "products" in products_response.json():
                        return base_url
                        
                except:
                    continue
            
            return ""
            
        except Exception as e:
            logger.error(f"Error finding Shopify store for {competitor_name}: {str(e)}")
            return ""
    
    def get_competitors_insights(self, limit: int = 3) -> List[ShopifyInsights]:
        """Get insights for competitors"""
        brand_name = self._get_domain_name(self.website_url)
        competitor_names = self._search_competitors(brand_name, limit=limit)
        
        competitor_insights = []
        
        for name in competitor_names:
            try:
                store_url = self._find_shopify_store_url(name)
                if not store_url:
                    continue
                    
                service = ShopifyService(store_url)
                insights = service.get_all_insights()
                competitor_insights.append(insights)
                
                if len(competitor_insights) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error getting insights for competitor {name}: {str(e)}")
                continue
        
        return competitor_insights