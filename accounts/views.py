from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import RegisterForm, ProfileForm
from .models import User
from offers.models import SkillOffer
from bookings.models import BookingRequest
from reviews.models import Review

def register(request):
    if request.user.is_authenticated:
        return redirect("offers:explore")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Аккаунт создан.")
        return redirect("offers:explore")
    return render(request, "accounts/register.html", {"form": form})

@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлён.")
        return redirect("accounts:profile", username=request.user.username)
    return render(request, "accounts/profile_edit.html", {"form": form})

def profile(request, username):
    person = get_object_or_404(User, username=username)
    offers = SkillOffer.objects.filter(owner=person, status=SkillOffer.Status.PUBLISHED).select_related("category")
    reviews = Review.objects.filter(booking__offer__owner=person).select_related("author", "booking")
    from django.db.models import Avg
    rating = reviews.aggregate(value=Avg("rating"))["value"]
    completed = BookingRequest.objects.filter(offer__owner=person, status=BookingRequest.Status.COMPLETED).count()
    return render(request, "accounts/profile.html", {
        "person": person, "offers": offers, "reviews": reviews,
        "rating": rating, "completed_count": completed,
    })

@login_required
@require_POST
def toggle_block(request, user_id):
    if not (request.user.is_superuser or request.user.role == User.Role.SUPER_ADMIN):
        messages.error(request, "Только суперадмин может блокировать пользователей.")
        return redirect("offers:explore")
    person = get_object_or_404(User, pk=user_id)
    if person.is_superuser or person == request.user:
        messages.error(request, "Это действие запрещено.")
    else:
        person.is_blocked = not person.is_blocked
        person.save(update_fields=["is_blocked"])
        messages.success(request, "Статус блокировки изменён.")
    return redirect("accounts:profile", username=person.username)
