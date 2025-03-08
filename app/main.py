# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import app.crud as crud
from app.database import SessionLocal, engine
import app.schemas as schemas
from app.models import *

app = FastAPI(title="E-commerce API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Product endpoints
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Order endpoints
@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, status: schemas.OrderStatus, db: Session = Depends(get_db)):
    db_order = crud.update_order_status(db, order_id=order_id, status=status)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Product variation endpoints
@app.post("/products/{product_id}/variations/", response_model=schemas.ProductVariation)
def create_product_variation(
    product_id: int,
    variation: schemas.ProductVariationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_product_variation(db=db, variation=variation, product_id=product_id)

@app.get("/products/{product_id}/variations/", response_model=List[schemas.ProductVariation])
def read_product_variations(product_id: int, db: Session = Depends(get_db)):
    variations = crud.get_product_variations(db, product_id=product_id)
    return variations

# Review endpoints
@app.post("/products/{product_id}/reviews/", response_model=schemas.Review)
def create_review(
    product_id: int,
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db)
):
    return crud.create_review(db=db, review=review, product_id=product_id)

@app.get("/products/{product_id}/reviews/", response_model=List[schemas.Review])
def read_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = crud.get_product_reviews(db, product_id=product_id)
    return reviews

# Inventory endpoints
@app.get("/inventory/{variation_id}", response_model=schemas.Inventory)
def get_inventory(variation_id: int, db: Session = Depends(get_db)):
    inventory = crud.get_inventory(db, variation_id=variation_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@app.put("/inventory/{variation_id}", response_model=schemas.Inventory)
def update_inventory(
    variation_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    inventory = crud.update_inventory(db, variation_id=variation_id, quantity=quantity)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory