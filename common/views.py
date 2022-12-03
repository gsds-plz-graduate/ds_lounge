from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'common/home.html')


def share(request):
    return render(request, 'common/share.html')
