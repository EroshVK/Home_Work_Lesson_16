import raw_data, json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///model.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(30))
    phone = db.Column(db.String(50))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.String(400))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


db.drop_all()
db.create_all()

for user_data in raw_data.users:
    db.session.add(User(**user_data))
    db.session.commit()

for order_data in raw_data.orders:
    order_data['start_date'] = datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
    order_data['end_date'] = datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
    db.session.add(Order(**order_data))
    db.session.commit()

for offer_data in raw_data.offers:
    db.session.add(Offer(**offer_data))
    db.session.commit()


@app.route('/users', methods=['GET', 'POST'])
def all_users():
    if request.method == 'GET':
        users = User.query.all()
        res = [user.to_dict() for user in users]
        return json.dumps(res), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(**user_data)
        db.session.commit()
        return '', 201


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_user(id: int):
    user = User.query.get(id)
    if request.method == 'GET':
        return json.dumps(user.to_dict()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.add(user)
        db.session.commit()
        return '', 204


@app.route('/orders', methods=['GET', 'POST'])
def all_orders():
    if request.method == 'GET':
        orders = Order.query.all()
        res = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['start_date'] = str(order_dict['start_date'])
            order_dict['end_date'] = str(order_dict['end_date'])
            res.append(order_dict)
        return json.dumps(res), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        orders_data = json.loads(request.data)
        db.session.add(**orders_data)
        db.session.commit()
        return '', 201


@app.route('/orders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_order(id: int):
    order = Order.query.get(id)
    if request.method == 'GET':
        order_dict = order.to_dict()
        order_dict['start_date'] = str(order_dict['start_date'])
        order_dict['end_date'] = str(order_dict['end_date'])
        return json.dumps(order_dict), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order.end_date =datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()
        order.address = order_data['address']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204


@app.route('/offers', methods=['GET', 'POST'])
def all_offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        res = [offer.to_dict() for offer in offers]
        return json.dumps(res), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        db.session.add(**offer_data)
        db.session.commit()
        return '', 201


@app.route('/offers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_offer(id: int):
    offer = Offer.query.get(id)
    if request.method == 'GET':
        return json.dumps(offer.to_dict()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
