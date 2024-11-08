import flask
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin, ModelAdmin
from peewee import TextField, IntegerField, FloatField

DATABASE = {
    'name': 'pizza.db',
    'engine': 'peewee.SqliteDatabase'
}
SECRET_KEY = 'afagfasgasgagfagsa'

app = flask.Flask(__name__) 
app.config.from_object(__name__)

db = Database(app)
auth = Auth(app, db)
admin = Admin(app, auth)


class Pizzas(db.Model):
    name = TextField()
    ingredients = TextField()
    size = IntegerField()
    price = FloatField()

class PizzaAdmin(ModelAdmin):
    columns: ('name')


admin.register(Pizzas, PizzaAdmin)
admin.setup()


@app.route('/')
def home():
    pizzas = Pizzas.select()
    return flask.render_template('home.html', pizzas=pizzas)


@app.route('/get_pizza/<int:id>')
def get_pizza(id):
    pizza = Pizzas.get_by_id(id)
    return flask.render_template('get_pizza.html',
                                 pizza=pizza, pizza_id=id)


@app.route('/buy_pizza', methods=['POST'])
def buy_pizza():
    pizza_id = flask.request.form.get('pizza_id')

    if 'cart' in flask.session:
        cart = flask.session['cart']
        cart.append(int(pizza_id))
        flask.session['cart'] = cart
    else:
        flask.session['cart'] = [int(pizza_id)]

    return flask.redirect(flask.url_for('my_cart'))


@app.route('/my_cart')
def my_cart():
    if 'cart' in flask.session:
        cart = flask.session['cart']
    else:
        cart = []

    cart_pizzas = [Pizzas.get_by_id(id) for i in cart]
    return flask.render_template('my_cart.html', pizzas=cart_pizzas)


@app.route('/create_admin')
def create_admin():
    auth.User.create_table(fail_silently=True)
    admin = auth.User(username='admin', email='', admin=True, active=True)
    admin.set_password('admin')
    admin.save()

    return 'admin created'


if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    Pizzas.create_table(fail_silently=True)
    app.run(debug=True)
