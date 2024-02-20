* Default run

`docker-compose down --remove-orphans && docker-compose up --build`
* 10 requests / asyncio event loop / hit proxy first

`docker-compose down --remove-orphans && CONCURRENCY=10 SERVER=proxy EVENTLOOP=asyncio docker-compose up --build`
* 10 requests / uvloop event loop / hit proxy first

`docker-compose down --remove-orphans && CONCURRENCY=10 SERVER=proxy EVENTLOOP=uvloop docker-compose up`
* 500 requests / asyncio event loop / hit proxied only / requests are sequential

`docker-compose down --remove-orphans && CONCURRENCY=500 SERVER=proxied EVENTLOOP=asyncio MODE=sequential docker-compose up`
* 500 requests / uvloop event loop / hit proxied only / requests are sequential

`docker-compose down --remove-orphans && CONCURRENCY=500 SERVER=proxied EVENTLOOP=uvloop MODE=sequential docker-compose up`
