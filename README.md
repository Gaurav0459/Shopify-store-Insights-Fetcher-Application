# ShopInsight - Shopify Store Analyzer

![ShopInsight Logo](https://img.shields.io/badge/ShopInsight-Shopify%20Analyzer-5d4fff?style=for-the-badge)

A powerful FastAPI application that extracts valuable insights from Shopify stores without requiring API access. Perfect for market research, competitor analysis, and understanding e-commerce trends.

## 🚀 Features

### Core Features
- 📊 **Complete Product Catalog** - Extract all products with details
- 🌟 **Hero Product Detection** - Identify featured products on homepage
- 📜 **Policy Extraction** - Privacy and return/refund policies
- ❓ **FAQ Collection** - Gather brand FAQs and answers
- 📱 **Social Media Discovery** - Find all social media handles
- 📞 **Contact Information** - Extract emails, phone numbers, and addresses
- ℹ️ **Brand Information** - Get the "About Us" content
- 🔗 **Important Links** - Identify key navigation links

### Bonus Features
- 🔍 **Competitor Analysis** - Automatically find and analyze competitors
- 💾 **Database Storage** - Persist all insights in MySQL/SQLite

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

### Challenges I Overcame

- **Rate Limiting**: Some stores would block requests if made too quickly
- **Different Themes**: Each store has unique HTML structure and class names
- **Hidden Content**: Some content is loaded dynamically with JavaScript
- **Pagination**: Handling stores with large product catalogs

## 📝 Future Improvements

- Add caching mechanism to avoid repeated requests to the same store
- Implement rate limiting to avoid being blocked by Shopify
- Add support for more languages beyond English
- Create a more detailed UI to visualize the extracted data
- Add historical data tracking to monitor changes over time

## 📄 License

MIT License