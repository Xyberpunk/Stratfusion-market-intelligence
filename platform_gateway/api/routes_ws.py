from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


async def _heartbeat(websocket: WebSocket, stream: str) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({"stream": stream, "status": "connected"})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return


@router.websocket("/ws/signals")
async def ws_signals(websocket: WebSocket) -> None:
    await _heartbeat(websocket, "signals")


@router.websocket("/ws/anomalies")
async def ws_anomalies(websocket: WebSocket) -> None:
    await _heartbeat(websocket, "anomalies")


@router.websocket("/ws/market-status")
async def ws_market_status(websocket: WebSocket) -> None:
    await _heartbeat(websocket, "market-status")
