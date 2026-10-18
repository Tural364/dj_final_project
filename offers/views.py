from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from accounts.models import User
from .forms import SkillOfferForm
from .models import Category, SkillOffer

def explore(request):
    qs = SkillOffer.objects.filter(status=SkillOffer.Status.PUBLISHED).select_related("owner", "category").annotate(
        average_rating=Avg("booking_requests__review__rating"), rating_count=Count("booking_requests__review", distinct=True)
    )
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    level = request.GET.get("level", "")
    fmt = request.GET.get("format", "")
    rating = request.GET.get("rating", "")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category__slug=category)
    if level:
        qs = qs.filter(level=level)
    if fmt:
        qs = qs.filter(format=fmt)
    if rating == "4":
        qs = qs.filter(average_rating__gte=4)
    return render(request, "offers/explore.html", {
        "offers": qs, "categories": Category.objects.all(), "q": q,
        "selected_category": category, "selected_level": level, "selected_format": fmt,
        "selected_rating": rating,
    })

def popular(request):
    offers = SkillOffer.objects.filter(status=SkillOffer.Status.PUBLISHED).select_related("owner", "category").annotate(
        average_rating=Avg("booking_requests__review__rating"), rating_count=Count("booking_requests__review", distinct=True)
    ).filter(average_rating__gte=4)
    return render(request, "offers/explore.html", {"offers": offers, "page_title": "Popular", "categories": Category.objects.all()})

def mentors(request):
    people = User.objects.filter(skill_offers__status=SkillOffer.Status.PUBLISHED, is_blocked=False).distinct().prefetch_related("skill_offers")
    return render(request, "accounts/mentors.html", {"people": people})

def category_list(request):
    return render(request, "offers/categories.html", {"categories": Category.objects.annotate(offer_count=Count("offers", filter=Q(offers__status=SkillOffer.Status.PUBLISHED)))})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    offers = SkillOffer.objects.filter(category=category, status=SkillOffer.Status.PUBLISHED).select_related("owner", "category").annotate(
        average_rating=Avg("booking_requests__review__rating"), rating_count=Count("booking_requests__review", distinct=True)
    )
    return render(request, "offers/explore.html", {"offers": offers, "page_title": category.name, "categories": Category.objects.all()})

def detail(request, pk):
    offer = get_object_or_404(SkillOffer.objects.select_related("owner", "category").annotate(
        average_rating=Avg("booking_requests__review__rating"), rating_count=Count("booking_requests__review", distinct=True)
    ), pk=pk)
    if offer.status != SkillOffer.Status.PUBLISHED and request.user != offer.owner and not (request.user.is_authenticated and request.user.is_staff):
        from django.http import Http404
        raise Http404
    completed_count = offer.booking_requests.filter(status="completed").count()
    return render(request, "offers/detail.html", {"offer": offer, "completed_count": completed_count})

@login_required
def create(request):
    if request.user.is_blocked:
        messages.error(request, "Заблокированный пользователь не может создавать предложения.")
        return redirect("offers:explore")
    form = SkillOfferForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        offer = form.save(commit=False)
        offer.owner = request.user
        offer.status = SkillOffer.Status.PENDING
        offer.save()
        messages.success(request, "Предложение отправлено на модерацию.")
        return redirect("offers:detail", pk=offer.pk)
    return render(request, "offers/offer_form.html", {"form": form, "page_title": "Новое предложение"})

@login_required
def edit(request, pk):
    offer = get_object_or_404(SkillOffer, pk=pk)
    if not (request.user == offer.owner or request.user.is_staff or request.user.role == User.Role.ADMIN or request.user.role == User.Role.SUPER_ADMIN):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    form = SkillOfferForm(request.POST or None, request.FILES or None, instance=offer)
    if request.method == "POST" and form.is_valid():
        offer = form.save(commit=False)
        if request.user == offer.owner and not request.user.is_staff and request.user.role == User.Role.USER:
            offer.status = SkillOffer.Status.PENDING
        offer.save()
        messages.success(request, "Изменения сохранены.")
        return redirect("offers:detail", pk=offer.pk)
    return render(request, "offers/offer_form.html", {"form": form, "page_title": "Редактировать предложение"})

@login_required
@require_POST
def delete(request, pk):
    offer = get_object_or_404(SkillOffer, pk=pk)
    allowed = request.user == offer.owner or request.user.is_staff or request.user.role in (User.Role.ADMIN, User.Role.SUPER_ADMIN)
    if not allowed:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    offer.delete()
    messages.success(request, "Предложение удалено.")
    return redirect("offers:explore")

@login_required
@require_POST
def moderate(request, pk, action):
    if not (request.user.is_staff or request.user.role in (User.Role.ADMIN, User.Role.SUPER_ADMIN)):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    offer = get_object_or_404(SkillOffer, pk=pk)
    if action == "approve":
        offer.status = SkillOffer.Status.PUBLISHED
    elif action == "reject":
        offer.status = SkillOffer.Status.REJECTED
    else:
        return redirect("offers:detail", pk=pk)
    offer.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Статус предложения: {offer.get_status_display()}.")
    return redirect("offers:detail", pk=pk)

@login_required
def my_offers(request):
    offers = SkillOffer.objects.filter(owner=request.user).select_related("category")
    return render(request, "offers/explore.html", {"offers": offers, "page_title": "My Offers", "categories": Category.objects.all()})
