from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import logging
import os
import json
import asyncio
import time
from typing import Dict, Optional
import redis.asyncio as redis
from dotenv import load_dotenv
import psutil
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("zendriver").setLevel(logging.WARNING)


@dataclass
class Session(ABC):
    id: str
    url: str
    cookies: Dict[str, str]
    headers: Dict[str, str]
    proxy: Optional[str]
    created_at: int = int(time.time() * 1000)



class Solver(ABC):
    name: str


    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.target_url = os.getenv("TARGET_URL")
        self.session_pool_size = int(os.getenv("SOLVER_SESSION_POOL_SIZE", "1"))

        self.proxy_user = os.getenv("PROXY_USER")
        self.proxy_pass = os.getenv("PROXY_PASS")
        self.proxy_server = os.getenv("PROXY_SERVER")
        if self.proxy_server and self.proxy_server.startswith("http://"):
            self.proxy_server = self.proxy_server[7:]

        self.redis_list_name = os.getenv("REDIS_LIST_NAME")
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = os.getenv("REDIS_PORT", 6379)
        self.redis_pass = os.getenv("REDIS_PASS")
        self.db = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_pass)


    @abstractmethod
    async def solve(self) -> Session:
        ...


    async def start(self) -> None:
        self.logger.info(f"Starting {self.name} solver")
        while True:
            try:
                if await self.db.llen(self.redis_list_name) < self.session_pool_size:
                    session = await self.solve()
                    if not session:
                        self.logger.error("No session found")
                        continue
                    await self.db.lpush(self.redis_list_name, json.dumps(asdict(session)))
                    self.logger.info(f"Solved: {session.url} with {session.proxy if session.proxy else 'no proxy'}")
                else:
                    await asyncio.sleep(2)
            except Exception as e:
                self.logger.exception("Error solving")
            finally:
                self.cleanup_processes()


    @staticmethod
    def is_in_docker():
        return os.path.exists('/.dockerenv')


    def cleanup_processes(self):
        if not self.is_in_docker():
            return
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] and "chrome" in proc.info["name"].lower():
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    self.logger.warning(f"Process {proc.info['name']} (PID: {proc.pid}) already terminated.")

