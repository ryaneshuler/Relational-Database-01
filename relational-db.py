from sqlalchemy import Boolean, ForeignKey, create_engine, Column, Integer, String, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from urllib.parse import quote_plus

pw = quote_plus("Konstantine42!")
engine = create_engine(f"mysql+mysqlconnector://root:{pw}@127.0.0.1/relational-db-01")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
    # Create relationship where User can have many Orders
    orders = relationship("Order", back_populates="user")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    price = Column(Integer)
    # Create relationship where Product can have many Orders
    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

    # define status here so metadata.create_all() includes it
    status = Column(Boolean, default=False)

Base.metadata.create_all(engine)

# Create users, products, and orders

user1 = User(name="John Doe", email="john.doe@example.com")
session.add(user1)

user2 = User(name="Jane Smith", email="jane.smith@example.com")
session.add(user2)

user3 = User(name="Alice Johnson", email="alice.johnson@example.com")
session.add(user3)

product1 = Product(name="Laptop", price=1000)
session.add(product1)

product2 = Product(name="Smartphone", price=500)
session.add(product2)

product3 = Product(name="Tablet", price=300)
session.add(product3)

# add users/products first and flush so they get ids (or use relationships directly)
session.add_all([user1, user2, user3, product1, product2, product3])
session.flush()  # assigns primary keys without committing

# create orders using object relationships
order1 = Order(user=user1, product=product1, quantity=1)
order2 = Order(user=user2, product=product2, quantity=2)
order3 = Order(user=user2, product=product3, quantity=4)
order4 = Order(user=user1, product=product2, quantity=3)

session.add_all([order1, order2, order3, order4])
session.commit()

# Retrieve all users and print their information
users = session.query(User).all()
for user in users:
    print(f"User: {user.name}, Email: {user.email}")

# Retrieve all products and print their name and price.
products = session.query(Product).all()
for product in products:
    print(f"Product: {product.name}, Price: {product.price}")

# Retrieve all orders, showing the user’s name, product name, and quantity.
orders = session.query(Order).all()
for order in orders:
    print(f"Order: User: {order.user.name}, Product: {order.product.name}, Quantity: {order.quantity}")

# Update a product's price
product_to_update = session.query(Product).filter_by(name="Laptop").first()
if product_to_update:
    product_to_update.price = 1200
    session.commit()

# Delete user with user_id 3
user_to_delete = session.query(User).filter_by(id=3).first()
if user_to_delete:
    session.delete(user_to_delete)
    session.commit()

# Add status value of True to orders 2 and 4
order2 = session.query(Order).filter_by(id=2).first()
if order2:
    order2.status = True

order4 = session.query(Order).filter_by(id=4).first()
if order4:
    order4.status = True

session.commit()

# Query all shipped orders
shipped_orders = session.query(Order).filter_by(status=True).all()
for order in shipped_orders:
    print(f"Shipped Order: User: {order.user.name}, Product: {order.product.name}, Quantity: {order.quantity}")

# Count total number of orders per user
user_order_counts = session.query(Order.user_id, func.count(Order.id)).group_by(Order.user_id).all()
for user_id, order_count in user_order_counts:
    user = session.query(User).filter_by(id=user_id).first()
    print(f"User: {user.name}, Total Orders: {order_count}")
