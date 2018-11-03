"""
This module should contain functionality to take in a list of objects with
an attribute `url` and return those objects with a `soup` attribute
added.

Ideally, this module would support a queue-like functionality, generating
a loop that is constantly accepting new work, performing it asynchronously,
and returning values.
"""
import asyncio

import aiohttp
