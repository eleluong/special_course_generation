from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import aiohttp

# Optional dependency: requests
try:
    import requests  # type: ignore
except Exception:
    requests = None  # type: ignore

FAST_RESEARCH_URL = "https://tinh12345bn--researcher-api-create-app.modal.run/fast_research"
FAST_SEARCH_URL = "https://tinh12345bn--researcher-api-create-app.modal.run/fast_search"
DEFAULT_API_KEY = os.getenv("RESEARCHER_API_KEY")


def fast_research(query: str, api_key: Optional[str] = None, timeout: float = 60.0) -> Dict[str, Any]:
    """
    Call the fast research endpoint.

    Args:
        query: The query string to research.
        api_key: Optional API key. Defaults to env RESEARCHER_API_KEY
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        RuntimeError: On HTTP errors or invalid JSON response.
    """
    key = api_key or DEFAULT_API_KEY
    headers = {
        "accept": "application/json",
        "X-API-Key": key,
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    if requests is not None:
        try:
            resp = requests.post(FAST_RESEARCH_URL, headers=headers, json=payload, timeout=timeout)
        except Exception as exc:
            raise RuntimeError(f"fast_research request failed: {exc}") from exc
        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"fast_research HTTP {resp.status_code}: {resp.text}")
        try:
            return resp.json()
        except ValueError as exc:
            raise RuntimeError("fast_research returned non-JSON response") from exc
    else:
        # Fallback to stdlib to avoid adding dependencies
        import urllib.request
        import urllib.error

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(FAST_RESEARCH_URL, data=data, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                status = r.getcode()
                body = r.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"fast_research HTTP {e.code}: {body}") from e
        except Exception as exc:
            raise RuntimeError(f"fast_research request failed: {exc}") from exc

        if not (200 <= status < 300):
            raise RuntimeError(f"fast_research HTTP {status}: {body.decode('utf-8', errors='replace')}")
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError("fast_research returned non-JSON response") from exc


def fast_search(
    query: str, api_key: Optional[str] = None, timeout: float = 60.0
) -> Dict[str, Any]:
    """
    Call the fast search endpoint.

    Args:
        query: The query string to search.
        api_key: Optional API key. Defaults to env RESEARCHER_API_KEY
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        RuntimeError: On HTTP errors or invalid JSON response.
    """
    key = api_key or DEFAULT_API_KEY
    headers = {
        "accept": "application/json",
        "X-API-Key": key,
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    if requests is not None:
        try:
            resp = requests.post(FAST_SEARCH_URL, headers=headers, json=payload, timeout=timeout)
        except Exception as exc:
            raise RuntimeError(f"fast_search request failed: {exc}") from exc
        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"fast_search HTTP {resp.status_code}: {resp.text}")
        try:
            return resp.json()
        except ValueError as exc:
            raise RuntimeError("fast_search returned non-JSON response") from exc
    else:
        # Fallback to stdlib to avoid adding dependencies
        import urllib.request
        import urllib.error

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(FAST_SEARCH_URL, data=data, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                status = r.getcode()
                body = r.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"fast_search HTTP {e.code}: {body}") from e
        except Exception as exc:
            raise RuntimeError(f"fast_search request failed: {exc}") from exc

        if not (200 <= status < 300):
            raise RuntimeError(f"fast_search HTTP {status}: {body.decode('utf-8', errors='replace')}")
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError("fast_search returned non-JSON response") from exc


async def async_fast_research(
    query: str, api_key: Optional[str] = None, timeout: float = 60.0
) -> Dict[str, Any]:
    """
    Asynchronously call the fast research endpoint.

    Args:
        query: The query string to research.
        api_key: Optional API key. Defaults to env RESEARCHER_API_KEY
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        RuntimeError: On HTTP errors or invalid JSON response.
    """
    import aiohttp  # type: ignore

    key = api_key or DEFAULT_API_KEY
    headers = {
        "accept": "application/json",
        "X-API-Key": key,
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(FAST_RESEARCH_URL, headers=headers, json=payload, timeout=timeout) as resp:
                if not (200 <= resp.status < 300):
                    text = await resp.text()
                    raise RuntimeError(f"async_fast_research HTTP {resp.status}: {text}")
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError as exc:
                    raise RuntimeError("async_fast_research returned non-JSON response") from exc
        except Exception as exc:
            raise RuntimeError(f"async_fast_research request failed: {exc}") from exc
        
async def async_fast_search(
    query: str, api_key: Optional[str] = None, timeout: float = 60.0
) -> Dict[str, Any]:
    """
    Asynchronously call the fast search endpoint.

    Args:
        query: The query string to search.
        api_key: Optional API key. Defaults to env RESEARCHER_API_KEY
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        RuntimeError: On HTTP errors or invalid JSON response.
    """
    import aiohttp  # type: ignore

    key = api_key or DEFAULT_API_KEY
    headers = {
        "accept": "application/json",
        "X-API-Key": key,
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(FAST_SEARCH_URL, headers=headers, json=payload, timeout=timeout) as resp:
                if not (200 <= resp.status < 300):
                    text = await resp.text()
                    raise RuntimeError(f"async_fast_search HTTP {resp.status}: {text}")
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError as exc:
                    raise RuntimeError("async_fast_search returned non-JSON response") from exc
        except Exception as exc:
            raise RuntimeError(f"async_fast_search request failed: {exc}") from exc