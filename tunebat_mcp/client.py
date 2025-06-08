"""Tunebat API client."""

import asyncio
import json
import unicodedata
from typing import Any
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

from .models import SearchResponse, Track, TunebatError


class TunebatClient:
    """Client for interacting with the Tunebat API.

    Note: The Tunebat API is protected by Cloudflare's bot detection system,
    which may block requests from automated clients. This client works best
    when deployed in environments that can bypass such protections.
    """

    BASE_URL = "https://api.tunebat.com/api/tracks/search"

    def __init__(self, timeout: float = 30.0):
        """Initialize the client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def search_with_browser(self, query: str) -> list[Track]:
        """Search for tracks using a browser to bypass Cloudflare protection.

        Args:
            query: Search query (artist, title, or both)

        Returns:
            List of matching tracks

        Raises:
            TunebatError: If the API request fails
        """
        encoded_query = quote_plus(query)
        url = f"{self.BASE_URL}?term={encoded_query}"

        try:
            async with async_playwright() as p:
                # Launch a headless browser with minimal arguments for better compatibility
                browser = await p.chromium.launch(headless=True)

                # Create a new page with realistic settings
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )

                # Set realistic browser headers and properties
                await page.set_extra_http_headers(
                    {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Cache-Control": "no-cache",
                        "Pragma": "no-cache",
                        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"macOS"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                    }
                )

                # Navigate to the API endpoint
                response = await page.goto(url, wait_until="networkidle", timeout=30000)

                if not response or response.status != 200:
                    await browser.close()
                    raise TunebatError(
                        f"Browser request failed with status: {response.status if response else 'No response'}",
                        status_code=response.status if response else None,
                    )

                # Get the page content and text before closing browser
                content = await page.content()
                page_text = await page.evaluate(
                    'document.body.textContent || document.body.innerText || ""'
                )
                await browser.close()

                # Extract JSON from the page content
                # The API returns JSON wrapped in a simple HTML structure
                try:
                    # Look for JSON in <pre> tags or try to parse the body text
                    if "<pre>" in content and "</pre>" in content:
                        json_text = content.split("<pre>")[1].split("</pre>")[0]
                    else:
                        # Use the page text content we already extracted
                        json_text = page_text.strip()

                    # Parse the JSON response
                    data = json.loads(json_text)

                    # Normalize text as done in the original method
                    if isinstance(data, str):
                        normalized_text = unicodedata.normalize("NFD", data)
                        cleaned_text = "".join(
                            char
                            for char in normalized_text
                            if unicodedata.category(char) != "Mn"
                        )
                        cleaned_text = cleaned_text.replace("'", "'")
                        data = json.loads(cleaned_text)

                    # Handle the response structure properly
                    # The browser returns the complete JSON structure, not wrapped in another layer
                    if isinstance(data, dict) and "data" in data:
                        # Extract the inner data object which contains the items
                        inner_data: Any = data["data"]  # type: ignore[misc]
                        if isinstance(inner_data, dict) and "items" in inner_data:
                            # Create SearchResponse with the items wrapped properly
                            search_response = SearchResponse(
                                data={"items": inner_data["items"]}
                            )
                        else:
                            # Fallback if structure is unexpected
                            search_response = SearchResponse(data={"items": []})
                    else:
                        # Fallback: wrap in expected structure
                        search_response = SearchResponse(
                            data={"items": data if isinstance(data, list) else []}
                        )

                    return search_response.items

                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    raise TunebatError(f"Failed to parse API response: {str(e)}") from e

        except Exception as e:
            if isinstance(e, TunebatError):
                raise
            raise TunebatError(f"Browser request failed: {str(e)}") from e

    async def search_with_retry(self, query: str, max_retries: int = 3) -> list[Track]:
        """Search with automatic retry on rate limiting.

        Args:
            query: Search query
            max_retries: Maximum number of retries

        Returns:
            List of matching tracks

        Raises:
            TunebatError: If all retries are exhausted
        """
        for attempt in range(max_retries + 1):
            try:
                return await self.search_with_browser(query)
            except TunebatError as e:
                if e.status_code == 429 and attempt < max_retries and e.retry_after:
                    await asyncio.sleep(e.retry_after)
                    continue
                raise
        # This should never be reached due to the raise in the except block
        return []
