# ShopInsight - Shopify store Insights-Fetcher Application


A powerful FastAPI application that extracts valuable insights from Shopify stores without requiring API access. Perfect for market research, competitor analysis, and understanding e-commerce trends.


## 🛠️ Installation

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/shopify-store-insights.git
   cd shopify-store-insights
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure database (optional)
   - Edit `.env` file to use MySQL instead of SQLite
   - Uncomment and modify the `DATABASE_URL` line

## 🖥️ Usage

1. Start the server
   ```bash
   python run.py
   ```

2. Open your browser and go to http://localhost:8000/

3. Enter a Shopify store URL (e.g., "memy.co.in" or "hairoriginals.com")

4. Click "Analyze Store" and wait for results

## 🔌 API Endpoints

- `POST /api/v1/insights` - Get insights from a Shopify store
  ```json
  {
    "website_url": "https://example-store.myshopify.com"
  }
  ```

- `POST /api/v1/insights/competitors` - Get competitor insights
  ```json
  {
    "website_url": "https://example-store.myshopify.com"
  }
  ```

## 📊 Response Format

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

## 💡 My Approach

When I started this project, I first analyzed several Shopify stores to understand their structure. I noticed that while they all use the Shopify platform, each store has its own unique theme and layout. This meant I couldn't rely on a single approach to extract data.

I decided to implement a multi-strategy approach for each data point:

1. **Primary Strategy**: Try the most common pattern first
2. **Fallback Strategies**: If the primary strategy fails, try alternative approaches
3. **Graceful Degradation**: Return partial data rather than failing completely

For example, with FAQs, I first look for definition lists (dt/dd pairs), then header/paragraph pairs, and finally accordion components. This ensures we get data even from stores with unusual layouts.

The most interesting discovery was that all Shopify stores expose their product catalog via the `/products.json` endpoint, which made that part much easier than initially expected.
