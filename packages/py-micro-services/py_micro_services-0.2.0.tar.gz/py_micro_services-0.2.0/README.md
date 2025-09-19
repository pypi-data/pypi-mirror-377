This contains very simple implementation of discovery server and gateway in python as well as a tools for creating microservices including self registration and heartbeat. 

# Example of usage

## Discovery server

```python3
from py_micro_services.discovery_server import DiscoveryServer, DiscoveryServerConfig

if __name__ == "__main__":

    config = DiscoveryServerConfig.load("config/discovery_server_config.json")

    server = DiscoveryServer(config)
    server.start()
```

after starting application the discovery server will run on address specified in the config file. You can watch all connected services on endpoint `/dashboard`.


## Gateway

```python3
from py_micro_services.gateway import Gateway, GatewayConfig

if __name__ == "__main__":

    config = GatewayConfig.load("config/gateway_config.json")

    server = Gateway(config)
    server.start()
```

after starting application the gateway will run on the address specified in the config file.

## Microservice

```python3
from fastapi import FastAPI
import uvicorn
import argparse
from routes.FirstRouter import FirstRouter
from routes.SecondRouter import SecondRouter
from fastapi import APIRouter

from py_micro_services.core import PyMicroservice

app = FastAPI()
service = PyMicroservice(config_file="config/service_config.json")

# include your routes here
FirstRouter.use_router(APIRouter(prefix="/first"))
app.include_router(FirstRouter(service).get_router(), tags=["Route 1"])

SecondRouter.use_router(APIRouter(prefix="/second"))
app.include_router(SecondRouter(service).get_router(), tags=["Second"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Hostname or IP address to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port number to bind to (default: 5000)')
    
    args = parser.parse_args()

    try:
        service.start(args.host, args.port)
        uvicorn.run("service_example:app", host=args.host, port=args.port, reload=True)
    finally:
        service.stop()
```

For microservices an implementation in FastAPI is expected. It is also expected that all endpoints are implemented in their own rotes, that closed in classes that extend `PyMicroserviceRouter` and registered in a similar way as in code above. The implementation of such a route can look like this

```python3
from py_micro_services.core import PyMicroserviceRouter, get, post
from pydantic import BaseModel


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    age: int | None = None

class FirstRouter(PyMicroserviceRouter):
    @get("/ping")
    async def ping(self) -> str:
        return "first router - pong"
    
    @get("/service_info")
    async def service_info(self) -> str:
        return "Service name: " + self._service.config.service_name

    @post("/make_user_older")
    async def make_user_older(self, user: User, years: int) -> User:
        user.age += years
        return user
```


