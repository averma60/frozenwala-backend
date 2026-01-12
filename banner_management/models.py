from django.db import models

# Create your models here.
from django.db import models
from ecomApp.models import Catagory
# Create your models here.
class Banner(models.Model):
    id = models.AutoField(primary_key=True)
    title=models.CharField(max_length=500)
    description=models.CharField(max_length=1000)
    add_photo = models.ImageField(upload_to='add_photos/')
    status= models.BooleanField(default=True)
    category = models.ForeignKey(Catagory, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Item ID: {self.id}"