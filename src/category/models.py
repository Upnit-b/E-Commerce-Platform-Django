from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    cat_image = models.ImageField(
        upload_to="photos/categories", blank=True, null=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    # function to provide navigation for category names in navbar
    def get_url(self):
        # take the url from store, products by category route so that user can be
        # redirected to products as per category on clicking the name
        return reverse("products_by_category", args=[self.slug])

    def __str__(self):
        return self.category_name

    # for getting the category name as slug and then not editing the slug independently
    # modifying save functionality to save the slug as per the category
    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)
