from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from app.database.models import (
    Store, Product, HeroProduct, FAQ, SocialHandle, ContactInfo, ImportantLink
)
from app.models.insights import ShopifyInsights


class InsightsRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_store_by_url(self, url: str) -> Optional[Store]:
        """Get store by URL"""
        return self.db.query(Store).filter(Store.url == url).first()
    
    def create_store(self, insights: ShopifyInsights) -> Store:
        """Create a new store with insights"""
        # Create store
        store = Store(
            url=insights.store_url,
            name=insights.store_name,
            about=insights.about_brand,
            privacy_policy=insights.privacy_policy,
            return_refund_policy=insights.return_refund_policy
        )
        self.db.add(store)
        self.db.flush()  # Flush to get the store ID
        
        # Create products
        for product_data in insights.products:
            product = Product(
                store_id=store.id,
                product_id=product_data.id,
                title=product_data.title,
                handle=product_data.handle,
                description=product_data.description,
                price=product_data.price,
                compare_at_price=product_data.compare_at_price,
                available=product_data.available,
                tags=product_data.tags,
                images=product_data.images,
                variants=product_data.variants,
                url=product_data.url
            )
            self.db.add(product)
        
        # Create hero products
        for hero_product in insights.hero_products:
            hero = HeroProduct(
                store_id=store.id,
                product_id=hero_product.id
            )
            self.db.add(hero)
        
        # Create FAQs
        for faq_data in insights.faqs:
            faq = FAQ(
                store_id=store.id,
                question=faq_data.question,
                answer=faq_data.answer
            )
            self.db.add(faq)
        
        # Create social handles
        for social_data in insights.social_handles:
            social = SocialHandle(
                store_id=store.id,
                platform=social_data.platform,
                url=social_data.url
            )
            self.db.add(social)
        
        # Create contact info
        if insights.contact_info:
            contact = ContactInfo(
                store_id=store.id,
                emails=insights.contact_info.emails,
                phone_numbers=insights.contact_info.phone_numbers,
                address=insights.contact_info.address
            )
            self.db.add(contact)
        
        # Create important links
        for link_data in insights.important_links:
            link = ImportantLink(
                store_id=store.id,
                name=link_data.name,
                url=link_data.url
            )
            self.db.add(link)
        
        # Commit changes
        self.db.commit()
        self.db.refresh(store)
        
        return store
    
    def update_store(self, store: Store, insights: ShopifyInsights) -> Store:
        """Update an existing store with new insights"""
        # Update store
        store.name = insights.store_name
        store.about = insights.about_brand
        store.privacy_policy = insights.privacy_policy
        store.return_refund_policy = insights.return_refund_policy
        
        # Delete existing related data
        self.db.query(Product).filter(Product.store_id == store.id).delete()
        self.db.query(HeroProduct).filter(HeroProduct.store_id == store.id).delete()
        self.db.query(FAQ).filter(FAQ.store_id == store.id).delete()
        self.db.query(SocialHandle).filter(SocialHandle.store_id == store.id).delete()
        self.db.query(ContactInfo).filter(ContactInfo.store_id == store.id).delete()
        self.db.query(ImportantLink).filter(ImportantLink.store_id == store.id).delete()
        
        # Create new related data
        # Products
        for product_data in insights.products:
            product = Product(
                store_id=store.id,
                product_id=product_data.id,
                title=product_data.title,
                handle=product_data.handle,
                description=product_data.description,
                price=product_data.price,
                compare_at_price=product_data.compare_at_price,
                available=product_data.available,
                tags=product_data.tags,
                images=product_data.images,
                variants=product_data.variants,
                url=product_data.url
            )
            self.db.add(product)
        
        # Hero products
        for hero_product in insights.hero_products:
            hero = HeroProduct(
                store_id=store.id,
                product_id=hero_product.id
            )
            self.db.add(hero)
        
        # FAQs
        for faq_data in insights.faqs:
            faq = FAQ(
                store_id=store.id,
                question=faq_data.question,
                answer=faq_data.answer
            )
            self.db.add(faq)
        
        # Social handles
        for social_data in insights.social_handles:
            social = SocialHandle(
                store_id=store.id,
                platform=social_data.platform,
                url=social_data.url
            )
            self.db.add(social)
        
        # Contact info
        if insights.contact_info:
            contact = ContactInfo(
                store_id=store.id,
                emails=insights.contact_info.emails,
                phone_numbers=insights.contact_info.phone_numbers,
                address=insights.contact_info.address
            )
            self.db.add(contact)
        
        # Important links
        for link_data in insights.important_links:
            link = ImportantLink(
                store_id=store.id,
                name=link_data.name,
                url=link_data.url
            )
            self.db.add(link)
        
        # Commit changes
        self.db.commit()
        self.db.refresh(store)
        
        return store
    
    def save_insights(self, insights: ShopifyInsights) -> Store:
        """Save insights to database (create or update)"""
        store = self.get_store_by_url(insights.store_url)
        
        if store:
            return self.update_store(store, insights)
        else:
            return self.create_store(insights)