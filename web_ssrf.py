import socket
import ipaddress
import requests

from typing import List
from pydantic import AnyHttpUrl

from fastapi import FastAPI, HTTPException, Depends


app = FastAPI()


def get_ips_from_host(hostname: str) -> List[str]:
    try:
        ip_addresses = [ip[4][0] for ip in socket.getaddrinfo(hostname, None)]
    except Exception as e:
        print(e)
        ip_addresses = None    
    return ip_addresses


def is_ip_forbidden(ip: str) -> bool:
    ip_obj = ipaddress.ip_address(ip)
    return ip_obj.is_loopback or ip_obj.is_private


def is_forbidden_url(url: AnyHttpUrl) -> AnyHttpUrl:
    ip_addresses = get_ips_from_host(url.host)
    if ip_addresses is None or all(is_ip_forbidden(ip) for ip in ip_addresses):
        raise HTTPException(status_code=400, detail="Access to the URL is forbidden")
    return url


def process_file(url: AnyHttpUrl) -> bool:
    try:
        data = requests.get(url, timeout=10)
        # process_data(data)
        return True
    except Exception:
        return False


@app.get("/upload")
def upload(url: AnyHttpUrl = Depends(is_forbidden_url)):
    result = process_file(url)
    return {"status": result}
