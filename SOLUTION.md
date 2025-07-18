# Shopify Store Insights Fetcher - Solution

## Overview

This application fetches insights from Shopify stores without using the official Shopify API. It extracts various data points from a Shopify store, including product catalog, hero products, policies, FAQs, social handles, contact information, and more.

## Architecture

The application follows a clean architecture with separation of concerns:

- **Models**: Pydantic models for data validation and serialization
- **Services**: Business logic for fetching and processing data
- **Routers**: API endpoints
- **Database**: SQLAlchemy models and repository pattern for persistence

## Features Implemented

### Mandatory Requirements

1. **Product Catalog**: Fetches all products from the store using the `/products.json` endpoint
2. **Hero Products**: Identifies products featured on the homepage
3. **Privacy Policy**: Extracts privacy policy content
4. **Return/Refund Policies**: Extracts return and refund policy content
5. **Brand FAQs**: Collects frequently asked questions and answers
6. **Social Handles**: Identifies social media profiles
7. **Contact Details**: Extracts email addresses, phone numbers, and physical address
8. **Brand Context**: Extracts information about the brand
9. **Important Links**: Identifies important links like order tracking, contact us, etc.

### Bonus Features

1. **Competitor Analysis**: Identifies competitors and fetches insights from their stores
2. **Database Persistence**: Stores all insights in a SQL database (MySQL or SQLite)

## Technical Implementation

### API Endpoints

- `POST /api/v1/insights`: Get insights from a Shopify store
- `POST /api/v1/insights/competitors`: Get insights from competitors

### Database Schema

- `stores`: Store information
- `products`: Product catalog
- `hero_products`: Products featured on homepage
- `faqs`: Frequently asked questions
- `social_handles`: Social media profiles
- `contact_info`: Contact information
- `important_links`: Important links

### Web Scraping Techniques

- Uses BeautifulSoup for HTML parsing
- Leverages Shopify's `/products.json` endpoint for product data
- Implements various patterns to extract FAQs, policies, and other content
- Handles different store layouts and structures

### Best Practices Implemented

1. **OOP Principles**: Classes with single responsibilities
2. **SOLID Design**: Separation of concerns, dependency injection
3. **Clean Code**: Meaningful variable names, comments, error handling
4. **RESTful API Design**: Proper HTTP methods, status codes, and response formats
5. **Pydantic Models**: For data validation and serialization
6. **Error Handling**: Proper error responses with status codes
7. **Code Structure**: Organized into modules and packages
8. **Edge Case Handling**: Handling different store layouts and missing data

## How to Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```

3. Access the web interface at http://localhost:8000/

4. For API documentation, visit http://localhost:8000/docs

## Testing

Unit tests are provided for the ShopifyService class. Run tests with:
```
python -m unittest discover tests
```

## Database Configuration

By default, the application uses SQLite. To use MySQL:

1. Edit the `.env` file and uncomment the `DATABASE_URL` line
2. Update the connection string with your MySQL credentials
3. Restart the application