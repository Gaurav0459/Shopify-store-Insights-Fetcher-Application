import json
import re
from typing import Dict, List, Optional, Any, Tuple
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse

from app.models.insights import Product, ShopifyInsights, SocialHandle, ContactInfo, ImportantLink, FAQ

logger = logging.getLogger(__name__)


class ShopifyService:
    def __init__(self, website_url: str):
        # Normalize URL to ensure it has a trailing slash
        self.website_url = website_url.rstrip("/") + "/"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        self.soup_cache = {}
        
    def _get_soup(self, url: str) -> BeautifulSoup:
        """Get BeautifulSoup object for a URL with caching"""
        if url in self.soup_cache:
            return self.soup_cache[url]
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            self.soup_cache[url] = soup
            return soup
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise

    def _get_json(self, url: str) -> Dict:
        """Get JSON data from a URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching JSON from {url}: {str(e)}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {url}")
            return {}

    def get_store_name(self) -> str:
        """Extract store name from the homepage"""
        soup = self._get_soup(self.website_url)
        
        # Try to get from meta tags first
        meta_title = soup.find("meta", property="og:site_name")
        if meta_title and meta_title.get("content"):
            return meta_title["content"]
        
        # Try to get from title tag
        title_tag = soup.find("title")
        if title_tag and title_tag.text:
            title = title_tag.text.strip()
            # Remove common suffixes like "| Official Site"
            title = re.sub(r'\s*[|]\s*.*$', '', title)
            return title.strip()
        
        # Fallback to domain name
        parsed_url = urlparse(self.website_url)
        domain = parsed_url.netloc
        return domain.replace("www.", "").split(".")[0].capitalize()

    def get_products(self) -> List[Product]:
        """Get all products from the store"""
        products_url = urljoin(self.website_url, "products.json")
        try:
            products_data = []
            page = 1
            while True:
                url = f"{products_url}?page={page}&limit=250"
                data = self._get_json(url)
                
                if not data.get("products"):
                    break
                    
                products_data.extend(data["products"])
                if len(data["products"]) < 250:
                    break
                    
                page += 1
                
            return [self._parse_product(product) for product in products_data]
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            return []

    def _parse_product(self, product_data: Dict) -> Product:
        """Parse product data into Product model"""
        images = []
        if product_data.get("images"):
            images = [img.get("src", "") for img in product_data["images"] if img.get("src")]
            
        variants = product_data.get("variants", [])
        price = None
        compare_at_price = None
        available = False
        
        if variants:
            price = variants[0].get("price")
            compare_at_price = variants[0].get("compare_at_price")
            available = any(variant.get("available", False) for variant in variants)
            
        return Product(
            id=str(product_data.get("id", "")),
            title=product_data.get("title", ""),
            handle=product_data.get("handle", ""),
            description=product_data.get("body_html", ""),
            price=price,
            compare_at_price=compare_at_price,
            available=available,
            tags=product_data.get("tags", []),
            images=images,
            variants=variants,
            url=urljoin(self.website_url, f"products/{product_data.get('handle')}")
        )

    def get_hero_products(self) -> List[Product]:
        """Get hero products from the homepage"""
        soup = self._get_soup(self.website_url)
        hero_products = []
        all_products = {p.handle: p for p in self.get_products()}
        
        # Look for product links on the homepage
        product_links = soup.find_all("a", href=re.compile(r"/products/"))
        
        for link in product_links:
            href = link.get("href", "")
            if not href:
                continue
                
            # Extract product handle from URL
            match = re.search(r"/products/([a-zA-Z0-9-]+)", href)
            if not match:
                continue
                
            handle = match.group(1)
            if handle in all_products:
                hero_products.append(all_products[handle])
                
        # Remove duplicates while preserving order
        seen = set()
        return [p for p in hero_products if not (p.handle in seen or seen.add(p.handle))]

    def get_privacy_policy(self) -> Optional[str]:
        """Get privacy policy content"""
        possible_paths = [
            "policies/privacy-policy",
            "pages/privacy-policy",
            "pages/privacy",
            "policies/privacy"
        ]
        
        for path in possible_paths:
            try:
                url = urljoin(self.website_url, path)
                soup = self._get_soup(url)
                
                # Look for main content
                content_selectors = [
                    "main", 
                    ".main-content", 
                    ".page-content", 
                    "#MainContent",
                    ".shopify-policy__body",
                    ".policy-content"
                ]
                
                for selector in content_selectors:
                    content = soup.select_one(selector)
                    if content:
                        return content.get_text(strip=True, separator=" ")
                        
            except Exception:
                continue
                
        return None

    def get_return_refund_policy(self) -> Optional[str]:
        """Get return/refund policy content"""
        possible_paths = [
            "policies/refund-policy",
            "pages/refund-policy",
            "pages/returns",
            "policies/returns",
            "pages/return-policy",
            "pages/shipping-returns"
        ]
        
        for path in possible_paths:
            try:
                url = urljoin(self.website_url, path)
                soup = self._get_soup(url)
                
                # Look for main content
                content_selectors = [
                    "main", 
                    ".main-content", 
                    ".page-content", 
                    "#MainContent",
                    ".shopify-policy__body",
                    ".policy-content"
                ]
                
                for selector in content_selectors:
                    content = soup.select_one(selector)
                    if content:
                        return content.get_text(strip=True, separator=" ")
                        
            except Exception:
                continue
                
        return None

    def get_faqs(self) -> List[FAQ]:
        """Get FAQs from the store"""
        possible_paths = [
            "pages/faq",
            "pages/faqs",
            "pages/frequently-asked-questions",
            "pages/help"
        ]
        
        faqs = []
        
        for path in possible_paths:
            try:
                url = urljoin(self.website_url, path)
                soup = self._get_soup(url)
                
                # Look for FAQ sections with common patterns
                # Pattern 1: dt/dd pairs
                dt_elements = soup.find_all("dt")
                for dt in dt_elements:
                    question = dt.get_text(strip=True)
                    dd = dt.find_next("dd")
                    if dd:
                        answer = dd.get_text(strip=True)
                        faqs.append(FAQ(question=question, answer=answer))
                
                # Pattern 2: h3/p or h4/p pairs
                for tag in ["h3", "h4"]:
                    headers = soup.find_all(tag)
                    for header in headers:
                        question = header.get_text(strip=True)
                        # Check if question looks like a question
                        if "?" in question or question.lower().startswith(("what", "how", "when", "where", "why", "do", "can", "is", "are")):
                            p = header.find_next("p")
                            if p:
                                answer = p.get_text(strip=True)
                                faqs.append(FAQ(question=question, answer=answer))
                
                # Pattern 3: FAQ accordions
                faq_buttons = soup.select(".accordion-button, .accordion-header, .faq-question, .faq-title")
                for button in faq_buttons:
                    question = button.get_text(strip=True)
                    # Find the corresponding content
                    content_id = button.get("aria-controls") or button.get("data-target", "").lstrip("#")
                    if content_id:
                        content = soup.find(id=content_id)
                        if content:
                            answer = content.get_text(strip=True)
                            faqs.append(FAQ(question=question, answer=answer))
                    else:
                        # Try to find the next sibling that might contain the answer
                        answer_container = button.find_next(".accordion-body, .faq-answer, .accordion-content")
                        if answer_container:
                            answer = answer_container.get_text(strip=True)
                            faqs.append(FAQ(question=question, answer=answer))
                
                if faqs:
                    return faqs
                    
            except Exception as e:
                logger.error(f"Error fetching FAQs from {path}: {str(e)}")
                continue
                
        return faqs

    def get_social_handles(self) -> List[SocialHandle]:
        """Get social media handles"""
        soup = self._get_soup(self.website_url)
        social_handles = []
        
        # Common social media platforms and their patterns
        social_patterns = {
            "instagram": r"(instagram\.com|instagr\.am)/([^/?]+)",
            "facebook": r"(facebook\.com|fb\.com)/([^/?]+)",
            "twitter": r"(twitter\.com|x\.com)/([^/?]+)",
            "youtube": r"youtube\.com/(@?[^/?]+)",
            "tiktok": r"tiktok\.com/(@?[^/?]+)",
            "pinterest": r"pinterest\.com/([^/?]+)",
            "linkedin": r"linkedin\.com/company/([^/?]+)"
        }
        
        # Look for social links in the footer and header
        for link in soup.find_all("a", href=True):
            href = link.get("href", "").lower()
            
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href):
                    social_handles.append(SocialHandle(platform=platform, url=href))
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        return [s for s in social_handles if not (s.url in seen or seen.add(s.url))]

    def get_contact_info(self) -> ContactInfo:
        """Get contact information"""
        contact_info = ContactInfo()
        
        # Try to find contact info on the homepage and contact page
        pages_to_check = [self.website_url]
        
        # Add contact page if it exists
        contact_paths = ["pages/contact", "pages/contact-us", "contact", "contact-us"]
        for path in contact_paths:
            pages_to_check.append(urljoin(self.website_url, path))
        
        for url in pages_to_check:
            try:
                soup = self._get_soup(url)
                
                # Extract emails
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                page_text = soup.get_text()
                emails = re.findall(email_pattern, page_text)
                contact_info.emails.extend([email for email in emails if email not in contact_info.emails])
                
                # Extract phone numbers (various formats)
                phone_patterns = [
                    r'\+\d{1,3}\s?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
                    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US/Canada
                    r'\d{10,12}'  # Simple digits
                ]
                
                for pattern in phone_patterns:
                    phones = re.findall(pattern, page_text)
                    contact_info.phone_numbers.extend([phone for phone in phones if phone not in contact_info.phone_numbers])
                
                # Try to find address
                address_containers = soup.select(".address, .contact-address, .store-address")
                for container in address_containers:
                    address = container.get_text(strip=True)
                    if address and len(address) > 10:  # Simple validation
                        contact_info.address = address
                        break
                
            except Exception as e:
                logger.error(f"Error extracting contact info from {url}: {str(e)}")
        
        return contact_info

    def get_about_brand(self) -> Optional[str]:
        """Get information about the brand"""
        possible_paths = [
            "pages/about",
            "pages/about-us",
            "about",
            "about-us",
            "pages/our-story",
            "pages/story"
        ]
        
        for path in possible_paths:
            try:
                url = urljoin(self.website_url, path)
                soup = self._get_soup(url)
                
                # Look for main content
                content_selectors = [
                    "main", 
                    ".main-content", 
                    ".page-content", 
                    "#MainContent",
                    ".about-content",
                    ".about-section"
                ]
                
                for selector in content_selectors:
                    content = soup.select_one(selector)
                    if content:
                        return content.get_text(strip=True, separator=" ")
                        
            except Exception:
                continue
                
        return None

    def get_important_links(self) -> List[ImportantLink]:
        """Get important links like order tracking, contact us, blogs"""
        soup = self._get_soup(self.website_url)
        important_links = []
        
        # Common important link patterns
        important_patterns = {
            "Order Tracking": r"(track|tracking|order-status)",
            "Contact Us": r"(contact|contact-us)",
            "Blog": r"(blog|articles|news)",
            "Shipping": r"(shipping|delivery)",
            "FAQ": r"(faq|help|support)",
            "Terms": r"(terms|terms-of-service|terms-conditions)",
            "Careers": r"(careers|jobs)",
            "Stores": r"(stores|locations|find-us)"
        }
        
        # Look for links in the header and footer
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            
            if not text or not href or href == "#" or href.startswith("javascript:"):
                continue
                
            # Make URL absolute
            if not href.startswith(("http://", "https://")):
                href = urljoin(self.website_url, href)
            
            # Check if it matches any important pattern
            for name, pattern in important_patterns.items():
                if re.search(pattern, href, re.I) or re.search(pattern, text, re.I):
                    important_links.append(ImportantLink(name=name, url=href))
                    break
            
            # If it has text but didn't match patterns, use the text as name
            if text and not any(link.url == href for link in important_links):
                # Only include links that seem to be within the same domain
                parsed_url = urlparse(href)
                parsed_base = urlparse(self.website_url)
                if parsed_url.netloc == parsed_base.netloc:
                    important_links.append(ImportantLink(name=text, url=href))
        
        # Remove duplicates while preserving order
        seen = set()
        return [link for link in important_links if not (link.url in seen or seen.add(link.url))]

    def get_all_insights(self) -> ShopifyInsights:
        """Get all insights from the Shopify store"""
        store_name = self.get_store_name()
        products = self.get_products()
        hero_products = self.get_hero_products()
        privacy_policy = self.get_privacy_policy()
        return_refund_policy = self.get_return_refund_policy()
        faqs = self.get_faqs()
        social_handles = self.get_social_handles()
        contact_info = self.get_contact_info()
        about_brand = self.get_about_brand()
        important_links = self.get_important_links()
        
        return ShopifyInsights(
            store_url=self.website_url,
            store_name=store_name,
            products=products,
            hero_products=hero_products,
            privacy_policy=privacy_policy,
            return_refund_policy=return_refund_policy,
            faqs=faqs,
            social_handles=social_handles,
            contact_info=contact_info,
            about_brand=about_brand,
            important_links=important_links
        )