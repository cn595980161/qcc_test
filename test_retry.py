import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


def retry_if_result_none(result):
    print(result)
    return result is None


@retry(retry=retry_if_exception_type(Exception), stop=stop_after_attempt(3), wait=wait_fixed(5))
async def get_result():
    print(1111)
    raise Exception


asyncio.get_event_loop().run_until_complete(get_result())
