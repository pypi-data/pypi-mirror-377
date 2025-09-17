from __future__ import annotations

import json
from typing import Optional

import typer
from rich import print_json

from .client import DPDClient


app = typer.Typer(help="CLI for Health Canada DPD API")


def _client(lang: str) -> DPDClient:
    return DPDClient(lang=lang)


@app.command()
def drugproduct(
    id: Optional[int] = typer.Option(None, help="Drug product code"),
    din: Optional[str] = typer.Option(None, help="DIN"),
    brandname: Optional[str] = typer.Option(None, help="Brand name (supports partial)"),
    status: Optional[str] = typer.Option(None, help="Product status code"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.drug_product(id=id, din=din, brandname=brandname, status=status, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def company(
    id: int = typer.Option(..., help="Company code"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.company(id=id, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def activeingredient(
    id: Optional[int] = typer.Option(None, help="Drug product code"),
    ingredientname: Optional[str] = typer.Option(None, help="Ingredient name filter"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.active_ingredient(id=id, ingredientname=ingredientname, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def form(
    id: int = typer.Option(..., help="Drug product code"),
    active: bool = typer.Option(False, help="Only active forms"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.form(id=id, active=active, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def route(
    id: int = typer.Option(..., help="Drug product code"),
    active: bool = typer.Option(False, help="Only active routes"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.route(id=id, active=active, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def schedule(
    id: int = typer.Option(..., help="Drug product code"),
    active: bool = typer.Option(False, help="Only active schedules"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.schedule(id=id, active=active, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def status(
    id: int = typer.Option(..., help="Drug product code"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.status(id=id, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def packaging(
    id: int = typer.Option(..., help="Drug product code"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client("en")
    try:
        items = client.packaging(id=id)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def pharmaceuticalstd(
    id: int = typer.Option(..., help="Drug product code"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client("en")
    try:
        items = client.pharmaceutical_std(id=id)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def therapeuticclass(
    id: int = typer.Option(..., help="Drug product code"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.therapeutic_class(id=id, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()


@app.command()
def veterinaryspecies(
    id: int = typer.Option(..., help="Drug product code"),
    lang: str = typer.Option("en", help="Language: en or fr"),
    pretty: bool = typer.Option(True, help="Pretty print JSON output"),
):
    client = _client(lang)
    try:
        items = client.veterinary_species(id=id, lang=lang)
        data = [item.model_dump() for item in items]
        if pretty:
            print_json(data=data)
        else:
            typer.echo(json.dumps(data))
    finally:
        client.close()
if __name__ == "__main__":  # pragma: no cover
    app()
