import email
from django.shortcuts import render
from django.http.response import Http404, HttpResponse
from .models import Blog, User

from django.urls import reverse
from django.template import loader
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from myapp.serializers import RegisterSerializer,LoginSerializer,ProfileSerializer,ChangePasswordSerializer,BlogSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from datetime import date, datetime as dt, timedelta
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password

# Create your views here.
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh)
,
      'access': str(refresh.access_token),
  }

  # User Registration Api Code start #
class UserRegistrationView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)#
        if serializer.is_valid(raise_exception=False):
            user = serializer.save()
            token = get_tokens_for_user(user)
            user = User.objects.get(email=user)
            birthdate = ''
            
            
           

            if user.birthdate != '':
                birthdate = user.birthdate
            else:
                birthdate = "null"

           
            
            User_data = {
                'id':user.id,
                'firstname':user.firstname,
                'lastname':user.lastname,
                'email':user.email,
                'birthdate':birthdate,
               
                'access_token':token.get('access'),
                'refresh_token':token.get('refresh')
            }
            return render(request, "register.html", {"message":"register Successfully.","data":User_data})
        else:
            return render(request, "register.html", {"message":"Password and email cannot be blank."})
# User Registration Api Code End #

# User Login Api Code Start #
class UserLoginView(APIView):
    # renderer_classes = [UserRenderer]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                try:
                    user = User.objects.get(email=serializer.data.get('email'))
                except User.DoesNotExist:
                    return Response({"status":"false", "message":"User Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)

  
      

                User_data = {
                    'id':user.id,
                    'email':user.email,
                    'access_token':token.get('access'),
                    'refresh_token':token.get('refresh')
                }
                return HttpResponseRedirect("/blog/",{"data":User_data})
        else:
            return render(request, "reset_password.html", {"message":"Password and email cannot be blank."})
# User Login Api Code End #


# User Profile API Code Start #
class ProfileView(APIView):
    # renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
   
    def put(self, request, format=None):
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({"status":"false", "message":"User Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            profile = User.objects.get(id=user)
        except User.DoesNotExist:
            return Response({"status":"false", "message":"profile Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return render(request, "register.html", {"message":"register Successfully."})
        else:
            return render(request, "register.html", {"message":"Password and email cannot be blank."})
# User Profile API Code End #


# User Change Password Code Start #
class UserChangePasswordView(APIView):
    # renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'status':'true', 'message':'Password Changed Successfully'}, status=status.HTTP_200_OK)
        return Response({'status':'false', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
# User Change Password Code End #

# User Reset / Forgot Password API Start #
class ResetPassword(APIView):
   
    
    # User Redirect to Reset Form. #
    def get(self, request):
        uid = request.query_params.get("uid")
        user_data = urlsafe_base64_decode(uid)
        user_data = eval(user_data)
        expire = dt.strptime(str(user_data["expire"]), "%Y-%m-%d").date()
        if dt.now().date() <= expire:
            user = user_data["user"]
            return render(request, "reset_password.html", {"user":user, "message":""})
        else:
            return render(request, "reset_password.html", {"message":"Reset Token Expiered."})  

# Reset Password Post Method #
def confirm(request):
    if request.method == "POST":
        if request.POST.get("password") != "" and request.POST.get("password2") != "":
            if request.POST["new_password"] == request.POST.get("new_password2"):
                user = User.objects.filter(email=str(request.POST.get("user")))
                if user == []:
                    return render(request, "reset_password.html", {"message":"user not found."})
                password = make_password(request.POST.get("password"))
                user.update(password=password)
                return render(request, "reset_password.html", {"message":"Password Successfully Reset."})
            else:
                return render(request, "reset_password.html", {"message":"Password and Re-password doesn't match."})
        else:
            return render(request, "reset_password.html", {"message":"Password and Re-password cannot be blank."})
# User Reset / Forgot Password API End #


class BlogCreate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        serializer = BlogSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
           
            return Response({"status":True, "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
           
            return Response({"status":False, "data":serializer.error}, status=status.HTTP_400_BAD_REQUEST)

class BlogDetailView(APIView):
    permission_classes = [IsAuthenticated]
        
    def get(self, request,pk, format=None):
        
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            blog = Blog.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'blog data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BlogSerializer(blog)
        return Response({"status":True, "message":"fetch data successfuly", "data":serializer.data}, status=status.HTTP_200_OK)

    def put(self,request,pk,format=None):
        
        try:
            user = User.objects.get(email=str(request.user)).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"user doesnot exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            blog = Blog.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'blog data not found'}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = BlogSerializer(blog,data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response({"status":True, "message":"Update  Successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
           return Response({"status":False,  "message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)  

    def delete(self,request,pk):
       
        try:
            user = User.objects.get(email=str(request.user)).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        try:
            blog = Blog.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'blog data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        blog.delete()
        return Response({"status":True, "message":"data was successfully delete"}, status=status.HTTP_200_OK) 
        


        

        
        
   