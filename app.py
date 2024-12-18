from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, IntegerField, FieldList, FormField, SelectField, FloatField, ValidationError
from wtforms.validators import DataRequired, Email, NumberRange
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from datetime import datetime, timedelta
import secrets
from faker import Faker
import random

# --- Configuration ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fnb.db'  # Use SQLite for development
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

# --- Initialize SQLAlchemy with the Flask app ---
from models import db  # Import the SQLAlchemy instance
db.init_app(app)  # Initialize the SQLAlchemy instance with the Flask app

# --- Import models after initializing SQLAlchemy ---
from models import Customer, Order, OrderItem, MenuItem

# --- Forms ---
class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Add Customer')

    def validate_email(self, email):
        customer = Customer.query.filter_by(email=email.data).first()
        if customer:
            raise ValidationError('Email already exists. Please use a different email.')

class EditCustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Update Customer')

class MenuItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Add Menu Item')

class EditMenuItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Update Menu Item')

class OrderItemForm(FlaskForm):
    menu_item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.menu_item_id.choices = [(item.id, f"{item.name} (${item.price:.2f})") for item in MenuItem.query.all()]

class OrderForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    items = FieldList(FormField(OrderItemForm), min_entries=1)
    submit = SubmitField('Place Order')

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        if not self.customer_id.choices:
            self.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]

        # Ensure menu items exist and set choices if not already set
        if not self.items.entries or not self.items.entries[0].form.menu_item_id.choices:
            menu_items = MenuItem.query.all()
            if not menu_items:
                raise ValueError("No menu items exist. Please add menu items first.")
            for item_form in self.items:
                item_form.menu_item_id.choices = [(item.id, f"{item.name} (${item.price:.2f})") for item in menu_items]

class EditOrderForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    items = FieldList(FormField(OrderItemForm), min_entries=1)
    submit = SubmitField('Update Order')

    def __init__(self, *args, **kwargs):
        super(EditOrderForm, self).__init__(*args, **kwargs)
        self.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Customer Routes ---
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(name=form.name.data, email=form.email.data, phone=form.phone.data)
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('view_customers'))
    return render_template('add_customer.html', form=form)

@app.route('/view_customers')
def view_customers():
    customers = Customer.query.all()
    return render_template('view_customers.html', customers=customers)

@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = EditCustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('view_customers'))
    return render_template('edit_customer.html', form=form, customer=customer)

# --- Menu Routes ---
@app.route('/add_menu_item', methods=['GET', 'POST'])
def add_menu_item():
    form = MenuItemForm()
    if form.validate_on_submit():
        # Create a new menu item
        menu_item = MenuItem(name=form.name.data, price=form.price.data)
        db.session.add(menu_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('view_menu'))
    return render_template('add_menu_item.html', form=form)

@app.route('/view_menu')
def view_menu():
    menu_items = MenuItem.query.all()
    return render_template('view_menu.html', menu_items=menu_items)

@app.route('/edit_menu_item/<int:id>', methods=['GET', 'POST'])
def edit_menu_item(id):
    menu_item = MenuItem.query.get_or_404(id)
    form = EditMenuItemForm(obj=menu_item)
    if form.validate_on_submit():
        menu_item.name = form.name.data
        menu_item.price = form.price.data
        db.session.commit()
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('view_menu'))
    return render_template('edit_menu_item.html', form=form, menu_item=menu_item)

