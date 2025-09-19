# Planning Center API

This Python library provides a seamless wrapper around the Planning Center API with support currently for the Calendar Endpoint.

## Features

- Pull Calendar and Tag information

## Installation

pip3 install pco_calendar

## Quick Start

```python
from pco_calendar.api import api

client = api(
    user="user_id",
    password="api_token",
)
```
