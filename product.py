from decimal import Decimal
from enum import Enum
from operator import eq, or_
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query
from database import (
    get_db,
    Product,
    Category,
    Size,
    Style,
    Brand,
    BrasType,
    Color,
    Material,
    PantiesType,
)
from sqlmodel import SQLModel, Field, Session, select

product = APIRouter(tags=["product"])


@product.get("/sizes", response_model=list[Size])
async def sizes(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(Size)).all()


@product.get("/styles", response_model=list[Style])
async def styles(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(Style)).all()


@product.get("/brands", response_model=list[Brand])
async def brands(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(Brand)).all()


@product.get("/bras_types", response_model=list[BrasType])
async def bras_types(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(BrasType)).all()


@product.get("/colors", response_model=list[Color])
async def colors(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(Color)).all()


@product.get("/materials", response_model=list[Material])
async def materials(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(Material)).all()


@product.get("/panties_types", response_model=list[PantiesType])
async def panties_types(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(PantiesType)).all()


@product.get("/categories", response_model=list[Category])
async def categories(session: Annotated[Session, Depends(get_db)]):
    return session.scalars(select(Category)).all()


class FilterParams(SQLModel):
    category_id: list[int | Category] | None = Field(default=None)
    size_id: list[int | Size] | None = Field(default=None)
    style_id: list[int | Style] | None = Field(default=None)
    brand_id: list[int | Brand] | None = Field(default=None)
    bras_type_id: list[int | BrasType] | None = Field(default=None)
    color_id: list[int | Color] | None = Field(default=None)
    material_id: list[int | Material] | None = Field(default=None)
    panties_type_id: list[int | PantiesType] | None = Field(default=None)

    available: bool = Field(default=True)
    price_min: Decimal | None = Field(default=0, max_digits=15, decimal_places=2)
    price_max: Decimal | None = Field(default=0, max_digits=15, decimal_places=2)
    offset: int = 0
    limit: int = Query(default=100, le=100)


def validate_price(
    prod: Product, filter_query: Annotated[FilterParams, Query()]
) -> bool:
    result = False
    if filter_query.price_max and filter_query.price_min:
        result = filter_query.price_min <= prod.price <= filter_query.price_max
    elif filter_query.price_max:
        result = prod.price <= filter_query.price_max
    elif filter_query.price_min:
        result = filter_query.price_min <= prod.price
    else:
        result = True
    return result


@product.get("/all", response_model=list[Product])
async def product_list(
    filter_query: Annotated[FilterParams, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> list[Product]:
    sql = select(Product)
    if filter_query.available:
        sql = sql.where(Product.count > 0)
    else:
        sql = sql.where(Product.count == 0)

    if filter_query.category_id:
        sql = sql.where(Product.category_id.in_(filter_query.category_id))

    if filter_query.size_id:
        sql = sql.where(Product.size_id.in_(filter_query.size_id))
    if filter_query.style_id:
        sql = sql.where(Product.style_id.in_(filter_query.style_id))
    if filter_query.brand_id:
        sql = sql.where(Product.brand_id.in_(filter_query.brand_id))
    if filter_query.bras_type_id:
        sql = sql.where(Product.bras_type_id.in_(filter_query.bras_type_id))
    if filter_query.color_id:
        sql = sql.where(Product.color_id.in_(filter_query.color_id))
    if filter_query.material_id:
        sql = sql.where(Product.material_id.in_(filter_query.material_id))
    if filter_query.panties_type_id:
        sql = sql.where(Product.panties_type_id.in_(filter_query.panties_type_id))

    if filter_query.offset:
        sql = sql.offset(filter_query.offset)
    if filter_query.limit:
        sql = sql.limit(filter_query.limit)

    items = db.scalars(sql)
    db.commit()
    items = list(filter(lambda prod: validate_price(prod, filter_query), items))
    return items
