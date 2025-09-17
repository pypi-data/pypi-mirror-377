from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class ActiveIngredient(BaseModelConfig):
    drug_code: int
    ingredient_name: str
    dosage_unit: Optional[str] = ""
    dosage_value: Optional[str] = None
    strength: Optional[str] = None
    strength_unit: Optional[str] = None


class Company(BaseModelConfig):
    company_code: int
    company_name: str
    company_type: Optional[str] = None
    city_name: Optional[str] = None
    country_name: Optional[str] = None
    post_office_box: Optional[str] = None
    postal_code: Optional[str] = None
    province_name: Optional[str] = None
    street_name: Optional[str] = None
    suite_number: Optional[str] = None


class DrugProduct(BaseModelConfig):
    drug_code: int
    drug_identification_number: Optional[str] = None
    brand_name: Optional[str] = None
    class_name: Optional[str] = None
    descriptor: Optional[str] = None
    number_of_ais: Optional[str] = None
    ai_group_no: Optional[str] = None
    company_name: Optional[str] = None
    last_update_date: Optional[str] = None


class DosageForm(BaseModelConfig):
    drug_code: int
    pharmaceutical_form_code: Optional[int] = None
    pharmaceutical_form_name: Optional[str] = None


class Packaging(BaseModelConfig):
    drug_code: int
    package_size: Optional[str] = None
    package_size_unit: Optional[str] = None
    package_type: Optional[str] = None
    product_information: Optional[str] = None
    upc: Optional[str] = None


class PharmaceuticalStandard(BaseModelConfig):
    drug_code: int
    pharmaceutical_std: Optional[str] = None


class RouteOfAdministration(BaseModelConfig):
    drug_code: int
    route_of_administration_code: Optional[int] = None
    route_of_administration_name: Optional[str] = None


class Schedule(BaseModelConfig):
    drug_code: int
    schedule_name: Optional[str] = None


class ProductStatus(BaseModelConfig):
    drug_code: int
    expiration_date: Optional[str] = None
    external_status_code: Optional[str] = None
    history_date: Optional[str] = None
    lot_number: Optional[str] = None
    original_market_date: Optional[str] = None
    status: Optional[str] = None


class TherapeuticClass(BaseModelConfig):
    drug_code: int
    tc_ahfs: Optional[str] = None
    tc_ahfs_number: Optional[str] = None
    tc_atc: Optional[str] = None
    tc_atc_number: Optional[str] = None


class VeterinarySpecies(BaseModelConfig):
    drug_code: int
    vet_species_name: Optional[str] = None
