from django.http import HttpResponse


def home(request):
    return HttpResponse("Public Home Page")
