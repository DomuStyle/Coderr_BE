# standard bib imports
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# third party imports
from rest_framework import serializers

class RegistrationSerializer(serializers.ModelSerializer):

    repeated_password = serializers.CharField(write_only=True)
    # maps 'username' field to 'fullname' for a better user-friendly representation
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User # specifies that this serializer is based on the User model
        fields = ['fullname', 'email', 'password', 'repeated_password'] # defines the fields to be included
        extra_kwargs = {
            'password': {
                'write_only': True # ensures the password is not included in response data
            }
        }

    # check if passwords match
    def save(self):
        # extract validated data for password, repeated password, email, and username
        fullname = self. validated_data['username']
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        email = self.validated_data['email']
        username = self.validated_data['username']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error: passwords dont match'})
        
        # ensure that the email is not already registered
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': "This email address already exists."})
        
        # split full name into first and last_name
        name_parts = fullname.strip().split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # create a new user instance with the provided email and username
        account = User(email=self.validated_data['email'],
                       username=self.validated_data['username'],
                       first_name=first_name,
                       last_name=last_name)
        
        # hash the password before saving to ensure security
        account.set_password(pw)
        account.save()  # save the user to the database
        
        return account  # return the newly created user instance
    

class CustomAuthTokenSerializer(serializers.Serializer):
    # defines an email field to be used for authentication
    email = serializers.EmailField()
    
    # defines a password field with styling to hide input characters
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False  # ensures that spaces in the password are not automatically removed
    )

    def validate(self, attrs):
        # retrieves email and password from the validated attributes
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                # tries to find a user with the given email address
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                # raises a validation error if no user with the provided email exists
                raise serializers.ValidationError("Invalid email or password.")

            # attempts to authenticate the user using the retrieved username and password
            user = authenticate(username=user_obj.username, password=password)

            if not user:
                # raises a validation error if authentication fails
                raise serializers.ValidationError("Invalid email or password.")
        else:
            # raises a validation error if either email or password is missing
            raise serializers.ValidationError("Both email and password are required.")

        # adds the authenticated user to the attributes and returns them
        attrs['user'] = user
        return attrs