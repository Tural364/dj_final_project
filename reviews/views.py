from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from bookings.models import BookingRequest
from accounts.models import User
from .forms import ReviewForm
from .models import Review

@login_required
def create(request, booking_id):
    booking = get_object_or_404(BookingRequest.objects.select_related("offer", "learner"), pk=booking_id)
    if booking.learner_id != request.user.id:
        raise PermissionDenied
    if booking.status != BookingRequest.Status.COMPLETED:
        messages.error(request, "Оставить отзыв можно только после завершения занятия.")
        return redirect("bookings:mine")
    if hasattr(booking, "review"):
        messages.error(request, "Для этого занятия отзыв уже существует.")
        return redirect("bookings:mine")
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.booking = booking
        review.author = request.user
        review.save()
        messages.success(request, "Спасибо за отзыв!")
        return redirect("bookings:mine")
    return render(request, "reviews/review_form.html", {"form": form, "booking": booking})

@login_required
def edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.author_id != request.user.id and not (request.user.is_staff or request.user.role in (User.Role.ADMIN, User.Role.SUPER_ADMIN)):
        raise PermissionDenied
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Отзыв обновлён.")
        return redirect("accounts:profile", username=review.booking.offer.owner.username)
    return render(request, "reviews/review_form.html", {"form": form, "booking": review.booking, "page_title": "Редактировать отзыв"})

@login_required
@require_POST
def delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.author_id != request.user.id and not (request.user.is_staff or request.user.role in (User.Role.ADMIN, User.Role.SUPER_ADMIN)):
        raise PermissionDenied
    review.delete()
    messages.success(request, "Отзыв удалён.")
    return redirect("offers:explore")
