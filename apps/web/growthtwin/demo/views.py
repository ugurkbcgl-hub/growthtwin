"""Views for the synthetic Phase 0 profile screen."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from growthtwin.demo.forms import DemoProfileForm
from growthtwin.demo.models import DemoProfile


@login_required
def profile_edit(request):
    profile, _ = DemoProfile.objects.get_or_create(owner=request.user)
    if request.method == "POST":
        form = DemoProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Demo klinik profili kaydedildi.")
            return redirect("demo:profile-edit")
    else:
        form = DemoProfileForm(instance=profile)

    return render(request, "demo/profile_edit.html", {"form": form})
