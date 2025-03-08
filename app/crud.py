from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from fastapi import HTTPException

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=user.password  # Remember to hash properly in production
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Product CRUD
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.product_id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Product Variation CRUD
def get_product_variation(db: Session, variation_id: int):
    return db.query(models.ProductVariation).filter(models.ProductVariation.variation_id == variation_id).first()

def get_product_variations(db: Session, product_id: int):
    return db.query(models.ProductVariation).filter(models.ProductVariation.product_id == product_id).all()

def create_product_variation(db: Session, variation: schemas.ProductVariationCreate, product_id: int):
    db_variation = models.ProductVariation(
        product_id=product_id,
        **variation.dict()
    )
    db.add(db_variation)
    db.commit()
    db.refresh(db_variation)
    return db_variation

# Order CRUD
def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.order_id == order_id).first()

def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    db_order = models.Order(
        user_id=user_id,
        **order.dict()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order_status(db: Session, order_id: int, status: schemas.OrderStatus):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        return None
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order

# Review CRUD
def create_review(db: Session, review: schemas.ReviewCreate, user_id: int, product_id: int):
    db_review = models.Review(
        user_id=user_id,
        product_id=product_id,
        **review.dict()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_product_reviews(db: Session, product_id: int):
    return db.query(models.Review).filter(models.Review.product_id == product_id).all()

# Inventory CRUD
def get_inventory(db: Session, variation_id: int):
    return db.query(models.Inventory).filter(models.Inventory.variation_id == variation_id).first()

def update_inventory(db: Session, variation_id: int, quantity: int):
    inventory = db.query(models.Inventory).filter(models.Inventory.variation_id == variation_id).first()
    if not inventory:
        return None
    inventory.quantity = quantity
    db.commit()
    db.refresh(inventory)
    return inventory