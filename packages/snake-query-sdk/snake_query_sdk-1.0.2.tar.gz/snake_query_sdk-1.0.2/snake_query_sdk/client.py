import requests
import json
from .exceptions import SnakeQueryError

class SnakeQuery:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = 'https://app.snakequery.com/api/query'
        self.timeout = 600  # 10 minutes

    def query(self, query: str, data: any = None, fetch_url: str = None, response_schema: dict = None, debug: bool = False) -> dict:
        if not query:
            raise ValueError("Query is required")

        if data is None and fetch_url is None:
            raise ValueError("Either data or fetch_url must be provided")

        if data is not None and fetch_url is not None:
            raise ValueError("Cannot provide both data and fetch_url, choose one")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        request_body = {
            'query': query
        }
        if data is not None:
            request_body['data'] = data
        if fetch_url is not None:
            request_body['fetchUrl'] = fetch_url
        if response_schema is not None:
            request_body['responseSchema'] = response_schema
        if debug is not None:
            request_body['debug'] = debug

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(request_body),
                timeout=self.timeout
            )

            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {
                    'message': f'Server returned non-JSON response: {response.reason}',
                    'statusCode': response.status_code,
                    'body': response.text[:200] + ('...' if len(response.text) > 200 else '')
                }

            if not response.ok:
                raise SnakeQueryError(
                    message=result.get('message', f'HTTP {response.status_code}: {response.reason}'),
                    status=response.status_code,
                    response=result
                )
            
            if result.get('code') != 200:
                raise SnakeQueryError(
                    message=str(result),
                    status=result.get('code')
                )

            return result.get('data')

        except requests.exceptions.Timeout:
            raise SnakeQueryError('Request timeout: Snake Query API took too long to respond (10 minute limit)', status=504)
        except requests.exceptions.RequestException as e:
            raise SnakeQueryError(f'Network error: Unable to connect to Snake Query API. {e}')
        
    def query_with_data(self, query: str, data: any, **kwargs) -> dict:
        return self.query(query=query, data=data, **kwargs)

    def query_with_url(self, query: str, fetch_url: str, **kwargs) -> dict:
        return self.query(query=query, fetch_url=fetch_url, **kwargs)
