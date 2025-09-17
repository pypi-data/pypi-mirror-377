"""Minimal asynchronous usage example for the dpd-client package."""

import asyncio

from dpd_client import AsyncDPDClient


async def main() -> None:
    client = AsyncDPDClient()
    try:
        products = await client.drug_product(din="00326925")
        for product in products:
            print(product.brand_name, product.drug_identification_number)
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
