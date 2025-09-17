# Altan SDK

Python SDK for the Altan API, providing easy access to integration and database functionality.

## Installation

```bash
pip install altan-sdk
```

## Quick Start

### Integration

```python
import asyncio
from altan_sdk import Integration

async def main():
    # Initialize the SDK with your API key
    integration = Integration(altan_api_key="your-api-key-here")
    
    # Create connections for any platform using connection_id
    instagram = integration("your-instagram-connection-id")
    salesforce = integration("your-salesforce-connection-id")
    slack = integration("your-slack-connection-id")
    
    # Execute an action on Instagram
    result = await instagram.execute(
        action_type_id="post_photo",
        payload={
            "image_url": "https://example.com/image.jpg",
            "caption": "Hello from Altan SDK!"
        }
    )
    
    print(f"Success: {result['success']}")
    print(f"Data: {result['data']}")
    
    # Execute an action on Salesforce
    sf_result = await salesforce.execute(
        action_type_id="create_lead",
        payload={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }
    )
    
    # Close connections when done
    await integration.close_all_connections()

# Run the async function
asyncio.run(main())
```

### Using Context Managers

```python
import asyncio
from altan_sdk import Integration

async def main():
    async with Integration(altan_api_key="your-api-key-here") as integration:
        # Use any connection by its ID
        instagram = integration("your-instagram-connection-id")
        
        result = await instagram.execute(
            action_type_id="get_profile",
            payload={}
        )
        
        print(result)

asyncio.run(main())
```

## Features

- **Integration Management**: Easy access to various social media and platform integrations
- **Action Execution**: Execute actions on connected platforms
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Async Support**: Built with async/await for efficient I/O operations
- **Type Hints**: Full type hint support for better development experience

## Flexible Connection Support

The SDK supports any connection available in your Altan account (5000+ integrations):

```python
# Create connections using their connection IDs
instagram = integration("instagram_connection_id")
salesforce = integration("salesforce_connection_id") 
slack = integration("slack_connection_id")
hubspot = integration("hubspot_connection_id")
shopify = integration("shopify_connection_id")
# ... and any other connection you have configured

# Alternative syntax (equivalent)
connection = integration.connection("any_connection_id")
```

## Error Handling

```python
from altan_sdk import Integration, AltanAPIError, AltanConnectionError

async def main():
    integration = Integration(altan_api_key="your-api-key")
    connection = integration("your-connection-id")
    
    try:
        result = await connection.execute("action_id", {"key": "value"})
    except AltanAPIError as e:
        print(f"API Error: {e}")
        print(f"Status Code: {e.status_code}")
        print(f"Response Data: {e.response_data}")
    except AltanConnectionError as e:
        print(f"Connection Error: {e}")
```

## License

MIT License
