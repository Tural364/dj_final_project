from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from offers.models import SkillOffer
from .models import Favorite

@login_required
def list_favorites(request):
    favorites = Favorite.objects.filter(user=request.user, offer__status=SkillOffer.Status.PUBLISHED).select_related("offer", "offer__owner", "offer__category")
    return render(request, "favorites/list.html", {"favorites": favorites, "offers": [item.offer for item in favorites]})

@login_required
@require_POST
def toggle(request, offer_id):
    offer = get_object_or_404(SkillOffer, pk=offer_id, status=SkillOffer.Status.PUBLISHED)
    favorite, created = Favorite.objects.get_or_create(user=request.user, offer=offer)
    if not created:
        favorite.delete()
        messages.success(request, "Удалено из избранного.")
    else:
        messages.success(request, "Добавлено в избранное.")
    return redirect(request.POST.get("next") or offer.get_absolute_url())
