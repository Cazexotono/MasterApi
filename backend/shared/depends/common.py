from ipaddress import IPv4Address
from typing import Optional
from user_agents import parse
from user_agents.parsers import UserAgent

from fastapi import Request

__all__ = ("get_client_ip_depends","parse_useragent_depends",)

# Проверять что запрос пришёл от nginx путём сравнения request.client.host
def get_client_ip_depends(request: Request)-> Optional[IPv4Address]:
    client_ip = request.headers.get("X-Real-IP")
    if client_ip:
        return IPv4Address(client_ip)
    return None

def parse_useragent_depends(request: Request) -> Optional[UserAgent]:
    user_agent_str = request.headers.get('user-agent', None)
    if not user_agent_str:
        return None
    user_agent = parse(user_agent_str)
    return user_agent