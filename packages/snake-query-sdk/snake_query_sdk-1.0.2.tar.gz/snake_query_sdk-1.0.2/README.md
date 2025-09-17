# SnakeQuery Python SDK

[![PyPI version](https://badge.fury.io/py/snake-query-sdk.svg)](https://pypi.org/project/snake-query-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for SnakeQuery - Transform natural language into structured data queries with AI.

## 🚀 Quick Start

```bash
pip install snake-query-sdk
```

```python
from snake_query_sdk import SnakeQuery, SchemaBuilder
import os

# It's recommended to set your API key as an environment variable
client = SnakeQuery(api_key=os.environ.get('SNAKE_QUERY_API_KEY'))

# Define the expected response structure
product_schema = SchemaBuilder.create() \
    .array(
        SchemaBuilder.create() \
        .object() \
        .add_string_property('name') \
        .add_number_property('price', minimum=0) \
        .required(['name', 'price']) \
        .build()
    )
    .build()

# Make the query
result = client.query(
    query='Find products under $100',
    fetch_url='https://api.store.com/products',
    response_schema=product_schema
)

print(result['response']) # Structured data
```

## ✨ Features

- 🧠 **Natural Language Processing**: Write queries in plain English
- 🏗️ **Schema-Driven**: Type-safe, validated responses
- 🌐 **Multiple Data Sources**: Query lists, dictionaries, or REST APIs
- ⚡ **High Performance**: Optimized for production use
- 🔒 **Secure**: Built-in authentication and error handling

## 📖 Documentation

- [📚 Full Documentation](https://docs.snakequery.com/python-sdk)
- [🚀 Getting Started](https://app.snakequery.com/)
- [🏗️ Schema Building Guide](https://docs.snakequery.com/essentials/schema-building)
- [💻 Examples](./examples/)

## 🎯 Core Concepts

### Natural Language Queries

Transform complex data operations into simple English:

```python
# Instead of complex Python:
# result = sorted(
#     [
#         {'name': item['title'], 'price': item['price'], 'rating': item['rating']}
#         for item in data
#         if item['price'] < 500 and item['category'] == 'electronics'
#     ],
#     key=lambda x: x['rating'],
#     reverse=True
# )[:5]

# Use natural language:
result = client.query(
    query='Find top 5 electronics under $500, show name, price and rating, sort by rating',
    data=products
)
```

### Structured Responses

Control output format with schemas:

```python
schema = SchemaBuilder.create() \
    .array(
        SchemaBuilder.create() \
        .object() \
        .add_string_property('productName') \
        .add_number_property('price', minimum=0) \
        .add_number_property('rating', minimum=0, maximum=5) \
        .required(['productName', 'price']) \
        .build()
    )
    .build()

result = client.query(
    query='Show top rated products',
    data=products,
    response_schema=schema
)

# Guaranteed structure:
# [{'productName': 'iPhone', 'price': 999, 'rating': 4.8}]
```

## 💻 Usage Examples

### Query Direct Data

```python
products = [
  { 'name': 'iPhone', 'price': 999, 'category': 'electronics' },
  { 'name': 'Shoes', 'price': 129, 'category': 'fashion' }
]

result = client.query(
    query='Find products by category and calculate average price per category',
    data=products
)
```

### Query External APIs

```python
result = client.query(
    query='Show me the 5 most expensive products with their details',
    fetch_url='https://api.escuelajs.co/api/v1/products',
    response_schema=expensive_products_schema
)
```

## 🔧 API Reference

### SnakeQuery Constructor

```python
client = SnakeQuery(api_key='your-api-key')
```

### query()

Main method for all query operations:

```python
def query(self, query: str, data: any = None, fetch_url: str = None, response_schema: dict = None, debug: bool = False) -> dict:
    # ...
```

### SchemaBuilder

Build type-safe response schemas:

```python
schema = SchemaBuilder.create() \
  .array(item_schema)              # Array of items
  .object()                       # Object structure
  .add_string_property('name')    # Add string field
  .add_number_property('price')   # Add number field
  .required(['name'])             # Mark fields as required
  .build()                        # Generate schema dictionary
```

## ⚠️ Error Handling

```python
from snake_query_sdk.exceptions import SnakeQueryError

try:
    result = client.query(**options)
except SnakeQueryError as e:
    if e.status == 401:
        print('Invalid API key')
    elif e.status == 402:
        print('Insufficient credits')
    elif e.status == 504:
        print('Query timeout - try simplifying')
    else:
        print(f'Error: {e.message}')
```

## 🌟 Advanced Features

### Environment Variables

```bash
export SNAKE_QUERY_API_KEY="your-api-key-here"
```

```python
import os
client = SnakeQuery(api_key=os.environ.get('SNAKE_QUERY_API_KEY'))
```

### Debug Mode

```python
result = client.query(
    query='Analyze data',
    data=dataset,
    debug=True  # Enables detailed logging
)
```

## 📊 Response Format

All successful queries return a dictionary:

```python
{
  'usageCount': {
    'inputTokens': 150,
    'outputTokens': 75,
    'totalTokens': 225
  },
  'response': [
    # Your structured data here
  ]
}
```

## 🚀 Examples

Check out the [examples directory](./examples/) for complete working examples.

Run an example:
```bash
export SNAKE_QUERY_API_KEY="your-key"
python examples/data_query_demo.py
```

## 📝 Requirements

- Python 3.7+
- `requests` library
- Valid SnakeQuery API key

## 🤝 Contributing

We welcome contributions! Please see our `CONTRIBUTING.md` for details.

## 📄 License

MIT License - see `LICENSE` file for details.
