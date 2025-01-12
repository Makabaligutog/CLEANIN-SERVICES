from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views import View
from .models import ServiceReview
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, DeleteView
from .models import Booking
from .forms import RegisterForm, BookingForm
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseForbidden
from .forms import ServiceReviewForm
from .forms import AdminSignupForm, AdminLoginForm
from .models import ServiceRating
from datetime import datetime
from .models import Service
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .forms import UserEditForm
from django.db.models import Count
from collections import defaultdict
import calendar
from django.http import HttpResponse
import re  
from datetime import date
import json
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from .forms import FeedbackForm  
from django.http import HttpResponseRedirect 
from .models import Feedback

def blog(request):
    reviews = ServiceReview.objects.all()
    return render(request, 'cleaning/Admin_blog.html', {'reviews': reviews})

def add_review(request):
    if request.method == 'POST':
        form = ServiceReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ad_blog')  # Redirect to the blog page or any other page
    else:
        form = ServiceReviewForm()
    
    return render(request, 'cleaning/Admin_blog.html', {'form': form})
# Home view
def home(request):
    feedbacks = Feedback.objects.all()
    # Render the landing page template and pass the feedbacks
    return render(request, 'cleaning/index.html', {'feedbacks': feedbacks})

   

# User Login View
def login_view(request):
    entered_username = ''
    if request.method == 'POST':
        entered_username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=entered_username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('u_home')
        else:
            messages.error(request, f'Invalid username or password for: {entered_username}')
    
    return render(request, 'cleaning/login.html')
#, {'entered_username': entered_username}
# User Registration View
def signup_view(request):
    print('signup submit')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        
        if pass1!=pass2:
            messages.error(request, 'Password did not Match! ')
            
                # Check if the username already exists
        if User.objects.filter(username=username).exists():
            print('This username is already taken.')
            messages.error(request, 'This username is already taken.')
                
            # form.add_error('username', 'This username is already taken.')
            return render(request, 'cleaning/register.html', {'form': form})
        
        

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            form.add_error('email', 'This email is already registered.')
            messages.error(request, 'This email is already registered.')

            return render(request, 'cleaning/register.html', {'form': form})
        
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            # If validation passes, save the user and log them in
            user = form.save()
            login(request, user)  # Log the user in after registration
            messages.success(request, 'Registration successful.')
            return redirect('login')  # Redirect to a relevant page (e.g., profile, home)
        else:
            print(form.errors)
    else:
        form = RegisterForm()
    return render(request, 'cleaning/register.html', {'form': form})

# Booking Creation View
# def create_booking(request):    
#     if request.method == 'POST':
#         form = BookingForm(request.POST)
        
#         if form.is_valid():
#             # Get the service that the user is trying to book
#             service = form.cleaned_data.get('service')  # Assuming 'service' is a field in your form
#             # Check if the user has already booked this service
#             if Booking.objects.filter(user=request.user, service=service).exists():
#                 messages.info(request, f"You have already booked the {service.name} service.")
#                 return redirect('cleaning/u-index.html')  # Redirect to the relevant page (e.g., user dashboard)
            
#             # If no existing booking, create the new booking
#             booking = form.save(commit=False)
#             booking.user = request.user  # Assign the current user to the booking
#             booking.save()

#             # If the request is an AJAX request, return a JSON response
#             if request.is_ajax():
#                 return JsonResponse({
#                     "message": "Booking created successfully!",
#                     "booking_id": str(booking.booking_id)
#                 }, status=201)

#             # For non-AJAX requests, redirect the user
#             messages.success(request, "Your booking has been successfully created!")
#             return redirect('cleaning/u-index.html')  # Change to the relevant page after booking

