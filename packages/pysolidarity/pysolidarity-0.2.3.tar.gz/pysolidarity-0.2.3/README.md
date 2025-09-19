# pysolidarity

Solidarity.Tech API Wrapper for Python.

Creates a clean(er) python interface to a few functions of the Solidarity.tech API.

This is an early version. Not fully tested. Significantly vibe-coded. **USE AT YOUR OWN RISK**

Currently only supports creating, updating, and fetching users.

## Installation

```bash
pip install pysolidarity
# with optional rate limiting support
pip install "pysolidarity[rate]"
```

## Quick start
```python
from pysolidarity import make_client_from_env

# export SOLIDARITY_API_KEY=...
client = make_client_from_env()

# Create-or-update by email or phone
user = client.users.create_or_update({"phone_number": "15555555555", "first_name":"Jimmy"})
print(user)

# Update (returns all user details)
client.users.update(user["id"], {"first_name":"Jiiiimmy"})

# Get (returns all user details)
client.users.get(user["id"])

# Enrol in automation (example below is by user_id but you can do it with email and phone_number)
client.users.enroll_in_automation(automation_id=12,user_id=1234)

```

## Rate limiting (does not work in publicly available version)
```python
import redis
from pysolidarity import make_rate_limited_client

r = redis.Redis(host="127.0.0.1", port=6379)
client = make_rate_limited_client(r, req_per_sec=4)
print(client.users.get(1234))
```

## Environment
`SOLIDARITY_API_KEY` (required)

## Development
```python
pip install -e .[dev]
```
