import asyncio
import logging
import os
import cProfile


from aiohttp import ClientTimeout
from aiohttp import ClientSession, TCPConnector

from concurrent.futures import ThreadPoolExecutor

try:
    import uvloop
except:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

CT_TOTAL = float(os.environ.get("CT_TOTAL", 1))
CT_CONNECT = float(os.environ.get("CT_CONNECT", 0.5))
CT_SOCK_CONNECT = float(os.environ.get("CT_SOCK_CONNECT", 0.5))
CEIL_THRESHOLD = float(os.environ.get("CEIL_THRESHOLD", 5))
CONCURRENCY = int(os.environ.get("CONCURRENCY", 500))
MODE = str(os.environ.get("MODE", "concurrency"))
SERVER = str(os.environ.get("SERVER", "proxied"))
CPROFILE = True if os.environ.get("CPROFILE", False) else False


async def fetch(session: ClientSession, url, params, timeout):
  result: bool = True
  t0 = asyncio.get_event_loop().time()
  try:
    async with session.get(url, params=params, timeout=timeout) as response:
      await response.read()
  except Exception as e:
    result = False
  finally:
    t1 = asyncio.get_event_loop().time()
  logger.info(f"url={url}, params={params}, result={result}, took {t1-t0} second(s)")
  return result

async def main():
  try:
    timeout = ClientTimeout(
        total=CT_TOTAL, connect=CT_CONNECT, sock_connect=CT_SOCK_CONNECT, ceil_threshold=CEIL_THRESHOLD
    )
    logger.info(f"Using ClientTimeout() with ceil_threshold set to {CEIL_THRESHOLD}.")
  except:
    timeout = ClientTimeout(
        total=CT_TOTAL, connect=CT_CONNECT, sock_connect=CT_SOCK_CONNECT
    )
    logger.info("Using ClientTimeout() without ceil_threshold.")

  results = []

  connector = TCPConnector(limit=0)
  async with ClientSession(connector=connector) as session:
    for iter in range(2):
      t0 = asyncio.get_event_loop().time()
      futures = [ fetch(session, f"http://{SERVER}/ping", params={"id":str(i)}, timeout=timeout) for i in range(CONCURRENCY) ]
      if MODE == "concurrency":
        results = await asyncio.gather(*futures)
      else:
        for c in futures:
          results.append(await c)
      t1 = asyncio.get_event_loop().time()
      logger.info(f"Iteration#{iter} took {t1-t0} second(s) to execute. Success={results.count(True)}, Failures={results.count(False)}")

async def wait_for_ping():
  for _ in range(20):
    async with ClientSession() as session:
      try:
        async with session.get(f"http://{SERVER}/ping") as response:
          assert response.status == 200
          break
      except Exception:
        logger.info("Wait for upstream to be available ...")
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    logger.info(f"Starting...")

    if CPROFILE:
      logger.info("Enable cProfile")
      profiler = cProfile.Profile()
      profiler.enable()

    try:
        type_of_event_loop = os.environ.get("EVENTLOOP", "asyncio")
        if type_of_event_loop == "uvloop":
            uvloop.install()
    except:
        pass
    loop = asyncio.get_event_loop()

    # Restore Python < 3.8 max_workers in default ThreadPoolExecutor
    # ncpu = os.cpu_count()
    # max_workers = ncpu * 5 if ncpu else 32
    # max_workers = 500
    # logger.info(f"Starting asyncio with default max_workers={max_workers}")
    # loop.set_default_executor(ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="AIO-default-threadpool"))

    try:
        logger.info(
            f"Starting with {'uvloop' if isinstance(loop, uvloop.Loop) else 'asyncio'} event loop"
        )
    except:
        logger.info(f"Starting with asyncio event loop")


    asyncio.get_event_loop().run_until_complete(wait_for_ping())
    asyncio.get_event_loop().run_until_complete(main())

    if CPROFILE:
      logger.info("Dump cProfile stats")
      profiler.disable()
      profiler.dump_stats("/cprofile/profile.prof")


    logger.info(f"Bye Bye!")
