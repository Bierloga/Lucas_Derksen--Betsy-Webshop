import peewee
import os


db = peewee.SqliteDatabase("database.db")


class User(peewee.Model):
    name = peewee.CharField()
    address_data = peewee.CharField()
    billing_info = peewee.CharField()

    class Meta:
        database = db


class Tag(peewee.Model):
    value = peewee.CharField(unique=True)

    class Meta:
        database = db


class Product(peewee.Model):
    name = peewee.CharField()
    description = peewee.TextField()
    price_per_unit = peewee.IntegerField()
    stock = peewee.IntegerField()
    owner = peewee.ForeignKeyField(User)
    tags = peewee.ManyToManyField(Tag)

    class Meta:
        database = db


class Transaction(peewee.Model):
    buyer = peewee.ForeignKeyField(User)
    product = peewee.ForeignKeyField(Product)
    quantity_bought = peewee.IntegerField()

    class Meta:
        database = db


Product_Tag = Product.tags.get_through_model()

# In order to check my functions in main.py, I populated the database with some mock data.
# To initialize, call create_mock_data()


def create_mock_data():
    if os.path.exists("database.db"):
        os.remove("database.db")
    db.connect()
    db.create_tables([User, Tag, Product, Transaction, Product_Tag])
    sweater_owner, _ = User.get_or_create(
        name="Tom", address_data="Hogeweg 15, Velp", billing_info="IBAN0123120512"
    )
    sweater_tag1, _ = Tag.get_or_create(value="Fluffy")
    sweater_tag2, _ = Tag.get_or_create(value="Clothing")
    sweater_tag3, _ = Tag.get_or_create(value="Warm")
    sweater = Product.create(
        name="Warm Sweater",
        description="Very comfy sweater to keep you warm on cold nights!",
        price_per_unit=5,
        stock=4,
        owner=sweater_owner,
    )
    sweater.tags.add([sweater_tag1, sweater_tag2, sweater_tag3])
    knife_owner, _ = User.get_or_create(
        name="Sara",
        address_data="Lagestraat 32A, Groesbeek",
        billing_info="IBAN05888812",
    )
    knife_tag1, _ = Tag.get_or_create(value="Metal")
    knife_tag2, _ = Tag.get_or_create(value="Sharp")
    knife_tag3, _ = Tag.get_or_create(value="Professional")
    knife = Product.create(
        name="Knife",
        description="Beef, vegetables or burglars? It can handle anything!",
        price_per_unit=50,
        stock=5,
        owner=knife_owner,
    )
    knife.tags.add([knife_tag1, knife_tag2, knife_tag3])
    car_owner, _ = User.get_or_create(
        name="Henk",
        address_data="Benedenlaan 22, Amsterdam",
        billing_info="IBAN88899785",
    )
    car_tag1, _ = Tag.get_or_create(value="Reliable")
    car_tag2, _ = Tag.get_or_create(value="Toyota")
    car_tag3, _ = Tag.get_or_create(value="Red")
    car = Product.create(
        name="Car",
        description="Has always belonged to an old lady",
        price_per_unit=1000,
        stock=1,
        owner=car_owner,
    )
    car.tags.add([car_tag1, car_tag2, car_tag3])
    sweater2_owner = User.get(User.name == "Henk")
    sweater2_tag1, _ = Tag.get_or_create(value="Red")
    sweater2_tag2, _ = Tag.get_or_create(value="Clothing")
    sweater2_tag3, _ = Tag.get_or_create(value="Cotton")
    sweater2 = Product.create(
        name="Red Sweater",
        description="Ugly red doesn't exist!",
        price_per_unit=30,
        stock=3,
        owner=sweater2_owner,
    )
    sweater2.tags.add([sweater2_tag1, sweater2_tag2, sweater2_tag3])
    db.close()
    print("Database succesfully filled with mock data!")
