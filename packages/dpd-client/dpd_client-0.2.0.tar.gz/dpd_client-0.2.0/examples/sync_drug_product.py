"""Minimal synchronous usage example for the dpd-client package."""

from dpd_client import DPDClient


def main() -> None:
    client = DPDClient(cache_ttl=30)
    try:
        products = client.drug_product(din="00326925")
        for product in products:
            print(product.brand_name, product.drug_identification_number)
    finally:
        client.close()


if __name__ == "__main__":
    main()
