from fastapi import FastAPI, HTTPException
from app.database import Database
import psycopg2
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import time
from fastapi import Request

app = FastAPI()

@app.middleware("http")
async def log_request_latency(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    print(f"Latency: {latency:.4f}s | {request.method} {request.url.path}")  # Simplified URL
    return response

# Initialize database connection pool
@app.on_event("startup")
async def startup():
    Database.initialize()

@app.on_event("shutdown")
async def shutdown():
    Database.close_all_connections()

# Simplified Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str

class AddressCreate(BaseModel):
    user_id: int
    street_address: str
    city: str
    country: str

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: float

class OrderCreate(BaseModel):
    user_id: int
    total_amount: float
    status: Optional[str] = "pending"

class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: float

class ReviewCreate(BaseModel):
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None

# Root endpoint
@app.get("/")
async def root():
    return {"message": "E-Commerce API"}

# User endpoints
@app.post("/users", status_code=201)
async def create_user(user: UserCreate):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id",
            (user.username, user.email, user.password_hash)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"user_id": user_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Convert to dict for better JSON serialization
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, user))
        return {"user": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Address endpoints
@app.post("/addresses", status_code=201)
async def create_address(address: AddressCreate):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO addresses (user_id, street_address, city, country) "
            "VALUES (%s, %s, %s, %s) RETURNING address_id",
            (address.user_id, address.street_address, address.city, address.country)
        )
        address_id = cursor.fetchone()[0]
        conn.commit()
        return {"address_id": address_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

@app.get("/addresses/{address_id}")
async def get_address(address_id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM addresses WHERE address_id = %s", (address_id,))
        address = cursor.fetchone()
        if address is None:
            raise HTTPException(status_code=404, detail="Address not found")
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, address))
        return {"address": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Category endpoints
@app.post("/categories", status_code=201)
async def create_category(name: str):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (name) VALUES (%s) RETURNING category_id",
            (name,)
        )
        category_id = cursor.fetchone()[0]
        conn.commit()
        return {"category_id": category_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

@app.get("/categories/{category_id}")
async def get_category(category_id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,))
        category = cursor.fetchone()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, category))
        return {"category": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Product endpoints
@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (name, description, category_id, price) VALUES (%s, %s, %s, %s) RETURNING product_id",
            (product.name, product.description, product.category_id, product.price)
        )
        product_id = cursor.fetchone()[0]
        conn.commit()
        return {"product_id": product_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, product))
        return {"product": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Order endpoints
@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, %s) RETURNING order_id",
            (order.user_id, order.total_amount, order.status)
        )
        order_id = cursor.fetchone()[0]
        conn.commit()
        return {"order_id": order_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, order))
        return {"order": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Order Item endpoints
@app.post("/order-items", status_code=201)
async def create_order_item(item: OrderItemCreate):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s) RETURNING order_item_id",
            (item.order_id, item.product_id, item.quantity, item.price)
        )
        item_id = cursor.fetchone()[0]
        conn.commit()
        return {"order_item_id": item_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Review endpoints
@app.post("/reviews", status_code=201)
async def create_review(review: ReviewCreate):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reviews (user_id, product_id, rating, comment) VALUES (%s, %s, %s, %s) RETURNING review_id",
            (review.user_id, review.product_id, review.rating, review.comment)
        )
        review_id = cursor.fetchone()[0]
        conn.commit()
        return {"review_id": review_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

@app.get("/reviews/{review_id}")
async def get_review(review_id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM reviews WHERE review_id = %s", (review_id,))
        review = cursor.fetchone()
        if review is None:
            raise HTTPException(status_code=404, detail="Review not found")
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, review))
        return {"review": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Get all products
@app.get("/products")
async def get_all_products():
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, product)) for product in products]
        return {"products": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)

# Get user orders
@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
        orders = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, order)) for order in orders]
        return {"orders": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        Database.return_connection(conn)