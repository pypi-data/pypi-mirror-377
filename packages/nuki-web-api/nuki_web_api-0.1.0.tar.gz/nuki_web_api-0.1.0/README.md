# nukiwebapi

A Python wrapper for the [Nuki Web API](https://developer.nuki.io/).

## Installation

```bash
pip install nukiwebapi
```

## Usage
```Python
from nukiwebapi import NukiWebAPI

client = NukiWebAPI("YOUR_ACCESS_TOKEN")

for lock_id, lock in client.smartlocks():
    print(lock_id, lock.name)
    lock.unlock()
```