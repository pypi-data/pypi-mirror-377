# newsdata-client

Python client for [Newsdata API](https://newsdata.io/documentation)

# Installation

Install using pip:

```bash
pip install newsdata-client
```

# Usage

Import the `client` class into your project, and initialize using the `api_key`.

```python
from newsdata_client import NewsDataClient

news_client = NewsDataClient(api_key="pub_XXXXXXXXXXX")
```
# Endpoints

There are four endpoint functions you can use.
You can add keyword arguments for parameters you like.
You can read [this](https://newsdata.io/documentation#latest-news) for more detail
on the parameters available for all the endpoints

```python
# Latest news endpoint
response = news_client.latest() 

# Crypto related news endpoint
response = news_client.crypto()

# News archive endpoint, for this endpoint you will have to
# give atleast one parameter, otherwise it will raise NewsDataException
response = news_client.archive(category=["technology"])

# News sources endpoint
response = news_client.sources()
```

# License

This project in under [MIT License](https://github.com/Vikuuu/newsdata-client/blob/main/LICENSE)
