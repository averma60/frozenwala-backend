from django.db import models
from ckeditor.fields import RichTextField


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    title=models.CharField(max_length=500)
    description = RichTextField()
    item_photo = models.ImageField(upload_to='item_photos/')
    # item_quantity = models.PositiveIntegerField()
    # item_measurement=models.CharField(max_length=10, default='')
    non_veg = models.BooleanField(default=False)
    item_old_price = models.FloatField()
    makingprice = models.FloatField()
    discount = models.IntegerField()
    item_new_price = models.FloatField()
    status= models.BooleanField(default=True)
    veg=models.CharField(max_length=10,default='1')
    category = models.ForeignKey("ecomApp.Catagory", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deal_of_the_day = models.BooleanField(default=False)
    recommended = models.BooleanField(default=False)
    most_popular = models.BooleanField(default=False)
    brand_name = models.CharField(max_length=155, default=None, null=True, blank=True)

    def __str__(self):
        return f"Item ID: {self.id}, Category: {self.category.name}"
    
class ItemImage(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    media_file = models.FileField(upload_to='item_media/', null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    image_path = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_item_images'   # Matches your MySQL table name

    def __str__(self):
        return f"{self.media_type.capitalize()} {self.id} for Item {self.item.id}"
    
class ItemReview(models.Model):
    user = models.ForeignKey("ecomApp.CustomUser", on_delete=models.CASCADE)
    item = models.ForeignKey("menu_management.Item", on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(default=1)   # 1–5
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_item_reviews"
        unique_together = ('user', 'item')   # Each user gives 1 review per item

    def __str__(self):
        return f"{self.user.phone_number} - {self.rating}★ - Item {self.item.id}"
    
class ItemHighlights(models.Model):
    item = models.OneToOneField('menu_management.Item', on_delete=models.CASCADE)

    recommended = models.BooleanField(default=False)
    popular_item = models.BooleanField(default=False)
    deals_of_the_day = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Highlights for {self.item.name}"

class MenuSettings(models.Model):
    show_out_of_stock = models.BooleanField(
        default=True,
        help_text="Show out of stock products on the app/website"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Menu Settings"