#         # If the form is not valid, return the user to the same page with errors
#         return redirect('cleaning/u-index.html')  # Or render with the form and errors if needed
@login_required
def create_booking(request):
    if request.method == "POST":
        
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        additional_info = request.POST.get('additional_info')
        booking_date = request.POST.get('booking_date')
        cleaning_service = request.POST.get('cleaning_service')

        # Validate required fields
        if not first_name or not last_name or not contact_number or not booking_date or not cleaning_service:
            return JsonResponse({"error": "Missing required fields. Please fill all required fields (First Name, Last Name, Contact Number, Booking Date, Cleaning Service)."}, status=400)

        # Validate booking date
        today = datetime.today().date()
        try:
            booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({"error": "Invalid booking date format. Please use YYYY-MM-DD."}, status=400)
        
        if Booking.objects.filter(user=request.user, status='approved').exists():
                return JsonResponse({"error": "You already have an active approved booking. Please cancel it before making a new one."}, status=400)

        
        if booking_date < today:
            return JsonResponse({"error": "Booking date cannot be in the past. Please select a valid future date."}, status=400)
        # Validate contact number format
        if not contact_number.isdigit() or len(contact_number) < 10 or len(contact_number) > 15:
            return JsonResponse({"error": "Please enter a valid contact number (10-15 digits)."}, status=400)
        
        if Booking.objects.filter(contact_number=contact_number).exists():
            return JsonResponse({"error": "This contact number is already used for a booking. Please use a different contact number."}, status=400)

        # **Prevent User from Making Multiple Bookings**
        # Check if the user already has a booking
        user = request.user
        existing_booking = Booking.objects.filter(user=user).exists()

        if existing_booking:
            return JsonResponse({"error": "You already have a booking. You cannot book again."}, status=400)

        # Check if the contact number or name is already booked for the selected date
        if Booking.objects.filter(booking_date=booking_date).exists():
            return JsonResponse({"error": "This date is already booked, Please choose a different date."}, status=400)

        if Booking.objects.filter(first_name=first_name, last_name=last_name, booking_date=booking_date).exists():
            return JsonResponse({"error": "This name is already associated with a booking on the selected date. Please choose a different name or date."}, status=400)
        
        

        # Validate cleaning service
        valid_services = [
            'residential', 'commercial', 'deep-cleaning', 'move-in-out', 'carpet-cleaning', 'upholstery-cleaning',
            'window-cleaning', 'eco-friendly', 'anti-bacterial-mist', 'car-interior-detailing', 'deep-dry-cleaning',
            'deep-home-cleaning', 'deep-upholstery-shampooing', 'steam-sterilization'
        ]
        if cleaning_service not in valid_services:
            return JsonResponse({"error": "Invalid cleaning service selected. Please choose a valid service."}, status=400)

        # Create the booking with the logged-in user
        try:
            booking = Booking(
                user=user,
                first_name=first_name,
                last_name=last_name,
                contact_number=contact_number,
                address=address,
                additional_info=additional_info,
                booking_date=booking_date,
                cleaning_service=cleaning_service
            )
            booking.save()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({"message": "Booking created successfully!"}, status=201)

    # If not POST request, return an error
    return JsonResponse({"error": "Invalid request method. Only POST is allowed."}, status=405)

class create_booking_views(View):
    def post(self, request):
        print('creating booking')
        try:
            form = BookingForm(request.POST)
            print(request.POST)
            if form.is_valid():
                newbooking = form.save(commit=False)
                newbooking.user = request.user
                newbooking.save()
                return JsonResponse({'success': "Successfuly saved Booking"}, status = 200)
            else:
                print(form.errors)
                return JsonResponse({'error': "Form invalid"}, status = 405)
        except Exception as e:
            return JsonResponse({'error': f'{e}'}, status = 500)
               
# User Profile View
@login_required
def profile_view(request):
    booking = Booking.objects.filter(user=request.user).first()
    return render(request, 'cleaning/user_profile.html', {'booking': booking})

