from django.shortcuts import render

from rest_framework import generics, viewsets, status, serializers, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from books.models import BooksLibrary, UserProfile

import datetime

# Create your views here.


class UserBasicDataSerializer(serializers.ModelSerializer):
	username = serializers.CharField(required=False, source='user.username')
	user_token = serializers.SerializerMethodField()

	def get_user_token(self, obj):
		try:
			token = Token.objects.get(user=obj.user)
			return token.key
		except:
			raise exceptions.ValidationError({'error':'Invalid Books Token'})

	class Meta:
		model = UserProfile
		fields = ('username', 'first_name', 'last_name', 'user_token')

# Register a user with email and password

class RegisterUserViewSet(APIView):
	
	def post(self, request):
		email = request.data.get('email', '')
		first_name = request.data.get('first_name', '')
		last_name = request.data.get('last_name', '')
		password = request.data.get('password', '')

		validated = True
		errors={}
		
		if not email:
			validated = False
			errors.update({'error': 'Email field is required'})

		if not password:
			validated = False
			errors.update({'error': 'Password field is required'})

		if not validated:
			return Response({'validated':False, 'errors':errors}, status=status.HTTP_400_BAD_REQUEST)
		
		# Create User and UserProfile
		user = User.objects.create(username=email)
		try:
			user.set_password(password)
			user.save()
			token = Token.objects.create(user=user)
			userprofile = UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name)
		except:
			user.delete()
			return Response({'error':'An error occured while registration'}, status=status.HTTP_400_BAD_REQUEST)
		
		return Response(UserBasicDataSerializer(userprofile).data, status=status.HTTP_200_OK)

#Login of a user

class CheckValidUser(APIView):

	def post(self, request):
		email = request.data.get('email', '')
		password = request.data.get('password', '')

		validated = True
		errors={}
		
		if not email:
			validated = False
			errors.update({'error': 'Email field is required'})

		if not password:
			validated = False
			errors.update({'error': 'Password field is required'})

		if not validated:
			return Response({'validated':False, 'errors':errors}, status=status.HTTP_400_BAD_REQUEST)

		auth_user = auth.authenticate(username=email, password=password)

		if not auth_user:
			return Response({'error': 'Invalid credentials given'}, status=status.HTTP_401_UNAUTHORIZED)
		else:
			user = User.objects.get(username=auth_user.username)
		userprofile = UserProfile.objects.get(user=user)

		return Response(UserBasicDataSerializer(userprofile).data, status=status.HTTP_200_OK)

# Books add, list, Update, Delete Views
class BooksListSerializer(serializers.ModelSerializer):
	class Meta:
		model = BooksLibrary
		fields = ('book_name', 'author_name', 'books_count', 'id')

class BooksDetailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = BooksLibrary
		fields = ('book_name', 'author_name', 'books_count', 'id', 'created_at')

class BooksListViewSet(generics.ListCreateAPIView):
	permission_classes = (IsAuthenticated,)
	queryset = BooksLibrary.objects.all()
	serializer_class = BooksListSerializer

class BooksDetailsViewSet(generics.ListCreateAPIView):
	permission_classes = (IsAuthenticated,)
	
	def get(self,request, book_id):

		book_details = get_object_or_404(BooksLibrary, id=book_id)

		return Response(BooksDetailsSerializer(book_details).data, status=status.HTTP_200_OK)

	def put(self, request, book_id):

		try:
			book_details = get_object_or_404(BooksLibrary, id=book_id)
		except:
			raise exceptions.ValidationError({'error':'Invalid Books Library'})

		if 'book_name' in request.data and request.data['book_name']:
			book_name = request.data['book_name']
		else:
			return Response({'error':'book_name field is required'}, status=status.HTTP_400_BAD_REQUEST)

		if 'author_name' in request.data and request.data['author_name']:
			author_name = request.data['author_name']
		else:
			return Response({'error':'author_name field is required'}, status=status.HTTP_400_BAD_REQUEST)

		if 'books_count' in request.data and request.data['books_count']:
			books_count = request.data['books_count']
		else:
			return Response({'error':'books_count field is required'}, status=status.HTTP_400_BAD_REQUEST)

		book_details.book_name = book_name
		book_details.author_name = author_name
		book_details.books_count = books_count
		book_details.save()

		return Response(BooksListSerializer(book_details).data, status.HTTP_200_OK)

	def delete(self, request, book_id):

		try:
			book_details = get_object_or_404(BooksLibrary, id=book_id)
		except:
			raise exceptions.ValidationError({'error':'Invalid Books Library'})

		book_details.delete()
		return Response({'status':'success'}, status=status.HTTP_200_OK)

# User borrow the number of books

class UserBorrowedBooksSerializer(serializers.ModelSerializer):
	borrowed_books = BooksListSerializer(many=True)
	class Meta:
		model = UserProfile
		fields = ('borrowed_books', 'borrowedDate')

class BorrowedBooksViewSet(generics.ListCreateAPIView):
	permission_classes = (IsAuthenticated,)
	serializer_class = UserBorrowedBooksSerializer
	queryset = BooksLibrary.objects.all()

	def get(self,request, user_id):

		try:
			userprofile = UserProfile.objects.get(id=user_id)
		except:
			raise exceptions.ValidationError({'error':'Invalid User'})

		return Response(UserBorrowedBooksSerializer(userprofile).data, status=status.HTTP_200_OK)


	def post(self, request, user_id):

		try:
			userprofile = UserProfile.objects.get(id=user_id)
		except:
			raise exceptions.ValidationError({'error':'Invalid User'})

		if 'books' in request.data and request.data['books']:
			books = request.data['books']
		else:
			return Response({'error':'books is required'}, status=status.HTTP_400_BAD_REQUEST)
		for book in books:
			try:
				borrowed_book = BooksLibrary.objects.get(id=book)
			except:
				raise exceptions.ValidationError({'error':'Invalid Book Id'})

			if borrowed_book.books_count != 0:
				borrowed_book.books_count -= 1
				borrowed_book.save()
				userprofile.borrowed_books.add(borrowed_book)
				userprofile.borrowedDate = datetime.date.today()
				userprofile.save()
			else:
				raise exceptions.ValidationError({'error': borrowed_book.book_name+' is not available '})

		return Response(UserBorrowedBooksSerializer(userprofile).data, status.HTTP_200_OK)

# User return the books

class ReturnBooksViewSet(generics.RetrieveUpdateAPIView):
	permission_classes = (IsAuthenticated,)
	serializer_class = UserBorrowedBooksSerializer
	queryset = BooksLibrary.objects.all()

	def patch(self, request, user_id):

		try:
			userprofile = UserProfile.objects.get(id=user_id)
		except:
			raise exceptions.ValidationError({'error':'Invalid User'})

		if 'book_id' in self.request.GET and self.request.GET['book_id']:
			book_id = self.request.GET['book_id']

			try:
				return_book = BooksLibrary.objects.get(id=book_id)
			except:
				raise exceptions.ValidationError({'error':'Invalid Book Id'})
		else:
			return Response({'error':'book id is required'}, status=status.HTTP_400_BAD_REQUEST)

		userprofile.borrowed_books.remove(return_book)
		userprofile.returnDate = datetime.date.today()
		userprofile.save()
		return_book.books_count += 1
		return_book.save()

		return Response(UserBorrowedBooksSerializer(userprofile).data, status.HTTP_200_OK)