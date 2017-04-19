import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.

def generate_unique_file_name(instance, filename):
    ext_name = filename.split('.')[-1]
    file_name = '{}.{}'.format(uuid.uuid4(), ext_name)
    return os.path.join('images', file_name)


class Supplier(models.Model):
    """
    Fields-
    1. supplier_id- Supplier identifier
    2. supplier_name- Supplier name
    3. point_of_contact- Person to contact (Company representative)
    4. Foreign Keys:
    Relationships-
    1. Ternary Relationship with Supplier, Order, and Item
    """
    supplier_name = models.CharField(max_length=40)
    point_of_contact = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return 'Supplier- {}'.format(self.supplier_name)


def order_quantity_validator(order_quantity):
    # Cannot have an empty order
    if order_quantity <= 0:
        raise ValidationError("Must order at least one item")


class Order(models.Model):
    """
    Fields-
    1. order_id- Order identifier
    2. date_ordered- Date when items were ordered
    3. date_fulfilled- Date when items were received
    4. order_quantity- Number of items ordered
    5. Foreign Keys:
    Relationships-
    1. Ternary Relationship with Supplier, Order, and Item
    """
    date_ordered = models.DateField(auto_now=True)
    date_fulfilled = models.DateField(blank=True)
    order_quantity = models.IntegerField(default=1, validators=[order_quantity_validator])

    def __str__(self):
        return 'Order #{}'.format(self.id)


