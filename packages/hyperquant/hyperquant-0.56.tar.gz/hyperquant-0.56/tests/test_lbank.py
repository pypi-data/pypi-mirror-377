import asyncio
import zlib
from aiohttp import ClientWebSocketResponse
import pybotters

def callback(msg, ws: ClientWebSocketResponse = None):
    # print("Received message:", msg)
    decompressed = zlib.decompress(msg, 16 + zlib.MAX_WBITS)
    text = decompressed.decode("utf-8")
    print(f"Decoded text: {text}")

async def main():
    async with pybotters.Client() as client:
        # webData2
        client.ws_connect(
            "wss://ccws.rerrkvifj.com/ws/V3/",
            send_json={
                "dataType": 3,
                "depth": 200,
                "pair": "arb_usdt",
                "action": "subscribe",
                "subscribe": "depth",
                "msgType": 2,
                "limit": 10,
                "type": 10000
            },
            hdlr_bytes=callback
        )

        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())