from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'core/index.html')


def tiers(request):
    return render(request, 'core/tiers.html')
