#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Chromium process launcher module."""

import asyncio
import json
import logging
import time
from http.client import HTTPException
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from cdpy.browser import Browser
from cdpy.connection import Connection
from cdpy.errors import BrowserError
from cdpy.util import (
    merge_dict,
)

logger = logging.getLogger(__name__)


def get_ws_endpoint(url) -> str:
    url = url + "/json/version"
    timeout = time.time() + 30
    while True:
        if time.time() > timeout:
            raise BrowserError("Browser closed unexpectedly:\n")
        try:
            with urlopen(url) as f:
                data = json.loads(f.read().decode())
            break
        except (URLError, HTTPException):
            pass
        time.sleep(0.1)

    return data["webSocketDebuggerUrl"]


async def connect(options: dict = None, **kwargs: Any) -> Browser:
    """Connect to the existing chrome.
    ``browserWSEndpoint`` or ``browserURL`` option is necessary to connect to
    the chrome. The format of ``browserWSEndpoint`` is
    ``ws://${host}:${port}/devtools/browser/<id>`` and format of ``browserURL``
    is ``http://127.0.0.1:9222```.
    The value of ``browserWSEndpoint`` can get by :attr:`~cdpy.browser.Browser.wsEndpoint`.
    Available options are:
    * ``browserWSEndpoint`` (str): A browser websocket endpoint to connect to.
    * ``browserURL`` (str): A browser URL to connect to.
    * ``ignoreHTTPSErrors`` (bool): Whether to ignore HTTPS errors. Defaults to
      ``False``.
    * ``defaultViewport`` (dict): Set a consistent viewport for each page.
      Defaults to an 800x600 viewport. ``None`` disables default viewport.
      * ``width`` (int): page width in pixels.
      * ``height`` (int): page height in pixels.
      * ``deviceScaleFactor`` (int|float): Specify device scale factor (can be
        thought as dpr). Defaults to ``1``.
      * ``isMobile`` (bool): Whether the ``meta viewport`` tag is taken into
        account. Defaults to ``False``.
      * ``hasTouch`` (bool): Specify if viewport supports touch events.
        Defaults to ``False``.
      * ``isLandscape`` (bool): Specify if viewport is in landscape mode.
        Defaults to ``False``.
    * ``slowMo`` (int|float): Slow down cdpy's by the specified amount of
      milliseconds.
    * ``logLevel`` (int|str): Log level to print logs. Defaults to same as the
      root logger.
    * ``loop`` (asyncio.AbstractEventLoop): Event loop (**experimental**).
    """
    options = merge_dict(options, kwargs)
    logLevel = options.get("logLevel")
    if logLevel:
        logging.getLogger("cdpy").setLevel(logLevel)

    browserWSEndpoint = options.get("browserWSEndpoint")
    if not browserWSEndpoint:
        browserURL = options.get("browserURL")
        if not browserURL:
            raise BrowserError("Need `browserWSEndpoint` or `browserURL` option.")
        browserWSEndpoint = get_ws_endpoint(browserURL)
    connectionDelay = options.get("slowMo", 0)
    connection = Connection(
        browserWSEndpoint,
        options.get("loop", asyncio.get_event_loop()),
        connectionDelay,
    )
    browserContextIds = (await connection.send("Target.getBrowserContexts")).get(
        "browserContextIds", []
    )
    ignoreHTTPSErrors = bool(options.get("ignoreHTTPSErrors", False))
    defaultViewport = options.get("defaultViewport", {"width": 800, "height": 600})
    return await Browser.create(
        connection,
        browserContextIds,
        ignoreHTTPSErrors,
        defaultViewport,
        None,
        lambda: connection.send("Browser.close"),
    )
