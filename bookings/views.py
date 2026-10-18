from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from offers.models import SkillOffer
from accounts.models import User
from .forms import BookingRequestForm
from .models import BookingRequest

@login_required
def create(request, offer_id):
    offer = get_object_or_404(SkillOffer, pk=offer_id, status=SkillOffer.Status.PUBLISHED)
    if request.user.is_blocked:
        messages.error(request, "Заблокированный пользователь не может отправлять запросы.")
        return redirect("offers:detail", pk=offer.pk)
    if offer.owner_id == request.user.id:
        messages.error(request, "Нельзя записаться на собственное предложение.")
        return redirect("offers:detail", pk=offer.pk)
    form = BookingRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if BookingRequest.objects.filter(offer=offer, learner=request.user, status__in=["pending", "accepted"]).exists():
            messages.error(request, "У вас уже есть активный запрос на это предложение.")
        else:
            booking = form.save(commit=False)
            booking.offer = offer
            booking.learner = request.user
            try:
                booking.save()
                messages.success(request, "Запрос отправлен.")
            except IntegrityError:
                messages.error(request, "Активный запрос уже существует.")
        return redirect("bookings:mine")
    return render(request, "bookings/request_form.html", {"form": form, "offer": offer})

@login_required
def mine(request):
    sent = BookingRequest.objects.filter(learner=request.user).select_related("offer", "offer__owner", "offer__category")
    received = BookingRequest.objects.filter(offer__owner=request.user).select_related("offer", "learner", "offer__category")
    return render(request, "bookings/mine.html", {"sent": sent, "received": received})

@login_required
@require_POST
def update_status(request, pk, action):
    booking = get_object_or_404(BookingRequest.objects.select_related("offer", "learner", "offer__owner"), pk=pk)
    is_owner = booking.offer.owner_id == request.user.id
    if action in ("accept", "reject", "complete") and not (is_owner or request.user.is_staff or request.user.role in (User.Role.ADMIN, User.Role.SUPER_ADMIN)):
        raise PermissionDenied
    if action == "cancel" and booking.learner_id != request.user.id:
        raise PermissionDenied
    mapping = {
        "accept": (BookingRequest.Status.PENDING, BookingRequest.Status.ACCEPTED),
        "reject": (BookingRequest.Status.PENDING, BookingRequest.Status.REJECTED),
        "complete": (BookingRequest.Status.ACCEPTED, BookingRequest.Status.COMPLETED),
        "cancel": (BookingRequest.Status.PENDING, BookingRequest.Status.CANCELLED),
    }
    if action not in mapping:
        raise PermissionDenied
    old, new = mapping[action]
    if booking.status != old:
        messages.error(request, "Этот переход статуса сейчас недоступен.")
    else:
        booking.status = new
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, "Статус запроса обновлён.")
    return redirect("bookings:mine")
