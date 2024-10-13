#!/usr/bin/env python
import aiohttp

from literaflow import utils
from literaflow.core import config

if __name__ == "__main__":
    web_app = utils.create_app()
    aiohttp.web.run_app(
        web_app,
        host=config.app_settings.HOST,
        port=config.app_settings.PORT,
    )
