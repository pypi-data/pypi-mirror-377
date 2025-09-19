from fastapi import FastAPI
from typing import Dict, List
from fastapi.responses import HTMLResponse
from fastapi import  Request
from pydantic import BaseModel, Field
from dataclasses import dataclass
import uvicorn
import time
import random
import json

class DiscoveryServerConfig(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8880)
    debug: bool = Field(default=False)
    down_timeout: int = Field(default=60)
    clear_timeout: int = Field(default=1800)

    @classmethod
    def load(cls, path: str) -> "DiscoveryServerConfig":
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

@dataclass
class ServiceInfo:
    name: str
    active_instances: list[str]
    status: str = "active"


class DiscoveryServer:
    def __init__(self, config: DiscoveryServerConfig):
        self.config = config
        self.registry: Dict[str, Dict[str, float]] = {}


    def start(self):
        app = FastAPI()

        # A simple service registry to register and list services
        # Service name -> address mapping (IP address or hostname and last health-check timestamp)


        @app.post("/register")
        async def register(service_name: str, address: str):
            if not service_name in self.registry:
                self.registry[service_name] = {}
            self.registry[service_name][address] = time.time()


        @app.post("/deregister")
        async def deregister(service_name: str, address: str):
            if service_name in self.registry and address in self.registry[service_name]:
                del self.registry[service_name][address]
                if self.registry[service_name] == {}:
                    del self.registry[service_name]


        @app.get("/services")
        async def list_services() -> List[ServiceInfo]:
            result = [ServiceInfo(name=name, active_instances=_get_active_services(name)) for name in list(self.registry.keys())]
            for service in result:
                service.status = "active" if service.active_instances else "inactive"
            return result


        @app.get("/address")
        async def get_service(service_name: str) -> str:
            instances = _get_active_services(service_name)
            if not instances or len(instances) == 0:
                return "Service has no running instances", 404
            return random.choice(instances)



        @app.get("/dashboard", response_class=HTMLResponse)
        async def get_dashboard(request: Request)-> HTMLResponse:
            return _ui_template


        def _get_active_services(service_name: str) -> List[str]:
            if not service_name in self.registry:
                return []
            for address, last_seen in list(self.registry[service_name].items()):
                if time.time() - last_seen > self.config.clear_timeout:
                        del self.registry[service_name][address]
            if self.registry[service_name] == {}:
                del self.registry[service_name]
            return [address for address, last_seen in self.registry[service_name].items() if time.time() - last_seen <= self.config.down_timeout]
                


        uvicorn.run(app, host=self.config.host, port=self.config.port)


_ui_template = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Service Dashboard</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background: #f4f6f8;
        margin: 0;
        padding: 20px;
      }

      h1 {
        text-align: center;
        color: #333;
      }

      .service-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
      }

      .service-card {
        background: white;
        border: 1px solid #ddd;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        width: 300px;
        padding: 15px;
        transition: box-shadow 0.3s;
      }

      .service-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
      }

      .service-name {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
      }

      .service-status {
        margin: 10px 0;
        font-weight: bold;
        color: green;
      }

      .status-inactive {
        color: red;
      }

      .instance-list {
        margin-top: 10px;
        padding-left: 20px;
      }

      .instance-list li {
        font-size: 14px;
      }
    </style>
  </head>
  <body>
    <h1>Service Registry Dashboard</h1>
    <div id="serviceContainer" class="service-grid"></div>

    <script>
      async function loadServices() {
        try {
          const response = await fetch("/services");
          const services = await response.json();

          const container = document.getElementById("serviceContainer");
          container.innerHTML = "";

          services.forEach((service) => {
            const card = document.createElement("div");
            card.className = "service-card";

            const statusClass = service.status.toLowerCase() === "active" ? "service-status" : "service-status status-inactive";

            card.innerHTML = `
            <div class="service-name">${service.name}</div>
            <div class="${statusClass}">Status: ${service.status}</div>
            <div><strong>Instances:</strong></div>
            <ul class="instance-list">
              ${service.active_instances.map((instance) => `<li>${instance}</li>`).join("")}
            </ul>
          `;

            container.appendChild(card);
          });
        } catch (err) {
          console.error("Error loading services:", err);
          document.getElementById("serviceContainer").innerHTML = '<p style="color:red;">Failed to load services.</p>';
        }
      }

      // Load services on page load
      window.onload = loadServices;
    </script>
  </body>
</html>"""
