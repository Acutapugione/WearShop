from fastapi import (
    FastAPI,
)
from product import product


app = FastAPI()


app.include_router(product)