# --- Order Routes ---
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    # Ensure there are menu items and customers
    if MenuItem.query.count() == 0:
        flash('Please add menu items before creating an order.', 'error')
        return redirect(url_for('add_menu_item'))
    
    if Customer.query.count() == 0:
        flash('Please add customers before creating an order.', 'error')
        return redirect(url_for('add_customer'))

    form = OrderForm()
    
    if request.method == 'POST':
        print("request form is : ", request.form)
        customer_id = request.form.get('customer_id')
        items_data = []
        item_index = 0
        while True:
            item_prefix = f'items-{item_index}'
            menu_item_id_key = f'{item_prefix}-menu_item_id'
            quantity_key = f'{item_prefix}-quantity'
            
            if menu_item_id_key in request.form and quantity_key in request.form:
                try:
                    menu_item_id = int(request.form[menu_item_id_key])
                    quantity = int(request.form[quantity_key])
                    if quantity > 0:
                        items_data.append({
                            'menu_item_id': menu_item_id,
                            'quantity': quantity
                        })

                except ValueError:
                    print(f"Error: Invalid data type for menu_item_id or quantity at index {item_index}")

                item_index += 1
            else:
                break
        
        print("Items data is : ", items_data)
        # Form validation and order creation
        if customer_id and items_data:
            try:
                order = Order(customer_id=customer_id)
                db.session.add(order)
                db.session.flush()

                for item in items_data:
                    menu_item = MenuItem.query.get(item['menu_item_id'])
                    if menu_item:
                        order_item = OrderItem(
                            order_id=order.id,
                            menu_item_id=item['menu_item_id'],
                            quantity=item['quantity'],
                            price=menu_item.price
                        )
                        db.session.add(order_item)

                db.session.commit()
                flash('Order added successfully!', 'success')
                return redirect(url_for('view_orders'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error creating order: {str(e)}', 'error')
        else:
            flash('Please select a customer and add at least one item.', 'error')

    return render_template('add_order.html', form=form)

    
@app.route('/view_orders')
def view_orders():
    orders = Order.query.all()
    return render_template('view_orders.html', orders=orders)

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = EditOrderForm(obj=order)

    # Populate the items FieldList with existing order items
    if request.method == 'GET':
        form.items.pop_entry()
        for item in order.order_items:
            item_form = OrderItemForm(obj=item)
            item_form.menu_item_id.data = item.menu_item_id
            form.items.append_entry(item_form)

    if form.validate_on_submit():
        # Update customer ID
        order.customer_id = form.customer_id.data

        # Update or add order items
        new_order_items = []
        for item_form in form.items:
            if item_form.quantity.data > 0:
                menu_item = MenuItem.query.get(item_form.menu_item_id.data)
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item_form.menu_item_id.data,
                    quantity=item_form.quantity.data,
                    price=menu_item.price
                )
                new_order_items.append(order_item)

        # Replace old order items with new ones
        order.order_items = new_order_items
        db.session.commit()

        flash('Order updated successfully!', 'success')
        return redirect(url_for('view_orders'))

    return render_template('edit_order.html', form=form, order=order)

# --- Reporting Routes ---
@app.route('/query_outer_join')
def query_outer_join():
    results = db.session.query(Customer.name, func.count(Order.id).label('order_count')) \
        .outerjoin(Order, Customer.id == Order.customer_id) \
        .group_by(Customer.name) \
        .all()
    headers = ["Customer Name", "Order Count"]
    return render_template('query_results.html', results=results, query_name="Customers and Their Order Counts (Outer Join)", headers=headers)

@app.route('/query_four_table_join')
def query_four_table_join():
    results = db.session.query(Customer.name, Order.order_date, MenuItem.name, func.sum(OrderItem.quantity).label('total_quantity')) \
        .join(Order, Customer.id == Order.customer_id) \
        .join(OrderItem, Order.id == OrderItem.order_id) \
        .join(MenuItem, OrderItem.menu_item_id == MenuItem.id) \
        .group_by(Customer.name, Order.order_date, MenuItem.name) \
        .all()
    headers = ["Customer Name", "Order Date", "Item Name", "Total Quantity"]
    return render_template('query_results.html', results=results, query_name="Total Quantity of Each Item Sold (4-Table Join)", headers=headers)

@app.route('/query_subqueries')
def query_subqueries():
    # Calculate total price per order
    order_totals = db.session.query(
        Order.id.label('order_id'),
        func.sum(OrderItem.quantity * OrderItem.price).label('total_price')
    ).join(OrderItem, Order.id == OrderItem.order_id) \
     .group_by(Order.id) \
     .subquery()

    # Calculate average total price
    average_total = db.session.query(func.avg(order_totals.c.total_price)).scalar()

    # Find customers with orders above average total price
    results = db.session.query(Customer.name) \
               .join(Order, Customer.id == Order.customer_id) \
               .join(order_totals, Order.id == order_totals.c.order_id) \
               .filter(order_totals.c.total_price > average_total) \
               .all()

    headers = ["Customer Name"]
    return render_template('query_results.html', results=results, query_name="Customers with Above-Average Order Total", headers=headers)

@app.route('/query_frequently_ordered_together')
def query_frequently_ordered_together():
    order_alias = aliased(Order)
    oi1 = aliased(OrderItem)
    oi2 = aliased(OrderItem)

    results = db.session.query(
        oi1.menu_item_id,
        oi2.menu_item_id,
        func.count().label('frequency')
    ).join(order_alias, oi1.order_id == order_alias.id) \
      .join(oi2, and_(order_alias.id == oi2.order_id, oi1.menu_item_id < oi2.menu_item_id)) \
      .group_by(oi1.menu_item_id, oi2.menu_item_id) \
      .order_by(func.count().desc()) \
      .all()

    # Fetch menu item names
    menu_items = {item.id: item.name for item in MenuItem.query.all()}
    formatted_results = []
    for row in results:
        formatted_results.append((
            menu_items[row[0]],
            menu_items[row[1]],
            row[2]
        ))

    headers = ["Item 1", "Item 2", "Frequency"]
    return render_template('query_results.html', results=formatted_results, query_name="Frequently Ordered Menu Items Together", headers=headers)

# --- Search Feature for Orders ---
@app.route('/search_orders', methods=['GET', 'POST'])
def search_orders():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        min_total_price = request.form.get('min_total_price')
        max_total_price = request.form.get('max_total_price')

        query = db.session.query(
            Order.id,
            Customer.name,
            Order.order_date,
            func.sum(OrderItem.quantity * OrderItem.price).label('total_price')
        ).join(Customer, Order.customer_id == Customer.id) \
          .join(OrderItem, Order.id == OrderItem.order_id) \
          .group_by(Order.id, Customer.name, Order.order_date)

        if customer_name:
            query = query.filter(Customer.name.like(f"%{customer_name}%"))
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        if min_total_price:
            query = query.having(func.sum(OrderItem.quantity * OrderItem.price) >= float(min_total_price))
        if max_total_price:
            query = query.having(func.sum(OrderItem.quantity * OrderItem.price) <= float(max_total_price))

        results = query.all()
        headers = ["Order ID", "Customer Name", "Order Date", "Total Price"]
        return render_template('query_results.html', results=results, query_name="Search Orders", headers=headers)

    return render_template('search_orders.html')

# --- Error Handling ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# --- Initialization ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)