# Update Booking View
from django.utils.timezone import now
@method_decorator(login_required, name='dispatch')
class BookingUpdateView(UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'cleaning/booking_update.html'
    success_url = reverse_lazy('user_profile')

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Validate booking_date is not in the past
        booking_date = form.cleaned_data.get('booking_date')
        if booking_date and booking_date < now().date():
            messages.error(self.request, "Booking date cannot be in the past.")
            return self.form_invalid(form)

        # Validate first_name
        first_name = form.cleaned_data.get('first_name')
        if not first_name.isalpha():
            messages.error(self.request, "First name must contain only alphabetic characters.")
            return self.form_invalid(form)

        # Validate last_name
        last_name = form.cleaned_data.get('last_name')
        if not last_name.isalpha():
            messages.error(self.request, "Last name must contain only alphabetic characters.")
            return self.form_invalid(form)

        # Validate contact_number
        contact_number = form.cleaned_data.get('contact_number')
        if not re.match(r'^\+?\d{7,15}$', contact_number):
            messages.error(self.request, "Enter a valid contact number (7-15 digits, with optional '+').")
            return self.form_invalid(form)

        # If all validations pass, proceed with saving
        response = super().form_valid(form)
        messages.success(self.request, "Your booking has been updated successfully!")
        return response

    # def form_invalid(self, form):
    #     # Optionally add a generic error message
    #     messages.error(self.request, "There was an error updating your booking. Please check the form.")
    #     return super().form_invalid(form)
    
# Delete Booking View
@method_decorator(login_required, name='dispatch')
class BookingDeleteView(DeleteView):
    model = Booking
    template_name = 'cleaning/booking_confirm_delete.html'
    success_url = reverse_lazy('user_profile')

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


# #user profile after mag book
# def profile_view(request):
#     # Fetch the user's latest booking, if any
#     booking = Booking.objects.filter(user=request.user).last()  # Get the most recent booking
#     return render(request, 'cleaning/user_profile.html', {'booking': booking})


# Admin Login View
def own_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('ad_dashboard')  # Redirect to the admin dashboard
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AdminLoginForm()

    return render(request, 'cleaning/admin_login.html', {'form': form})

# Admin Signup View
def own_signup(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Admin account created successfully.')
                return redirect('admin_signup')  # Redirect to the admin dashboard or any other page
            else:
                messages.error(request, 'Signup failed. Please try again.')
    else:
        form = AdminSignupForm()
    
    return render(request, 'cleaning/admin_signup.html', {'form': form})



#services ratings
def save_ratings(request):
    if request.method == "POST":
        for service, _ in ServiceRating.SERVICE_CHOICES:
            for month in [
                'January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December'
            ]:
                # Get the input value
                rating_key = f"ratings_{service}_{month}"
                rating_value = request.POST.get(rating_key)
                
                # If there's a value, proceed with save/update
                if rating_value:
                    rating_value = int(rating_value)  # Convert to integer
                    rating_obj, created = ServiceRating.objects.update_or_create(
                        service_name=service, 
                        month=month,
                        defaults={'rating': rating_value}
                    )
        # Redirect back to the ratings view
        return redirect('ratings')

    # If not POST, redirect to ratings page
    return redirect('ratings')

# Upload a services
def upload_service(request):
    if request.method == 'POST' and request.FILES['image']:
        name = request.POST['name']
        description = request.POST['description']
        image = request.FILES['image']

        # Use the model to handle file saving
        new_service = Service(
            name=name,
            description=description,
            image=image
        )
        new_service.save()

        return redirect('ad_services')  # Redirect to services page

    return render(request, 'cleaning/admin_services.html')

# User Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

def user_home(request):
    return render(request, 'cleaning/u-index.html')
# User Homepage

    
# User Services Page
def services(request):
    # Query the database for all booked dates
    booked_dates = Booking.objects.values_list('booking_date', flat=True)
    context = {
        'booked_dates': list(booked_dates)  # Convert QuerySet to a list for use in JS
    }
    return render(request, 'cleaning/u-services.html', context)
    

# User About Us Page
def about(request):
    return render(request, 'cleaning/u-about.html')

# User Blog Page
def blog(request):
    return render(request, 'cleaning/u-blog.html')

# Admin homepage
@login_required
def admin_home(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")
    bookings = Booking.objects.all()
    return render(request, 'cleaning/Admin_index.html', {'bookings': bookings})

#Anti bacterial in Services Learn More
def anti_bacterial(request):
    return render(request, 'cleaning/anti_bacterial.html')
# Admin ratings
from django.db.models import Count

def ratings_view(request):
    return render(request, 'cleaning/admin_dashboard_services.html')

# Admin services
def admin_services(request):
    services = Service.objects.all()
    return render(request, 'cleaning/admin_services.html', {'services': services})

def admin_about(request):
    return render(request, 'cleaning/admin_about.html')

def admin_blog(request):
    return render(request, 'cleaning/Admin_Blog.html')
   

# About Home Page
def about_home(request):
    return render(request, 'cleaning/about.html')

# Services Home Page
def services_home(request):
    return render(request, 'cleaning/services.html')

# Blog Home Page
def blog_home(request):
    return render(request, 'cleaning/blog.html')

#car interior
def car_interior(request):
    return render(request, 'cleaning/car_interior.html')

def deep_dry(request):
    return render(request, 'cleaning/deep_dry.html')

def deep_home(request):
    return render(request, 'cleaning/deep_home.html')

def deep_holstery(request):
    return render(request, 'cleaning/deep_holstery.html')


def sterilization(request):
    return render(request, 'cleaning/sterilization.html')

def residential_cleaning(request):
    return render(request, 'cleaning/residential.html')

def commercial_cleaning(request):
    return render(request, 'cleaning/commercial.html')

def move_in_cleaning(request):
    return render(request, 'cleaning/move_in.html')

def carpet_cleaning(request):
    return render(request, 'cleaning/carpet.html')

def window_cleaning(request):
    return render(request, 'cleaning/window.html')

#approved booking
@csrf_exempt
def approved(request):
     # Fetch bookings data from the database
    all_bookings = Booking.objects.all()  # Replace with appropriate queryset if necessary
    approved_bookings = Booking.objects.filter(status='approved')
    pending_bookings = Booking.objects.filter(status='pending')

    # Calculate totals
    total_bookings = all_bookings.count()
    approved_count = approved_bookings.count()
    pending_count = pending_bookings.count()

    # Prepare context
    context = {
        'bookings': all_bookings,            # Use this for the table
        'approved_bookings': approved_count, # Count of approved bookings
        'pending_bookings': pending_count,   # Count of pending bookings
        'total_bookings': total_bookings     # Total bookings
    }
    return render(request, 'cleaning/approved.html', context)

def approve_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=booking_id)
        booking.status = Booking.APPROVED  # Update to approved status
        booking.save()

        # Include the phone number in the response
        return JsonResponse({
            'success': True,
            'message': 'Booking approved successfully.',
            'phone_number': booking.contact_number  # Pass the contact number
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

#approve booking page sa mga na approve
def approved_bookings_view(request):
    approved_bookings = Booking.objects.filter(status='approved')  # Filter only approved bookings
    print(approved_bookings)
    context = {
        'bookings': approved_bookings,  # Pass the filtered bookings to the template
        'total_bookings': Booking.objects.count(),
        'approved_bookings': approved_bookings.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
    }
    return render(request, 'cleaning/approved_bookings.html', context)

def deny_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=booking_id)
        booking.status = Booking.DENIED  # Update to denied status
        booking.save()
        return JsonResponse({'success': True, 'message': 'Booking denied successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

#manage users in admin page
def manage_users(request):
    users = User.objects.all()
    if request.method == 'POST':
            # Handle Edit User
            if 'edit_user' in request.POST:
                user_id = request.POST.get('user_id')
                user = get_object_or_404(User, id=user_id)
                form = UserEditForm(request.POST, instance=user)
                if form.is_valid():
                    form.save()
                    messages.success(request, f"User {user.username} updated successfully.")
                else:
                    messages.error(request, "Error updating user.")
            
            # Handle Delete User
            if 'delete_user' in request.POST:
                user_id = request.POST.get('user_id')
                user = get_object_or_404(User, id=user_id)

                # Soft delete (deactivate) the user
                user.is_active = False
                user.save()
                messages.success(request, f"User {user.username} has been deactivated.")
            
            return redirect('manage_users')

    return render(request, 'cleaning/manage_users.html', {'users': users})

def edit_user(request, id):
    # Get the user object, or return 404 if it does not exist
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        # Retrieve new user data from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_active = request.POST.get('is_active') == 'on'  # Checkbox is either 'on' or None

        # Validate username
        if not username:
            messages.error(request, "Username cannot be empty.")
            return render(request, 'cleaning/admin_edit_profile.html', {'user': user})
        
        # Validate email
        if not email:
            messages.error(request, "Email cannot be empty.")
            return render(request, 'cleaning/admin_edit_profile.html', {'user': user})

        # You can add more email validation here if needed

        # Update user attributes if data is valid
        user.username = username
        user.email = email

        # Set active status; users created in the last 7 days will be active by default
        # This is where the logic for recent users comes into play
        if user.date_joined > timezone.now() - timedelta(days=7):
            user.is_active = True  # If the user was created recently, they are active by default
        else:
            user.is_active = is_active  # Otherwise, use the form value
        
        user.save()

        # Display a success message
        messages.success(request, f"User {user.username} updated successfully!")
        
        # Redirect to the manage users page after the update
        return redirect('user_manage')

    # Render the form to edit the user
    return render(request, 'cleaning/admin_edit_profile.html', {'user': user})
#highest rating sa services
def most_booked_service_view(request):
    # Query for all bookings
    bookings = Booking.objects.all()
    
    # Prepare data structure for monthly analysis
    monthly_data = defaultdict(lambda: defaultdict(int))
    
    for booking in bookings:
        month_name = calendar.month_name[booking.booking_date.month]  # Get month name
        monthly_data[month_name][booking.cleaning_service] += 1
    
    # Sort monthly data for display
    sorted_monthly_data = {
        month: dict(sorted(services.items(), key=lambda item: item[1], reverse=True))
        for month, services in sorted(monthly_data.items())
    }

    context = {
        'monthly_data': sorted_monthly_data
    }
    return render(request, 'cleaning/most_book_service.html', context)


#calendar bookmark
@login_required
def calendar_view(request):
    # Get the current year and month
    current_year = timezone.now().year
    current_month = timezone.now().month

    # Get the next month's year and month
    if current_month == 12:
        next_month = 1
        next_month_year = current_year + 1
    else:
        next_month = current_month + 1
        next_month_year = current_year

    # Get bookings for the current month and future months (including previous month for display)
    bookings = Booking.objects.filter(booking_date__year=current_year, booking_date__month=current_month)
    future_bookings = Booking.objects.filter(booking_date__gt=timezone.now())  # Get all future bookings

    # Get all bookings from the previous year
    last_year_bookings = Booking.objects.filter(
        booking_date__year=current_year - 1  # Get all bookings from the previous year
    )

    # Get all bookings for the previous month (for display in the next month)
    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = current_year

    # Get all bookings from last month (display them in the next month)
    last_month_bookings = Booking.objects.filter(
        booking_date__month=last_month,
        booking_date__year__lte=current_year  # This includes past bookings (even from last year)
    )

    # Create a dictionary with date as key (formatted as YYYY-MM-DD) and username as value
    booked_dates = {}

    # Add current month bookings
    for booking in bookings:
        booked_dates[str(booking.booking_date)] = booking.user.username

    # Add future bookings (upcoming months)
    for booking in future_bookings:
        booked_dates[str(booking.booking_date)] = booking.user.username

    # Add last year bookings (for previous months in this year)
    for booking in last_year_bookings:
        booked_dates[str(booking.booking_date)] = booking.user.username

    # Add last month bookings (displayed in next month)
    for booking in last_month_bookings:
        next_month_date = booking.booking_date.replace(year=next_month_year, month=next_month)
        booked_dates[str(next_month_date)] = booking.user.username

    # Pass the booked dates to the template
    return render(request, 'cleaning/calendar.html', {
        'booked_dates': booked_dates,
        'current_year': current_year,
        'current_month': current_month,
        'next_month': next_month,
        'next_month_year': next_month_year,
    })
#submit booking sa services
@login_required
@csrf_protect
def submit_booking(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            cleaning_service = request.POST.get('cleaning_service')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name', 'Unknown')
            contact_number = request.POST.get('contact_number')
            address = request.POST.get('address')
            additional_info = request.POST.get('additional_info', '')
            booking_date = request.POST.get('booking_date')

            # Validate booking date
            if not booking_date or booking_date < str(date.today()):
                return JsonResponse({"error": "Invalid booking date. Please select a future date."}, status=400)

            # Separate validations
            if Booking.objects.filter(user=request.user).exists():
                return JsonResponse({"error": "You already have a booking."}, status=400)

            if Booking.objects.filter(first_name=first_name, last_name=last_name).exists():
                return JsonResponse({"error": "This name is already associated with a booking. Please use a different name."}, status=400)

            if Booking.objects.filter(contact_number=contact_number).exists():
                return JsonResponse({"error": "This contact number is already associated with a booking. Please use a different number."}, status=400)

            if Booking.objects.filter(booking_date=booking_date, status='approved').exists():
                return JsonResponse({"error": "The selected date is already booked. Please choose another date."}, status=400)

            if Booking.objects.filter(user=request.user, status='approved').exists():
                return JsonResponse({"error": "You already have an active approved booking. Please cancel it before making a new one."}, status=400)

            # Create and save the booking directly without confirmation
            booking = Booking.objects.create(
                user=request.user,
                cleaning_service=cleaning_service,
                first_name=first_name,
                last_name=last_name,
                contact_number=contact_number,
                address=address,
                additional_info=additional_info,
                booking_date=booking_date,
                status='pending'  # Assuming status starts as 'pending' until approved
            )
            booking.save()

            # Fetch and return all booked dates
            booked_dates = Booking.objects.filter(status='approved').values_list('booking_date', flat=True)
            return JsonResponse({"success": "Booking submitted successfully!", "booked_dates": list(booked_dates)})

        except Exception as e:
            return JsonResponse({"error": "An unexpected error occurred. Please try again later."}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)
    
def check_booking(request, service_name):
    if request.user.is_authenticated:
        current_user = request.user
        existing_booking = Booking.objects.filter(cleaning_service=service_name).first()

        if existing_booking:
            if existing_booking.user == current_user:
                return JsonResponse({"error": "You have already booked this service. Please wait for the admin approval"})
            else:
                return JsonResponse({"error": f"This service is already booked by another user ({existing_booking.user.username}). Please choose another one."})
        else:
            return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": "You must be logged in to book a service."})
    
def admin_dashboard(request):
    all_bookings = Booking.objects.all()
    approved_bookings = Booking.objects.filter(status='approved')
    pending_bookings = Booking.objects.filter(status='pending')
    total_users = User.objects.filter(is_staff=False).count()

    # Calculate totals
    total_bookings = all_bookings.count()
    approved_count = approved_bookings.count()
    pending_count = pending_bookings.count()

    # Prepare context
    context = {
        'bookings': all_bookings.order_by('-created_at')[:5],  # Pass recent 5 bookings
        'approved_bookings': approved_count,
        'pending_bookings': pending_count,
        'total_bookings': total_bookings,
        'total_users': total_users,
        'current_date': date.today().strftime('%B %d, %Y'),
    }
    return render(request, 'cleaning/admin_dashboard.html', context)


#admin booking page
def admin_booking(request):
    bookings_list = Booking.objects.all()  # Replace with your Booking model/query
    paginator = Paginator(bookings_list, 20)  # Show 10 bookings per page
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    total_bookings = Booking.objects.count()
    approved_bookings = Booking.objects.filter(status='Approved').count()
    pending_bookings = Booking.objects.filter(status='Pending').count()

    return render(request, 'cleaning/Bookings.html', {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'approved_bookings': approved_bookings,
        'pending_bookings': pending_bookings,
    })
    
#admin booking page if imo syang e approve
@csrf_exempt  # Use only for testing if CSRF issues arise; remove in production
def confirm_booking(request, booking_id):
    if request.method == 'POST':
        try:
            booking = get_object_or_404(Booking, pk=booking_id)
            if booking.status != Booking.PENDING:
                return JsonResponse({'success': False, 'message': 'Booking is not in a pending state.'})

            booking.status = Booking.APPROVED  # Change status to approved
            booking.save()

            return JsonResponse({
                'success': True,
                'message': 'Booking approved successfully.',
                'phone_number': booking.contact_number,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

#also for deny the bookings
@csrf_exempt
# def deny_booking(request, booking_id):
#     if request.method == 'POST':
#         try:
#             booking = get_object_or_404(Booking, pk=booking_id)
#             if booking.status != Booking.PENDING:
#                 return JsonResponse({'success': False, 'message': 'Booking is not in a pending state.'})

#             booking.status = Booking.DENIED  # Change status to denied
#             booking.save()

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Booking denied successfully.',
#                 'phone_number': booking.contact_number,
#             })
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
#     return JsonResponse({'success': False, 'message': 'Invalid request method.'})
#admin manage users page
@login_required
def user_manage(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(is_staff=False, username__icontains=query).order_by('id')
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    if request.method == 'POST' and 'delete_user' in request.POST:
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, f"User {user.username} deleted successfully.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    context = {
        'users': users_page,
        'query': query,
        'current_date': date.today().strftime('%B %d, %Y'),
    }
    return render(request, 'cleaning/users.html', context)
#under the manage user page 
@login_required
def delete_user(request, user_id):
    if request.method == "POST":
        try:
        
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, "User deleted successfully.")
            return JsonResponse({"success": True, "message": "User deleted successfully."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found."}, status=404)
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

def staffs(request):
    return render(request, 'cleaning/staff.html')
def policy(request):
    return render(request, 'cleaning/privacy_and_policy.html')

#chart page in reports
def reports(request):
    # Get the selected month from the request, default to the current month if not provided
    month = request.GET.get('month', None)  # Get the selected month from the URL parameter
    
    if month:
        # Filter bookings for the selected month
        bookings = Booking.objects.filter(booking_date__month=month)
    else:
        # If no month is selected, you can just get all bookings
        bookings = Booking.objects.all()

    # Count the number of bookings for each cleaning service
    service_counts = {choice[1]: 0 for choice in Booking.CLEANING_CHOICES}
    
    # Annotate the bookings by the count of cleaning service
    bookings = bookings.values('cleaning_service').annotate(count=Count('cleaning_service'))

    for booking in bookings:
        service_name = dict(Booking.CLEANING_CHOICES).get(booking['cleaning_service'])
        if service_name:
            service_counts[service_name] = booking['count']
    
    # Pass the service counts and month to the template
    context = {
        'service_counts': service_counts,
        'selected_month': month  # Include the selected month in the context
    }
    
    return render(request, 'cleaning/reports.html', context)


#schedule page didto sa damin
@login_required
def schedule(request):
    # Get the current year and month
    current_year = timezone.now().year
    current_month = timezone.now().month

    # Get the next month's year and month
    if current_month == 12:
        next_month = 1
        next_month_year = current_year + 1
    else:
        next_month = current_month + 1
        next_month_year = current_year

    # Get bookings for the current month and future months (including previous month for display)
    bookings = Booking.objects.filter(booking_date__year=current_year, booking_date__month=current_month)
    future_bookings = Booking.objects.filter(booking_date__gt=timezone.now())  # Get all future bookings

    # Get all bookings from the previous year
    last_year_bookings = Booking.objects.filter(
        booking_date__year=current_year - 1  # Get all bookings from the previous year
    )

    # Get all bookings for the previous month (for display in the next month)
    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = current_year

    # Get all bookings from last month (display them in the next month)
    last_month_bookings = Booking.objects.filter(
        booking_date__month=last_month,
        booking_date__year__lte=current_year  # This includes past bookings (even from last year)
    )

    # Create a dictionary with date as key (formatted as YYYY-MM-DD) and username as value
    booked_dates = {}

    # Add current month bookings
    for booking in bookings:
        booked_dates[str(booking.booking_date)] = booking.user.username

    # Add future bookings (upcoming months)
    for booking in future_bookings:
        booked_dates[str(booking.booking_date)] = booking.user.username

    # Add last year bookings (for previous months in this year)
    for booking in last_year_bookings:
        booked_dates[str(booking.booking_date)] = booking.user.username

    # Add last month bookings (displayed in next month)
    for booking in last_month_bookings:
        next_month_date = booking.booking_date.replace(year=next_month_year, month=next_month)
        booked_dates[str(next_month_date)] = booking.user.username

    # Pass the booked dates to the template
    return render(request, 'cleaning/services_schedule.html', {
        'booked_dates': booked_dates,
        'current_year': current_year,
        'current_month': current_month,
        'next_month': next_month,
        'next_month_year': next_month_year,
    })

#submit ratings
# def submit_rating(request):
#     if request.method == "POST":
#         # Handle rating submission logic
#         service = request.POST.get('service')
#         rating = request.POST.get('rating')
#         feedback = request.POST.get('feedback')

#         # Save to database or perform other logic
#         # Example:
#         # ServiceRating.objects.create(service=service, rating=rating, feedback=feedback)

#         return JsonResponse({'success': True, 'message': 'Rating submitted successfully.'})
#     return JsonResponse({'success': False, 'error': 'Invalid request method.'})


from django.urls import reverse 
# def submit_feedback(request):
#     if request.method == 'POST':
#         form = FeedbackForm(request.POST)

#         if form.is_valid():
#             # Fetch the logged-in user (if available)
#             user = request.user
            
#             # Retrieve the user's first name and last name from the latest booking (or any logic you want)
#             booking = Booking.objects.filter(user=user).last()  # Getting the latest booking (or modify this logic)
            
#             if booking:
#                 first_name = booking.first_name
#                 last_name = booking.last_name
#             else:
#                 first_name = "Unknown"
#                 last_name = "Unknown"

#             # Save the feedback with the associated user's name
#             feedback = form.save(commit=False)
#             feedback.name = f"{first_name} {last_name}"  # Set the full name
#             feedback.user = user  # Associate the feedback with the logged-in user
#             feedback.save()

#             return JsonResponse({'status': 'success'})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'There was an issue with your submission.'})

#     else:
#         form = FeedbackForm()

#     return render(request, 'feedback_form.html', {'form': form})

def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_about'))
    else:
        form = FeedbackForm()

    return render(request, 'cleaning/u-about.html', {'form': form})

# # rating sa services ug feedbacks
# from .forms import RatingForm
# from .models import Rating
# @login_required
# def submit_rating(request):
#     if request.method == 'POST':
#         service = request.POST.get('service')
#         rating = request.POST.get('rating')
#         feedback = request.POST.get('feedback')

#         # Save the rating and feedback
#         Rating.objects.create(
#             user=request.user,
#             service=service,
#             rating=rating,
#             feedback=feedback
#         )

#         messages.success(request, 'Thank you for your feedback!')
#         return redirect('user_services')  # Replace 'service_page' with your desired redirect URL

#     return redirect('user_services')  # Replace 'home' with your desired fallback URL


# def display_ratings(request):
#     ratings = Rating.objects.all()
#     return render(request, 'cleaning/u-services.html', {'ratings': ratings})