import asyncio

import aiofiles
import aiohttp

from literaflow.core import logger
from literaflow.utils import http_statuses


async def download_file(
    file_to_download_url: str,
    destination_path: str,
    download_timeout: int = 120,
) -> None:
    """Download a file from a URL to a destination path."""
    try:
        async with (
            asyncio.timeout(download_timeout),
            aiohttp.ClientSession() as session,
            session.get(file_to_download_url) as resp,
        ):
            if resp.status == http_statuses.HTTP_200_OK:
                async with aiofiles.open(destination_path, mode="wb") as f:
                    content = await resp.read()
                    await f.write(content)
                logger.info(
                    f"Successfully downloaded {file_to_download_url} to {destination_path}"
                )
            else:
                logger.error(
                    f"Failed to download {file_to_download_url}: Status {resp.status}"
                )
    except TimeoutError as exc:
        logger.error(
            f"Download of {file_to_download_url} timed out after {download_timeout} seconds"
        )
        raise exc
