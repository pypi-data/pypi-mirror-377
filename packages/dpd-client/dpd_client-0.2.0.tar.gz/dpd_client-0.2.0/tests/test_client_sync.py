from collections.abc import Generator

import httpx
import pytest
import respx

from dpd_client import DPDClient, DPDDecodeError, DPDHTTPError, DPDInvalidParam
from dpd_client.client import BASE_URL


SYNC_ENDPOINT_CASES = [
    (
        "drug_product",
        "drugproduct/",
        {"din": "00326925"},
        {"drug_code": 2049, "brand_name": "SINEQUAN"},
        "brand_name",
        "SINEQUAN",
        True,
    ),
    (
        "company",
        "company/",
        {"id": 101},
        [{"company_code": 101, "company_name": "ACME"}],
        "company_name",
        "ACME",
        True,
    ),
    (
        "active_ingredient",
        "activeingredient/",
        {"ingredientname": "acetaminophen"},
        [{"drug_code": 22, "ingredient_name": "Acetaminophen"}],
        "ingredient_name",
        "Acetaminophen",
        True,
    ),
    (
        "form",
        "form/",
        {"id": 5},
        [{"drug_code": 5, "pharmaceutical_form_name": "Tablet"}],
        "pharmaceutical_form_name",
        "Tablet",
        True,
    ),
    (
        "packaging",
        "packaging/",
        {"id": 11685},
        {
            "drug_code": 11685,
            "package_type": "Blister Pack",
            "package_size": "24",
            "package_size_unit": "Ea",
        },
        "package_type",
        "Blister Pack",
        False,
    ),
    (
        "pharmaceutical_std",
        "pharmaceuticalstd/",
        {"id": 10},
        {"drug_code": 10, "pharmaceutical_std": "USP"},
        "pharmaceutical_std",
        "USP",
        False,
    ),
    (
        "route",
        "route/",
        {"id": 12},
        [{"drug_code": 12, "route_of_administration_name": "Oral"}],
        "route_of_administration_name",
        "Oral",
        True,
    ),
    (
        "schedule",
        "schedule/",
        {"id": 9},
        [{"drug_code": 9, "schedule_name": "OTC"}],
        "schedule_name",
        "OTC",
        True,
    ),
    (
        "status",
        "status/",
        {"id": 44},
        [{"drug_code": 44, "status": "Marketed"}],
        "status",
        "Marketed",
        True,
    ),
    (
        "therapeutic_class",
        "therapeuticclass/",
        {"id": 7},
        [{"drug_code": 7, "tc_ahfs": "Antidepressants"}],
        "tc_ahfs",
        "Antidepressants",
        True,
    ),
    (
        "veterinary_species",
        "veterinaryspecies/",
        {"id": 3},
        [{"drug_code": 3, "vet_species_name": "Canine"}],
        "vet_species_name",
        "Canine",
        True,
    ),
]


@pytest.fixture()
def client() -> Generator[DPDClient, None, None]:
    instance = DPDClient()
    yield instance
    instance.close()


@pytest.mark.parametrize(
    "method_name, endpoint, kwargs, payload, attr, expected, expect_lang",
    SYNC_ENDPOINT_CASES,
)
@respx.mock
def test_sync_endpoints_return_models_and_expected_query_params(
    client: DPDClient,
    method_name: str,
    endpoint: str,
    kwargs: dict,
    payload: object,
    attr: str,
    expected: str,
    expect_lang: bool,
) -> None:
    route = respx.get(f"{BASE_URL}{endpoint}").mock(return_value=httpx.Response(200, json=payload))

    items = getattr(client, method_name)(**kwargs)

    assert route.called
    assert len(items) == 1
    assert getattr(items[0], attr) == expected

    request = route.calls.last.request
    params = dict(request.url.params)
    assert params.get("type") == "json"
    if expect_lang:
        assert params.get("lang") == "en"
    else:
        assert "lang" not in params


def test_drug_product_requires_filter(client: DPDClient) -> None:
    with pytest.raises(DPDInvalidParam):
        client.drug_product()


def test_active_ingredient_requires_filter(client: DPDClient) -> None:
    with pytest.raises(DPDInvalidParam):
        client.active_ingredient()


@pytest.mark.parametrize(
    "method_name, endpoint",
    [
        ("form", "form/"),
        ("route", "route/"),
        ("schedule", "schedule/"),
    ],
)
@respx.mock
def test_sync_endpoints_map_active_true_to_yes(
    client: DPDClient, method_name: str, endpoint: str
) -> None:
    route = respx.get(f"{BASE_URL}{endpoint}").mock(return_value=httpx.Response(200, json=[{"drug_code": 1}]))

    getattr(client, method_name)(id=1, active=True)

    request = route.calls.last.request
    params = dict(request.url.params)
    assert params.get("active") == "yes"


@respx.mock
def test_sync_caching_prevents_second_request() -> None:
    route = respx.get(f"{BASE_URL}drugproduct/").mock(
        return_value=httpx.Response(
            200,
            json={
                "drug_code": 1,
                "drug_identification_number": "00000000",
                "brand_name": "Example",
            },
        )
    )

    client = DPDClient(cache_ttl=60)
    try:
        first = client.drug_product(din="00000000")
        second = client.drug_product(din="00000000")
    finally:
        client.close()

    assert len(first) == 1
    assert len(second) == 1
    assert route.call_count == 1


@respx.mock
def test_sync_404_raises_http_error() -> None:
    respx.get(f"{BASE_URL}drugproduct/").mock(return_value=httpx.Response(404, text="missing"))

    client = DPDClient()
    try:
        with pytest.raises(DPDHTTPError):
            client.drug_product(din="does-not-exist")
    finally:
        client.close()


@respx.mock
def test_sync_decode_error() -> None:
    respx.get(f"{BASE_URL}drugproduct/").mock(return_value=httpx.Response(200, text="not-json"))

    client = DPDClient()
    try:
        with pytest.raises(DPDDecodeError):
            client.drug_product(din="12345678")
    finally:
        client.close()


@respx.mock
def test_sync_retries_on_5xx_then_succeeds() -> None:
    responses = [
        httpx.Response(500, text="err1"),
        httpx.Response(502, text="err2"),
        httpx.Response(200, json=[{"drug_code": 2, "drug_identification_number": "11111111"}]),
    ]
    route = respx.get(f"{BASE_URL}drugproduct/").mock(side_effect=responses)

    client = DPDClient(retries=3)
    try:
        items = client.drug_product(din="11111111")
    finally:
        client.close()

    assert len(items) == 1
    assert route.call_count == 3
