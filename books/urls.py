from django.urls import re_path
from .views import *



urlpatterns = [

    re_path(r'^register/user/', RegisterUserViewSet.as_view(), name='Api to register new users'),
    re_path(r'^login/user/', CheckValidUser.as_view(), name='Api to check the user is valid'),
    re_path(r'^list/', BooksListViewSet.as_view(), name='Api to list pr create books'),
    re_path(r'^(?P<book_id>[\w|\W]+)/details/$', BooksDetailsViewSet.as_view(), name='Api to list details of a purticular book'),
    re_path(r'^(?P<user_id>[\w|\W]+)/borrow/$', BorrowedBooksViewSet.as_view(), name='Api to list borrowed books and book borrowing by a by user'),
    re_path(r'^(?P<user_id>[\w|\W]+)/return/$', ReturnBooksViewSet.as_view(), name='Api to return a borrowed book book'),

]