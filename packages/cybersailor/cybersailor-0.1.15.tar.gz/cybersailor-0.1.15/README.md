# Cybersailor Python SDK

Cybersailor is a Python SDK for real-time data processing with Carthooks integration.

## Version 0.1.11 - Single Threaded SQS Mode

### Major Changes
- **Single Threaded Architecture**: Removed multi-threading support for simplified execution
- **SQS-Only Mode**: Only supports SQS-based subscriptions (polling mode removed)
- **Simplified API**: Cleaner, more predictable behavior with single-threaded execution

### Features
- Real-time data processing via Amazon SQS
- Automatic monitoring task renewal
- Thread-safe DNS caching
- HTTP/2 support with connection pooling
- IPv6 support (configurable)

### Installation
```bash
pip install cybersailor
```

### Usage
```python
from cybersailor import Sailor

def handler(ctx, message):
    print(f"Received: {message.item_id}")
    return True

sailor = Sailor(token="your_token")
sailor.subscribe(
    handler=handler,
    app_id=123456,
    collection_id=789012,
    sqs_queue_url="https://sqs.region.amazonaws.com/account/queue-name"
)
sailor.run()
```

### Breaking Changes from 0.1.x
- `sqs_queue_url` parameter is now required for `subscribe()`
- Polling mode has been removed
- No longer uses background threads for SQS listening and renewal