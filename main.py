import models
from rich.table import Table
from rich.console import Console


__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"


def search(term):
    if isinstance(term, str) is False:
        raise ValueError("You can only search for strings!")
    else:
        table = Table(title="Search Results:")
        table.add_column("Product name", style="cyan")
        table.add_column("Price per unit", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Quantity", style="yellow")
        table.add_column("Tags", style="cyan")
        query = models.Product.select().where(models.Product.name.contains(term))
        for item in query:
            new_list = []
            for group in item.tags:
                new_list.append(group.value)
            tag_list = ", ".join(new_list)
            table.add_row(
                item.name,
                str(item.price_per_unit),
                item.description,
                str(item.stock),
                str(tag_list),
            )
        console = Console()
        console.print(table)


def list_user_products(user_id):
    if isinstance(user_id, int) is False:
        raise ValueError("Please provide valid user_id")
    query = models.Product.select().where(models.Product.owner == user_id)
    if len(list(query)) < 1:
        raise ValueError("No products were found for this id")
    username = models.User.get(models.User.id == user_id)
    table = Table(title=f"Products for user {username.name}")
    table.add_column("Product name", style="cyan")
    table.add_column("Price per unit", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Quantity", style="yellow")
    table.add_column("Tags", style="cyan")
    for item in query:
        new_list = []
        for group in item.tags:
            new_list.append(group.value)
        tag_list = ", ".join(new_list)
        table.add_row(
            item.name,
            str(item.price_per_unit),
            item.description,
            str(item.stock),
            str(tag_list),
        )
    console = Console()
    console.print(table)


""" Regarding list_product_per_tag(): The assignment specifies you have to show the items belonging to a certain tag, but the pre-made function
below didn't take a tag but the id of a tag as input. I chose to follow the assignment, since in the real world, users
will not look up the id's of tags, but enter an actual tag in a search field or something like that. """


def list_products_per_tag(tag):
    if isinstance(tag, str) is False:
        raise ValueError("Please provide valid tag")
    exists = models.Tag.select().where(models.Tag.value == tag)
    if len(list(exists)) < 1:
        raise ValueError("No products were found for this id")
    table = Table(title=f"Products for tag: {tag}")
    table.add_column("Product name", style="cyan")
    table.add_column("Price per unit", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Quantity", style="yellow")
    tag = models.Tag.get(models.Tag.value == tag)
    tag_id = tag.id
    query = models.Product.select()
    for item in query:
        for element in item.tags:
            if element.id == tag_id:
                table.add_row(
                    item.name,
                    str(item.price_per_unit),
                    item.description,
                    str(item.stock),
                )
    console = Console()
    console.print(table)


"""Again some ambiguity in the assignment. Do I have to add a new product to the catalog like the function name
suggests, or do I have to add an existing product to a user? I chose the first option. """

"""I'm assuming there would be an inputfield on a page somewhere, where on submit the product info would be sent
in the form of a Dictionary. so product would need to get something like this: 
{"name": TV, "description": "Only shows black&white", "price": 4, "stock": 3, "tags": ["Philips", "Damaged", "Electronics"]}"""


def add_product_to_catalog(user_id, product):
    if isinstance(user_id, int) is False:
        raise ValueError("Please provide valid user_id")
    if isinstance(product, dict) is False:
        raise ValueError("No correct dict could be processed")
    query = models.User.select().where(models.User.id == user_id)
    if len(list(query)) < 1:
        raise ValueError("This user was not found")
    user = models.User.get(models.User.id == user_id)
    new_product, _ = models.Product.get_or_create(
        name=product["name"],
        owner=user,
        description=product["description"],
        price_per_unit=product["price"],
        stock=product["stock"],
    )
    for item in product["tags"]:
        new_item, _ = models.Tag.get_or_create(value=item)
        new_product.tags.add(new_item)
    print("New Item added to catalog!")


def update_stock(product_id, new_quantity):
    if isinstance(product_id, int) is False:
        raise ValueError("Please provide valid product_id")
    if isinstance(new_quantity, int) is False:
        raise ValueError("Please provide proper value for new quantity")
    does_exist = models.Product.select().where(models.Product.id == product_id)
    if len(list(does_exist)) < 1:
        raise ValueError("No product was found for this id")
    product = models.Product.get(models.Product.id == product_id)
    product.stock = new_quantity
    product.save()
    print(f"Stock of {product.name} was updated to {new_quantity} for seller")


def remove_product(product_id):
    product = models.Product.get(models.Product.id == product_id)
    product.delete_instance()
    print("Product was removed from database")


def purchase_product(product_id, buyer_id, quantity):
    product = models.Product.get(models.Product.id == product_id)
    new_owner = models.User.get(models.User.id == buyer_id)
    products_owned = models.Product.select().where(product.name == models.Product.name)
    # Check if the item isn't already owned by the buyer
    if product.owner.name == new_owner.name:
        raise ValueError("You can't buy your own item!")
    # If you try to buy more than is in stock
    if product.stock < quantity:
        raise ValueError("You can't buy more items than are in stock!")
    # If you try to buy less than is in stock
    elif product.stock > quantity:
        # If the buyer already owns the same kind of product
        if len(list(products_owned)) > 0:
            product_already = models.Product.get(product.name == models.Product.name)
            new_quantity = product_already.stock - quantity
            update_stock(product_already.id, new_quantity)
            models.Transaction.create(
                buyer=new_owner, quantity_bought=quantity, product=product
            )
        # If the buyer doesn't already own this kind of product
        else:
            new_quantity = product.stock - quantity
            update_stock(product_id, new_quantity)
            copied_product = models.Product.create(
                name=product.name,
                description=product.description,
                owner=new_owner,
                price_per_unit=product.price_per_unit,
                stock=quantity,
            )
            for item in product.tags:
                copied_product.tags.add(item)
            models.Transaction.create(
                buyer=new_owner, quantity_bought=quantity, product=copied_product
            )
            print("Product added to new owner!")
    # If you try to buy the whole stock
    elif product.stock == quantity:
        # If the buyer already owns the same kind of product
        if len(list(products_owned)) > 0:
            product_already = models.Product.get(product.name == models.Product.name)
            new_quantity = product_already.stock - quantity
            update_stock(product_already.id, new_quantity)
            remove_product(product_id)
            print(f"Product is now out of stock for {product.owner.name}.")
            models.Transaction.create(
                buyer=new_owner, quantity_bought=quantity, product=product
            )
        # If the buyer doesn't already own the same kind of product
        else:
            update_stock(product_id, 0)
            remove_product(product_id)
            print(f"Product is now out of stock for {product.owner.name}.")
            copied_product = models.Product.create(
                name=product.name,
                description=product.description,
                owner=new_owner,
                price_per_unit=product.price_per_unit,
                stock=quantity,
            )
            for item in product.tags:
                copied_product.tags.add(item)
            models.Transaction.create(
                buyer=new_owner, quantity_bought=quantity, product=copied_product
            )
            print("Product added to new owner!")
    print(
        f"{product.name} was sold from user {product.owner.name} to user {new_owner.name}"
    )
    # If the stock of the item is now 0, it will be deleted from the database.
    if product.stock == 0:
        remove_product(product.id)
        print(
            f"Product is now out of stock for {product.owner.name} and therefore this item will be deleted."
        )


def show_transaction_table():
    table = Table(title="Transactions")
    table.add_column("Buyer_id", style="cyan")
    table.add_column("Buyer name", style="green")
    table.add_column("Product_id", style="magenta")
    table.add_column("Product name", style="cyan")
    table.add_column("Quantity bought", style="green")
    query = models.Transaction.select()
    if len(list(query)) < 1:
        raise ValueError("No transaction data to display!")
    for item in query:
        table.add_row(
            str(item.buyer.id),
            item.buyer.name,
            str(item.product.id),
            item.product.name,
            str(item.quantity_bought),
        )
    console = Console()
    console.print(table)
