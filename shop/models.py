from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.


class Category(MPTTModel):
    """Category model. """
    name = models.CharField(max_length=50, verbose_name='category')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model."""
    name = models.CharField(max_length=128, verbose_name='product')
    slug = models.SlugField(max_length=128, unique=True, verbose_name='URL')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    new_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    brand = models.CharField(max_length=50, verbose_name='brand')
    in_stock = models.BooleanField(default=False)
    quantity = models.PositiveSmallIntegerField(default=0)
    discount = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(99)], help_text='%')
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail_product', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = 'products'


def path_to_images(instance, filename):
    return 'images/{0}/{1}/{2}'.format(instance.product.category, instance.product.slug, filename)


class ImagesProduct(models.Model):
    """Images for product model."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=path_to_images)

    def __str__(self):
        return self.image

    class Meta:
        verbose_name_plural = 'images'
        ordering = ('product',)