class SellingOrder(models.Model):
    """
    Fields-
    1. supplier_order_id- Order from supplier Identifier
    2. Foreign Key:
    Relationship-
    1. One to Many with Supplier                            --In This Model
    2. One to Many with Order                               --In This Model
    3. One to Many with Item                                --In This Model
    Note: The Foreign Keys are set to 'Protect' so that if a valid reference
    exists, it won't change the references to null. We will have a record
    of which suppliers supplied what items on which days.
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    item = models.ForeignKey('Crate.Item', related_name='item_id_sold_by', on_delete=models.PROTECT)

    def __str__(self):
        return 'SellingOrder- Supplier:{}, Order #{}, Item: {}'.format(self.supplier, self.order, self.item)


class Category(models.Model):
    """
    Fields-
    1. category_name- Name of the category
    2. category_description- Description
    3. category_image- Image of category
    4. Foreign Keys:
    Relationships-
    1. One to Many with Subcategory                         --In 'Subcategory' Model
    """
    category_name = models.CharField(max_length=20, primary_key=True)
    category_description = models.CharField(max_length=100, blank=True)
    category_image = models.ImageField(upload_to=generate_unique_file_name, blank=True)

    def __str__(self):
        return 'Category- {}'.format(self.category_name)


class SubCategory(models.Model):
    """
    1. subcategory_name- Name of the subcategory
    2. category_name- Name of the category that holds this subcategory
    3. subcategory_description- Description
    4. subcategory_image- Subcategory Image
    5. Foreign Keys:
    Relationships-
    1. One to Many with Category                            --In This Model
    2. One to Many with Interest Group                      --In This Model
    Note: Foreign Key is set to Protect so that the Category should never be deleted
    """
    subcategory_name = models.CharField(max_length=30, primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    subcategory_description = models.CharField(max_length=100, blank=True)
    subcategory_image = models.ImageField(upload_to=generate_unique_file_name, blank=True)

    def __str__(self):
        return 'Subcategory- {}'.format(self.subcategory_name)


class InterestGroup(models.Model):
    """
    Fields-
    1. interest_id- Primary key (Identifier) of Interest Group
    2. interest_group_name- Name of the interest_group
    3. subscription_cost- Monthly price of a box
    4. interest_group_description- Description
    5. Foreign Keys:
    Relationships-
    1. Many to Many with User                           --In 'User' Model
    2. One to Many with Discussion                      --In 'Discussion' Model
    3. One to Many with Subcategory                     --In This Model
    4. Many to Many with Item                           --In this Model
    5. Many to One with Box                             --In 'Box' Model
    Note: Foreign Key is set to Protect so that Subcategory should never be deleted
    """
    interest_group_name = models.CharField(max_length=30)
    subscription_cost = models.DecimalField(max_digits=6, decimal_places=2)
    interest_group_description = models.CharField(max_length=100, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    have = models.ManyToManyField('Crate.Item', blank=True)
    interest_group_image = models.ImageField(upload_to=generate_unique_file_name, blank=True)

    def __str__(self):
        return 'Interest Group- {}'.format(self.interest_group_name)


def positive_vote_validator(score):
    # Forces score to be >= 0
    if score < 0:
        return ValidationError("Vote Score cannot be negative")


class Vote(models.Model):
    """
    Fields-
    1. item_id- Identifier of item which is being voted on
    2. selling_cycle- Identifier of which cycle the item is being sold in
    3. vote_score- Number of votes for the give item in the given cycle
    4. Foreign Keys:
    Relationships-
    1. One to Many with Item                        --In This Model
    2. One to Many with Selling Cycle               --In This Model
    """
    item = models.ForeignKey('Crate.Item', on_delete=models.PROTECT)
    selling_cycle = models.ForeignKey('Crate.SellingCycle', on_delete=models.PROTECT)
    vote_score = models.IntegerField(default=0, validators=[positive_vote_validator])

    # Gives guarantee that an item in two selling cycles can be voted on
    class Meta:
        unique_together = ('item', 'selling_cycle')

    def __str__(self):
        return 'Votes- Item: {}, Selling Cycle: {}'.format(self.item, self.selling_cycle)


def validate_month_start(date):
    # Forces the start date for a selling cycle to be at the start of the month
    if date.day != 1:
        raise ValidationError("Selling Cycle must be at the start of the month.")


class SellingCycle(models.Model):
    """
    Fields-
    1. cycle_date- Date (Start of month for the cycle
    2. Foreign Keys:
    Relationships-
    1. One to Many with Box                         --In 'Box' Model
    2. Many to Many with Item                       --In 'Item' Model
    """
    cycle_date = models.DateField(primary_key=True, validators=[validate_month_start])

    def __str__(self):
        return 'Selling Cycle- {}'.format(self.cycle_date)


class Box(models.Model):
    """
    Fields-
    1. id = models.AutoField(primary_key=True) is created by default
    2. 4 Foreign Keys to the Tables
    models.ForeignKey(<Model>, on_delete=models.ON_CASCADE)
    Relationships-
    1. Many to Many with User                       --In 'UserProfile' Model
    2. Many to One with Selling Cycle               --In This Model
    3. Many to Many with Items                      --In 'Item' Model
    4. Many to One with Interest Groups             --In This Model
    """
    sold_during = models.ForeignKey(SellingCycle, on_delete=models.PROTECT)
    type = models.ForeignKey(InterestGroup, on_delete=models.PROTECT)

    # Guarantees that a box for a interest group is unique for every selling cycle
    class Meta:
        unique_together = ('sold_during', 'type')

    def __str__(self):
        return 'Box #{} {} {}'.format(self.id, str(self.type), str(self.sold_during))


def positive_quantity_validator(quantity):
    # Quantity must be positive
    if quantity < 0:
        raise ValidationError("Quantity must be non-negative")


class Item(models.Model):
    """
    Fields-
    1. id = models.AutoField(primary_key=True) is created by default
    2. item_name- Name of item (String)
    3. item_Description- Description of the item (String)
    4. item_quantity- Number of items in stock (Integer)
    5. price_per_item- Price to sell an item (Decimal)
    6. Foreign Keys:
    Relationships-
    Many to Many with Interest Group                --In 'Interest_Group' Model
    Many to Many with Box                           --In This Model
    Ternary Relationship with Supplier and Orders   --In This Model
    """
    item_name = models.CharField(max_length=40)
    item_description = models.CharField(max_length=500, blank=True)
    item_quantity = models.IntegerField(default=0, validators=[positive_quantity_validator])
    price_per_item = models.DecimalField(max_digits=6, decimal_places=2)
    contained_in = models.ManyToManyField(Box, blank=True)
    sold_by = models.ManyToManyField(Supplier, through=SellingOrder, blank=True)

    def __str__(self):
        return 'Item- {}'.format(self.item_name)
