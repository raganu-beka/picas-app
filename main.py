import flask
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin, ModelAdmin
from peewee import TextField, IntegerField, FloatField

from werkzeug.utils import secure_filename

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FloatField as FF
from wtforms.validators import DataRequired, Length, EqualTo

import os

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
    picture = TextField(null=True)


class PizzaAdmin(ModelAdmin):
    columns: ('name')


admin.register(Pizzas, PizzaAdmin)
admin.setup()


class UserRegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=6, max=20)])
    email = EmailField('E-mail',
                       validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=32)])
    confirm_password = PasswordField('Confirm password',
                                     validators=[DataRequired(), EqualTo('password')])


class CreatePizzaForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    ingredients = StringField('Ingredients', validators=[DataRequired()])
    size = FF('Size', validators=[DataRequired()])
    price = FF('Price', validators=[DataRequired()])


class CreatePizzaForm(FlaskForm):
    name = StringField('Name')
    price = FloatField('Price')
    ingredients = StringField('Ingredients')
    size = FloatField('Size')


@app.route('/')
def home():
    pizzas = Pizzas.select()
    return flask.render_template('home.html', pizzas=pizzas)


@app.route('/get_pizza/<int:id>')
def get_pizza(id):
    pizza = Pizzas.get_by_id(id)
    return flask.render_template('get_pizza.html',
                                 pizza=pizza, pizza_id=id)


@app.route('/create_pizza', methods=['GET', 'POST'])
@auth.admin_required
def create_pizza():
    form = CreatePizzaForm()

    if flask.request.method == 'POST':
        name = flask.request.form.get('pizza_name')
        price = float(flask.request.form.get('price'))
        ingredients = flask.request.form.get('ingredients')
        size = int(flask.request.form.get('size'))

        if 'picture' in flask.request.files:
            file = flask.request.files['picture']
            filename = secure_filename(file.filename)
            filepath = os.path.abspath(app.root_path + '/static/' + filename)
            file.save(filepath)

            new_pizza = Pizzas(name=name, price=price,
                               ingredients=ingredients, size=size,
                               picture=filename)
            
        else:
            new_pizza = Pizzas(name=name, price=price,
                               ingredients=ingredients, size=size)
            
        new_pizza.save()
        flask.redirect(flask.url_for('home'))
            

    return flask.render_template('create_pizza.html',
                                 form=form)


@app.route('/buy_pizza', methods=['POST'])
@auth.login_required
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
@auth.login_required
def my_cart():
    if 'cart' in flask.session:
        cart = flask.session['cart']
    else:
        cart = []

    cart_pizzas = [Pizzas.get_by_id(i) for i in cart]
    return flask.render_template('my_cart.html', pizzas=cart_pizzas)


@app.route('/create_admin')
def create_admin():
    auth.User.create_table(fail_silently=True)
    admin = auth.User(username='admin', email='', admin=True, active=True)
    admin.set_password('admin')
    admin.save()

    return 'admin created'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = auth.User(username=username,
                         email=email,
                         admin=False, active=True)
        user.set_password(password)
        user.save()

        return flask.redirect(flask.url_for('home')) 

    return flask.render_template('register.html', form=form)


if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    Pizzas.create_table(fail_silently=True)
    app.run(debug=True)
