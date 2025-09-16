import json
import traceback
from functools import partial
from httpx import HTTPStatusError
from openai import APIStatusError

from fastapi import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi.exceptions import RequestValidationError, HTTPException

from meutils.notice.feishu import send_message_for_http as send_message

exc_set = {
    "sensitive",
    "OversizeImage",
    "Timeout while downloading url",
    "filtered by safety checks",
    "InvalidParameter",
}  # 请求头里设置 跳过的内容


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    # print(exc)
    content = {
        "error":
            {
                "message": f"{exc.detail}",
                "type": "http-error",
            }
    }
    return JSONResponse(
        content=content,
        status_code=exc.status_code
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def chatfire_api_exception_handler(request: Request, exc: Exception):
    content = {
        "error":
            {
                "message": f"{exc}",
                "type": "cf-api-error",
            },

        "code": status.HTTP_500_INTERNAL_SERVER_ERROR  # 默认 是否默认都不重试？
    }

    # 默认值
    reps = None
    if isinstance(exc, (HTTPStatusError, APIStatusError)):  # todo 透传状态码
        status_code = exc.response.status_code or 500

        content['code'] = status_code
        content['error']['message'] = f"{exc.response.text}"

        # 置换错误
        for i in {"fal.ai", "api.ppinfra"}:
            content['error']['message'] = content['error']['message'].replace(i, 'AI')

        reps = JSONResponse(
            content=content,
            status_code=status_code,
        )

    if any(i.lower() in str(exc).lower() for i in exc_set):  # todo 内容审核
        reps = JSONResponse(
            content=content,
            status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
        )

        # return reps

    # send_message
    content_detail = f"{traceback.format_exc()}"  # 是不是最后几行就可以了
    #
    # from meutils.pipe import logger
    # logger.debug(content_detail)

    if any(code in content_detail for code in {'451', }):
        content_detail = ""

    send_message([content, content_detail], title=__name__)

    # from meutils.pipe import logger
    #
    # try:
    #
    #     logger.debug(request.headers)
    #     logger.debug(request.url)
    #     logger.debug(request.method)
    #     logger.debug(request.query_params._dict)
    #
    #     logger.debug(request.client)
    #     logger.debug(request.cookies)
    #
    #     payload  = await request.body()
    #
    #     # send_message(payload, title=__name__)
    #
    #     logger.debug(payload)
    #     logger.debug(payload)
    #
    #
    # except Exception as e:
    #     logger.debug(e)

    return reps or JSONResponse(
        content=content,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


if __name__ == '__main__':
    pass
