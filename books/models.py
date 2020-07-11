

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.


class BooksLibrary(models.Model):
    
    book_name = models.CharField(max_length=50)
    author_name = models.CharField(max_length=50)
    books_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.book_name

class UserProfile(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    borrowed_books = models.ManyToManyField(BooksLibrary, related_name="books_borrowed", blank=True) 
    borrowedDate = models.DateField(null=True, blank=True)
    returnDate = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name