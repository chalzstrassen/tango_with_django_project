from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Category(models.Model):
    
    name=models.CharField(max_length=128,unique=True,validators=[RegexValidator(regex='^\S+')])
    views=models.IntegerField(default=0)
    likes=models.IntegerField(default=0)
    slug=models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super(Category,self).save(*args,**kwargs)
    
class Page(models.Model):
    category=models.ForeignKey(Category)
    title=models.CharField(max_length=128)
    url=models.URLField()
    views=models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    
    def __str__(self):
        return self.user.username
    
