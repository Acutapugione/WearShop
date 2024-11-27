from decimal import Decimal
import enum
from fastapi import Depends
from pydantic import computed_field
from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    Session,
    Computed,
    create_engine,
    select,
)

import product

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)  # , echo=True)


class PKMixin(SQLModel):
    id: int | None = Field(primary_key=True)


class Category(PKMixin, SQLModel, table=True):  #
    name: str = Field(index=True)
    products: list["Product"] | None = Relationship(back_populates="category")


class Size(PKMixin, SQLModel, table=True):
    name: str = Field(index=True)


class Color(PKMixin, SQLModel, table=True):
    name: str = Field(index=True)


class Brand(PKMixin, SQLModel, table=True):
    name: str = Field(index=True)


class Material(PKMixin, SQLModel, table=True):
    name: str = Field(index=True)


class Style(PKMixin, SQLModel, table=True):
    name: str = Field(index=True)


class BrasType(PKMixin, SQLModel, table=True):
    name: str = Field(index=True)


class PantiesType(PKMixin, SQLModel, table=True):
    name: str = Field(index=True)


class Product(PKMixin, SQLModel, table=True, ignore=("price",)):

    name: str = Field(index=True)
    category_id: int | None = Field(default=None, foreign_key="category.id")
    category: Category | None = Relationship(back_populates="products")

    size_id: int | None = Field(default=None, foreign_key="size.id")
    size: Size | None = Relationship()  # back_populates="products"

    color_id: int | None = Field(default=None, foreign_key="color.id")
    color: Color | None = Relationship()  # back_populates="products"

    brand_id: int | None = Field(default=None, foreign_key="brand.id")
    brand: Brand | None = Relationship()  # back_populates="products"

    material_id: int | None = Field(default=None, foreign_key="material.id")
    material: Material | None = Relationship()  # back_populates="products"

    style_id: int | None = Field(default=None, foreign_key="style.id")
    style: Style | None = Relationship()  # back_populates="products"

    bras_type_id: int | None = Field(default=None, foreign_key="brastype.id")
    bras_type: BrasType | None = Relationship()  # back_populates="products"

    panties_type_id: int | None = Field(default=None, foreign_key="pantiestype.id")
    panties_type: PantiesType | None = Relationship()  # back_populates="products"

    count: int = 0
    rating: int = 0
    discount: Decimal = Field(default=0, max_digits=5, decimal_places=3)  # Decimal(0)
    price_raw: Decimal = Field(default=0, max_digits=10, decimal_places=2)  # Decimal(0)

    # @hybrid_property
    @computed_field(return_type=Decimal)
    @property
    def price(self):
        return self.price_raw - ((self.discount / 100) * self.price_raw)

    # def price(self) -> float:
    #     return self.price_raw * self.discount


def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def init_records():
    with Session(engine) as session:
        session.bulk_save_objects(
            [
                Category(name=name)
                for name in [
                    "NEW",
                    "SALE",
                    "BRAS",
                    "PANTIES",
                    "LINGERIE",
                    "SETS",
                    "SWIMWEAR",
                    "SLEEPWEAR",
                    "HOME LINEN",
                    "INDIVIDUAL TAILORING",
                ]
            ]
        )

        session.bulk_save_objects(
            [
                Size(name=name)
                for name in [
                    "XS",
                    "S",
                    "M",
                    "L",
                    "XL",
                    "XXL",
                ]
            ]
        )

        session.bulk_save_objects(
            [
                Color(name=name)
                for name in [
                    "Білий",
                    "Чорний",
                    "Червоний",
                    "Рожевий",
                    "Синій",
                    "Зелений",
                ]
            ]
        )

        session.bulk_save_objects(
            [
                Brand(name=name)
                for name in [
                    "Agent Provocateur",
                    "Calvin Klein",
                    "Victoria's Secret",
                    "Cosabella",
                ]
            ]
        )

        # Бавовна, Шовк, Мереживо, Сатин, Поліестер, Спандекс,
        session.bulk_save_objects(
            [
                Material(name=name)
                for name in [
                    "Бавовна",
                    "Шовк",
                    "Мереживо",
                    "Сатин",
                    "Поліестер",
                    "Спандекс",
                ]
            ]
        )
        # Класичний, Спортивний, Романтичний, Сексуальний,
        session.bulk_save_objects(
            [
                Style(name=name)
                for name in [
                    "Класичний",
                    "Спортивний",
                    "Романтичний",
                    "Сексуальний",
                ]
            ]
        )
        # Push-up, Балконет, Бралет, Без кісточок, Спортивний,
        session.bulk_save_objects(
            [
                BrasType(name=name)
                for name in [
                    "Push-up",
                    "Балконет",
                    "Бралет",
                    "Без кісточок",
                    "Спортивний",
                ]
            ]
        )
        # Стрінги, Шортики, Класичні, Бразиліани,
        session.bulk_save_objects(
            [
                PantiesType(name=name)
                for name in [
                    "Стрінги",
                    "Шортики",
                    "Класичні",
                    "Бразиліани",
                ]
            ]
        )
        session.commit()
        sample = Product(
            name="Sample",
            category=session.scalars(select(Category)).first(),
            brand=session.scalars(select(Brand)).first(),
            color=session.scalars(select(Color)).first(),
            material=session.scalars(select(Material)).first(),
            size=session.scalars(select(Size)).first(),
            style=session.scalars(select(Style)).first(),
            count=10,
            price_raw=1500,
            discount=2,
            rating=100500,
        )
        session.add(sample)

        session.commit()


async def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


create_db_and_tables()
init_records()
