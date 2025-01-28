from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth import get_user_model
import random
import string
from django.contrib.auth.decorators import user_passes_test
from .models import *

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

User = get_user_model()


def index(request):
    articles = Article.objects.all().order_by('-published_date')[:6]
    featured_articles = Article.objects.filter(is_featured=True)[:2]

    return render(request, 'home.html', {
        'articles': articles,
        'featured_articles': featured_articles
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Redirect to the home page after login
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')  # Redirect to login page after successful sign-up
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            messages.success(request, 'Thank you! Your message has been sent.')
            return redirect('contact_us')  # Redirect back to the contact page
    else:
        form = ContactForm()

    return render(request, 'contact_us.html', {'form': form})

@login_required
def news_list(request):
    news = News.objects.all().order_by('-published_date')  # Order by latest news
    return render(request, 'index.html', {'news': news})


# Create your views here.
def news_detail(request, pk):
    article = get_object_or_404(News, pk=pk)
    return render(request, 'news_detail.html', {'article': article})


def about(request):
    return render(request, 'about.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def terms_conditions(request):
    return render(request, 'terms_conditions.html')


def article_detail(request, article_id):
    # Get the article using the provided ID
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'article_detail.html', {'article': article})


def search(request):
    query = request.GET.get('query', '')
    articles = Article.objects.all()

    if query:
        form = SearchForm(request.GET)
        return render(request, 'base.html', {
            'form': form,
            'articles': articles,
            'query': query
        })

    return render(request, 'base.html', {
        'form': SearchForm(),
        'articles': articles,

    })


VERIFICATION_CODES = {}


def send_verification_code(email):
    """Generate and send a verification code to the given email."""
    code = ''.join(random.choices(string.digits, k=6))  # 6-digit OTP
    expiration_time = datetime.now() + timedelta(minutes=10)  # Expires in 10 minutes
    VERIFICATION_CODES[email] = {'code': code, 'expires_at': expiration_time}

    # Send email
    send_mail(
        subject='Password Reset Verification Code',
        message=f'Your verification code is: {code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def password_reset_request(request):
    """Step 1: User requests a password reset."""
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            send_verification_code(email)
            messages.success(request, 'A verification code has been sent to your email.')
            return redirect('password_reset_verify')
        else:
            messages.error(request, 'No user found with this email address.')

    return render(request, 'password_reset_request.html')


def password_reset_verify(request):
    """Step 2: User enters verification code and new password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        new_password = request.POST.get('password')

        # Check if the code is valid
        stored_data = VERIFICATION_CODES.get(email)
        if stored_data and stored_data['code'] == code:
            if datetime.now() > stored_data['expires_at']:
                messages.error(request, 'Verification code has expired.')
            else:
                # Reset the password
                user = User.objects.filter(email=email).first()
                if user:
                    user.password = make_password(new_password)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('login')
        else:
            messages.error(request, 'Invalid verification code.')

    return render(request, 'password_reset_verify.html')


def is_superuser(user):
    return user.is_superuser


@login_required
def admin_dashboard(request):
    # Ensure only admin users can access this view
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Sample data for the charts
    chart_data = {
        'labels': ['News', 'Articles', 'Messages', 'Users'],
        'values': [
            News.objects.count(),
            Article.objects.count(),
            ContactMessage.objects.count(),
            User.objects.count()
        ]
    }

    context = {
        'news_count': News.objects.count(),
        'articles_count': Article.objects.count(),
        'messages_count': ContactMessage.objects.count(),
        'users_count': User.objects.count(),
        'chart_data': chart_data,
    }

    return render(request, 'admin_dashboard.html', context)


@user_passes_test(is_superuser)
def manage_news(request):
    news = News.objects.all()
    return render(request, 'manage_news.html', {'news': news})


@user_passes_test(is_superuser)
def manage_articles(request):
    articles = Article.objects.all()
    return render(request, 'manage_articles.html', {'articles': articles})


@user_passes_test(is_superuser)
def manage_messages(request):
    messages = ContactMessage.objects.all()
    return render(request, 'manage_messages.html', {'messages': messages})


@user_passes_test(is_superuser)
def manage_users(request):
    users = User.objects.filter(is_superuser=False)
    return render(request, 'manage_users.html', {'users': users})

def reply_message(request, message_id):
    message = get_object_or_404(ContactMessage, pk=message_id)
    if request.method == 'POST':
        form = ReplyMessageForm(request.POST)
        if form.is_valid():
            reply_message = form.cleaned_data['reply_message']
            recipient_email = form.cleaned_data['recipient_email']

            try:
                subject = f"Re: {message.subject}"
                send_mail(
                    subject,
                    reply_message,
                    'izaturengeraolivier@gmail.com',
                    [recipient_email],
                    fail_silently=False,
                )
                return redirect('message_list')
            except Exception as e:
                # Log the error for debugging
                print(f"Error sending email: {e}")
                # Display an error message to the user
                messages.error(request, "Reply message sent successfully.")
        else:
            messages.error(request, "Invalid form data.")
    else:
        form = ReplyMessageForm(initial={
            'recipient_email': message.email,
            'original_message': message.message,
        })
    return render(request, 'reply_message.html', {'message': message, 'form': form})


@login_required
def deactivate_user(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot deactivate the superuser.")
    else:
        user.is_active = False
        user.save()
        messages.success(request, f"User '{user.username}' deactivated successfully.")
    return redirect('manage_users')


@login_required
def activate_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User '{user.username}' activated successfully.")
    return redirect('manage_users')


@login_required
def make_admin(request, user_id):
    user = User.objects.get(pk=user_id)
    if not user.is_superuser:  # Prevent making the superuser an admin again
        user.is_staff = True
        user.save()
        messages.success(request, f"User '{user.username}' granted admin privileges.")
    else:
        messages.error(request, "User is already an administrator.")
    return redirect('manage_users')


@login_required
def revoke_admin(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot revoke admin privileges from the superuser.")
    else:
        user.is_staff = False
        user.save()
        messages.success(request, f"Admin privileges revoked from user '{user.username}'.")
    return redirect('manage_users')


@login_required
def delete_account(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('manage_users')

    if request.method == 'POST':
        user.delete()
        messages.success(request, "User account deleted successfully.")
        return redirect('manage_users')

    return render(request, 'delete_account.html', {'user': user})
