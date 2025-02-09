from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def register(request):
    pass

@login_required
def index(request):
    return render(request, "tierra_media/index.html")