from rest_framework import serializers
from myapp.models import User,Blog

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'birthdate',  'password']
        extra_kwargs={
            'password':{'write_only':True},
            'firstname':{'required':False},
            'birthdate':{'required':False},
            'lastname':{'required':False},
            
        }
    
    def create(self, validate_data):
        user = User.objects.create(
            firstname=validate_data['firstname'],
            lastname=validate_data['lastname'],
            email=validate_data['email'],
            birthdate=validate_data['birthdate'],
           
           
        )
    
        user.set_password(validate_data['password'])
        user.save()
        
        return user

class LoginSerializer(serializers.ModelSerializer):
    ''' User Login by email and password '''
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'birthdate' ]


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=255, write_only=True, style={'input_type':'password'})
    new_password2 = serializers.CharField(max_length=255, write_only=True, style={'input_type':'password'})

    class Meta:
        fields = ['new_password', 'new_password2']

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password2 = attrs.get('new_password2')
        user = self.context.get('user')
        if new_password != new_password2:
            raise serializers.ValidationError("Password and Confirm Password Doesn't Match")
        user.set_password(new_password)
        user.save()
        return attrs

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id','blog','comment']
        extra_kwargs = {
            "user":{'write_only':True},
            'blog':{'required':False},
            'comment':{'required':False},
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Blog.objects.create(**validated_data)