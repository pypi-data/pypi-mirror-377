from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os, httpx

load_dotenv()  # reads .env from current working directory
# Fallback to repo root (one level up) if not found
if not os.getenv("N2YO_API_KEY"):
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

API = "https://api.n2yo.com/rest/v1/satellite"
KEY = os.getenv("N2YO_API_KEY")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root() -> dict:
    return {
        "ok": True,
        "message": "N2YO proxy running",
        "endpoints": [
            "/positions/{sat}/{lat}/{lng}/{alt}/{secs}",
        ],
    }

@app.get("/positions/{sat}/{lat}/{lng}/{alt}/{secs}")
async def positions(sat:int, lat:float, lng:float, alt:int, secs:int):
    if not KEY: raise HTTPException(500, "N2YO_API_KEY missing")
    url = f"{API}/positions/{sat}/{lat}/{lng}/{alt}/{secs}&apiKey={KEY}"
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.get(url)
        r.raise_for_status()
    return r.json()

@app.get("/tle/{sat}")
async def tle(sat: int):
    if not KEY: raise HTTPException(500, "N2YO_API_KEY missing")
    url = f"{API}/tle/{sat}&apiKey={KEY}"
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.get(url)
        r.raise_for_status()
    return r.json()

@app.get("/visualpasses/{sat}/{lat}/{lng}/{alt}/{days}/{min_el}")
async def visual_passes(sat: int, lat: float, lng: float, alt: int, days: int, min_el: int):
    if not KEY: raise HTTPException(500, "N2YO_API_KEY missing")
    url = f"{API}/visualpasses/{sat}/{lat}/{lng}/{alt}/{days}/{min_el}/&apiKey={KEY}"
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.get(url)
        r.raise_for_status()
    return r.json()
