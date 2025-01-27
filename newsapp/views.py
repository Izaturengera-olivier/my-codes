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


@user_passes_test(is_superuser)
def admin_dashboard(request):
    news_count = News.objects.count()
    articles_count = Article.objects.count()
    messages_count = ContactMessage.objects.count()
    users_count = User.objects.filter(is_superuser=False).count()
    return render(request, 'admin_dashboard.html', {
        'news_count': news_count,
        'articles_count': articles_count,
        'messages_count': messages_count,
        'users_count': users_count
    })
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

