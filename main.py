import flask
from flask_peewee.db import Database
from flask_peewee.auth import Auth

DATABASE = {
    'name': 'pizza.db',
    'engine': 'peewee.SqliteDatabase'
}
SECRET_KEY = 'afagfasgasgagfagsa'

app = flask.Flask(__name__) 
app.config.from_object(__name__)

db = Database(app)
auth = Auth(app, db)


class Pizza:

    def __init__(self, name, ingredients, size, price):
        self.name = name
        self.ingredients = ingredients
        self.size = size
        self.price = price


pizzas = [
    Pizza('siera', 'siers', 20, 5),
    Pizza('margarita', 'siers', 45, 20),
]

@app.route('/')
def home():
    return flask.render_template('home.html', pizzas=pizzas)


@app.route('/create_pizza', methods=['GET', 'POST'])
def create_pizza():
    if flask.request.method == 'POST':
        new_pizza = Pizza(
            name=flask.request.form.get('pizza_name'),
            ingredients=flask.request.form.get('ingredients'),
            size=int(flask.request.form.get('size')),
            price=float(flask.request.form.get('price'))
        )
        pizzas.append(new_pizza)
        return flask.redirect(flask.url_for('home'))

    return flask.render_template('create_pizza.html')


@app.route('/get_pizza/<int:id>')
def get_pizza(id):
    pizza = pizzas[id]
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

    cart_pizzas = [pizzas[i] for i in cart]
    return flask.render_template('my_cart.html', pizzas=cart_pizzas)

if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    app.run(debug=True)
