# Ecommerce App

A REST API ecommerce backend built with **Flask + SQLAlchemy + JWT**.

## Structure
```
ecommerce-app/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/
│   │   └── models.py        # User, Product, CartItem, Order, OrderItem
│   └── routes/
│       ├── auth.py          # Register, Login, /me
│       ├── products.py      # CRUD products (admin write, public read)
│       ├── cart.py          # Cart management (JWT protected)
│       └── orders.py        # Place & manage orders
├── tests/
│   └── test_api.py
├── run.py
├── requirements.txt
└── .env
```

## Setup
```bash
pip install -r requirements.txt
python run.py
```

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login → JWT token |
| GET  | /api/auth/me | Current user info |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /api/products/ | List all (filter ?category=) |
| GET    | /api/products/:id | Get one |
| POST   | /api/products/ | Create (admin) |
| PUT    | /api/products/:id | Update (admin) |
| DELETE | /api/products/:id | Delete (admin) |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /api/cart/ | View cart |
| POST   | /api/cart/ | Add item |
| PUT    | /api/cart/:id | Update quantity |
| DELETE | /api/cart/:id | Remove item |
| DELETE | /api/cart/ | Clear cart |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | /api/orders/ | Place order from cart |
| GET    | /api/orders/ | List orders (own / all if admin) |
| GET    | /api/orders/:id | Order detail |
| PUT    | /api/orders/:id/status | Update status (admin) |

## Git Setup
```bash
git init
git add .
git commit -m "Initial ecommerce app"
git remote add origin <your-repo-url>
git push -u origin main
```
