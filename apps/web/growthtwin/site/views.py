"""Public product pages for the local campaign-experience prototype."""

from django.shortcuts import render


def home(request):
    """Render the public product overview and interactive local mockup."""
    return render(request, "site/home.html")
