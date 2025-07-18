# Shopify Store Insights Fetcher

A FastAPI application that fetches insights from Shopify stores without using the official Shopify API.

## Features

- Fetches product catalog
- Identifies hero products (featured on homepage)
- Extracts privacy policy
- Extracts return/refund policies
- Collects brand FAQs
- Finds social media handles
- Gathers contact information
- Extracts brand information
- Identifies important links

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the server:
   ```
   uvicorn main:app --reload
   ```

2. Access the API documentation at http://localhost:8000/docs

3. Use the `/api/v1/insights` endpoint with a Shopify store URL to get insights:
   ```json
   {
     "website_url": "https://example-store.myshopify.com"
   }
   ```

## API Endpoints

- `POST /api/v1/insights`: Get insights from a Shopify store

## Response Format

The API returns a JSON object with the following structure:

```json
{
  "store_url": "https://example-store.myshopify.com",
  "store_name": "Example Store",
  "products": [...],
  "hero_products": [...],
  "privacy_policy": "...",
  "return_refund_policy": "...",
  "faqs": [...],
  "social_handles": [...],
  "contact_info": {...},
  "about_brand": "...",
  "important_links": [...]
}
```