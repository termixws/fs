from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
products = []


class Product(BaseModel):
    id: int
    name: str
    price: float


@app.post("/products")
def add_products(product: Product):
    for p in products:
        if p.id == product.id:
            return {"error" : "product with this id already exists"}
    products.append(product)
    return product

@app.get("/products")
def get_products():
    return products

@app.get("/products/search")
def product_serch(min_price : float, max_price : float):
    result = []
    for product in products:
        if min_price <= product.price <= max_price:
            result.append(product)
    return result