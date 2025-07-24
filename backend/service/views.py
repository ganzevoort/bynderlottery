from django.shortcuts import render


def index_view(request):
    """Simple index view that welcomes the user."""
    return render(request, "index.html")
