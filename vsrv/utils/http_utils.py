'''
    vsys - HTTP Utilites
'''
from typing import Any
import aiohttp
from vsrv.exceptions import ApplicationException, ExceptionSeverity
from vsrv.logging.insight import SystemInsight


async def http_post_async(req_url: str, data: Any, headers: dict[str, str] | None = None):
    '''
        Async - HTTP Post
    '''
    try:
        SystemInsight.logger().info(f"HTTP POST Request: {req_url}")
        # Disable SSL Verification
        tcp_con = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=tcp_con) as session:
            async with session.post(url=req_url, json=data, headers=headers) as request:
                response = await request.json()
                SystemInsight.logger().info(f"HTTP POST Request: {req_url} Response:\n\t {response}")
                return response
    except Exception as exc:
        SystemInsight.logger().exception(f"HTTP POST Request: {req_url} Failed", exc_info=True)
        raise ApplicationException(
            severity=ExceptionSeverity.CRITICAL,
            message="Failed HTTP POST Request",
            exceptionObject=exc
        ) from exc


async def http_get_async(req_url: str, data: Any = None, headers: dict[str, str] | None = None) -> dict:
    '''
        Async - HTTP Post
    '''
    try:
        SystemInsight.logger().info(f"HTTP GET Request: {req_url}")
        # Disable SSL Verification
        tcp_con = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=tcp_con) as session:
            async with session.get(url=req_url, json=data, headers=headers) as request:
                response = await request.json()
                return response
    except Exception as exc:
        SystemInsight.logger().exception(f"HTTP GET Request: {req_url} Failed", exc_info=True)
        raise ApplicationException(
            severity=ExceptionSeverity.CRITICAL,
            message="Failed HTTP GET Request",
            exceptionObject=exc
        ) from exc
