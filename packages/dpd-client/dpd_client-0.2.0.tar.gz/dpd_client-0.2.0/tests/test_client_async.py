from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
import respx

from dpd_client import AsyncDPDClient
from dpd_client.client import BASE_URL


ASYNC_ENDPOINT_CASES = [
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


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator[AsyncDPDClient, None]:
    instance = AsyncDPDClient()
    try:
        yield instance
    finally:
        await instance.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name, endpoint, kwargs, payload, attr, expected, expect_lang",
    ASYNC_ENDPOINT_CASES,
)
@respx.mock
async def test_async_endpoints_return_models_and_expected_query_params(
    async_client: AsyncDPDClient,
    method_name: str,
    endpoint: str,
    kwargs: dict,
    payload: object,
    attr: str,
    expected: str,
    expect_lang: bool,
) -> None:
    route = respx.get(f"{BASE_URL}{endpoint}").mock(return_value=httpx.Response(200, json=payload))

    result = await getattr(async_client, method_name)(**kwargs)

    assert route.called
    assert len(result) == 1
    assert getattr(result[0], attr) == expected

    request = route.calls.last.request
    params = dict(request.url.params)
    assert params.get("type") == "json"
    if expect_lang:
        assert params.get("lang") == "en"
    else:
        assert "lang" not in params


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name, endpoint",
    [
        ("form", "form/"),
        ("route", "route/"),
        ("schedule", "schedule/"),
    ],
)
@respx.mock
async def test_async_endpoints_map_active_true_to_yes(
    async_client: AsyncDPDClient, method_name: str, endpoint: str
) -> None:
    route = respx.get(f"{BASE_URL}{endpoint}").mock(return_value=httpx.Response(200, json=[{"drug_code": 1}]))

    await getattr(async_client, method_name)(id=1, active=True)

    request = route.calls.last.request
    params = dict(request.url.params)
    assert params.get("active") == "yes"
