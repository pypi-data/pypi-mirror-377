from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import httpx
import uvicorn
import json

class GatewayConfig(BaseModel):
    discovery_server_address: str

    @classmethod
    def load(cls, path: str) -> "GatewayConfig":
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    

class Gateway:
    def __init__(self, config: GatewayConfig):
        self.config = config

    async def get_service_url(self, service_name: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.config.discovery_server_address}/address?service_name={service_name}")
            return response.json()


    def start(self):
        app = FastAPI()

        @app.api_route("/{service_name}/{path:path}", methods=["GET", "POST"])
        async def proxy(service_name: str, path: str, request: Request):
            if service_name == "favicon.ico":
                return ""

            service_url = await self.get_service_url(service_name)
            if not service_url:
                return {"error": "Service not found"}

            # Extract query parameters and reconstruct full URL
            query_string = request.url.query
            url = f"{service_url}/{path}"
            if not url.startswith("http"):
                url = f"http://{url}"
            if url.endswith("/"):
                url = url[:-1]
            if query_string:
                url = f"{url}?{query_string}"

            async with httpx.AsyncClient() as client:
                if request.method == "GET":
                    response = await client.get(url, headers=request.headers)
                else:
                    body = await request.body()
                    response = await client.request(
                        method=request.method,
                        url=url,
                        content=body,
                        headers=request.headers
                    )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )

        uvicorn.run(app, port=8080)
