from django.db import models
from ckeditor.fields import RichTextField


class News(models.Model):
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title