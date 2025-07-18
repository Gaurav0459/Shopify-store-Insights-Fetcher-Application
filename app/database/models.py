from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    about = Column(Text, nullable=True)
    privacy_policy = Column(Text, nullable=True)
    return_refund_policy = Column(Text, nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="store")
    hero_products = relationship("HeroProduct", back_populates="store")
    faqs = relationship("FAQ", back_populates="store")
    social_handles = relationship("SocialHandle", back_populates="store")
    contact_info = relationship("ContactInfo", back_populates="store", uselist=False)
    important_links = relationship("ImportantLink", back_populates="store")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    product_id = Column(String(255))
    title = Column(String(255))
    handle = Column(String(255))
    description = Column(Text, nullable=True)
    price = Column(String(50), nullable=True)
    compare_at_price = Column(String(50), nullable=True)
    available = Column(Boolean, default=True)
    tags = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    variants = Column(JSON, nullable=True)
    url = Column(String(255), nullable=True)
    
    # Relationships
    store = relationship("Store", back_populates="products")


class HeroProduct(Base):
    __tablename__ = "hero_products"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    product_id = Column(String(255))
    
    # Relationships
    store = relationship("Store", back_populates="hero_products")


class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    question = Column(Text)
    answer = Column(Text)
    
    # Relationships
    store = relationship("Store", back_populates="faqs")


class SocialHandle(Base):
    __tablename__ = "social_handles"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    platform = Column(String(50))
    url = Column(String(255))
    
    # Relationships
    store = relationship("Store", back_populates="social_handles")


class ContactInfo(Base):
    __tablename__ = "contact_info"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), unique=True)
    emails = Column(JSON, nullable=True)
    phone_numbers = Column(JSON, nullable=True)
    address = Column(Text, nullable=True)
    
    # Relationships
    store = relationship("Store", back_populates="contact_info")


class ImportantLink(Base):
    __tablename__ = "important_links"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    name = Column(String(255))
    url = Column(String(255))
    
    # Relationships
    store = relationship("Store", back_populates="important_links")