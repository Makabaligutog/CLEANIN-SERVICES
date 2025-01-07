from django import forms
from django.contrib.auth.models import User
from .models import Booking
from .models import ServiceReview
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Feedback

class ServiceReviewForm(forms.ModelForm):
    class Meta:
        model = ServiceReview
        fields = ['customer_name', 'message', 'photo', 'rating']
       
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        exclude = ['booking_id', 'status', 'user', 'created_at']
     
class BookingFormAdmin(forms.ModelForm):
    class Meta:
        model = Booking
        exclude = ['booking_id', 'user', 'created_at']
     



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']

class AdminSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active']  # Edit any fields you need
        widgets = {
            'is_active': forms.CheckboxInput(),  # Checkbox for active status
        }
        
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']