from django.shortcuts import render

# Create your views here.
def google_login(request):
    return render(request, 'oauth/login.html')