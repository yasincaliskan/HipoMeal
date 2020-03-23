from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect,redirect, Http404
from .models import Meal, Ingredient, Like, Rate
from .forms import MealForm, IngredientForm, CommentForm
from django.db.models import Sum, Count, FloatField
from django.db.models.functions import Cast
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.views.generic import DetailView, ListView


class MealListView(ListView):
    paginate_by = 3
    model = Meal
    template_name = 'meal/home.html'
    context_object_name = 'meals'
    ordering = ['-publishing_date']

    def get_queryset(self):
        queryset = super(MealListView, self).get_queryset()
        if self.request.GET.get('search'):
            search_keys = self.request.GET.get('search').split(" ")
            for key in search_keys:
                queryset = queryset.filter(
                    Q(ingredients__name__icontains=key) |
                    Q(title__icontains=key) |
                    Q(description__icontains=key)
                ).distinct()
        if self.request.GET.get('ingredients'):
            queryset = queryset.filter(ingredients__in=self.request.GET.get('ingredients').split(','))
        if self.request.GET.get('category'):
            queryset = queryset.filter(category=int(self.request.GET.get('category')))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MealListView, self).get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.annotate(count=Count('meals')).order_by('-count')[:5]
        return context


class MealDetailView(DetailView):
    model = Meal
    context_object = 'meal'
    template_name = 'meal/meal_detail.html'

    def get_queryset(self):
        meals = Meal.objects.annotate(
            rate_total=Sum('rates__points'),
            rate_count=Count('rates')
        ).annotate(
            rate_average=F('rate_total') / F('rate_count')
        ).all()
        return meals

    def get_context_data(self, **kwargs):
        context = super(MealDetailView, self).get_context_data()
        meal = self.get_object()
        context['liked_by_user'] = meal.likes.filter(liked=True).exists()
        context['like_count'] = meal.likes.filter(liked=True).count()
        return context


def meal_create(request):
    if not request.user.is_authenticated:
        return Http404()

    if request.method == "POST":
        form = MealForm(request.POST, request.FILES or None)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()
            meal.ingredients.set(form.cleaned_data["ingredients"])
            messages.success(request, 'Meal created successfully!')
            return HttpResponseRedirect(meal.get_absolute_url())
    else:
        form = MealForm()

    context = {'form': form}
    return render(request, 'meal/form.html', context)


def meal_update(request, slug):
    if not request.user.is_authenticated:
        return Http404()

    meal = get_object_or_404(Meal, slug=slug)
    if meal.user == request.user:
        form = MealForm(request.POST or None, request.FILES or None, instance=meal)

        if form.is_valid():
            form.save()
            messages.success(request, 'Meal updated successfully!')
            return HttpResponseRedirect(meal.get_absolute_url())
    else:
        return redirect('meal:home')
    context = {'form': form}
    return render(request, 'meal/form.html', context)


def meal_delete(request, slug):
    if not request.user.is_authenticated:
        return Http404()

    meal = get_object_or_404(Meal, slug=slug)
    if meal.user == request.user:
        meal.delete()
        messages.error(request, 'Meal deleted!')
    else:
        messages.error(request, 'You can not delete this recipe.')
    return redirect('meal:home')


def ingredient_create(request):
    if not request.user.is_authenticated:
        return Http404()

    if request.method == "POST":
        form = IngredientForm(request.POST or None)

        if form.is_valid():
            ingredient = form.save()
            messages.success(request, 'Ingredient added successfully!')
            return redirect('meal:create')
    else:
        ingredient = IngredientForm()

    context = {'ingredient': ingredient}
    return render(request, 'meal/ingredient_form.html', context)


def comment_create(request, slug):
    meal = get_object_or_404(Meal, slug=slug)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.meal = meal
        comment.save()
        return HttpResponseRedirect(meal.get_absolute_url())
    context = {
        'form': form,
    }
    return render(request, 'meal/comment.html', context)


def like_meal(request, slug):
    if request.method == "POST":
        meal = Meal.objects.get(slug=slug)
        like = meal.likes.filter(user=request.user).first()
        if like:
            like.liked = False if like.liked else True
            like.save()
        else:
            like = Like(user=request.user, meal=meal, liked=True)
            like.save()

        like_count = meal.likes.filter(liked=True).count()

        response = {
            "like_count": like_count,
            "liked": like.liked
        }
        return JsonResponse(response)


def rate_meal(request, slug):
    if request.method == "POST":
        meal = Meal.objects.get(slug=slug)
        rate = meal.rates.filter(user=request.user).first()
        if rate:
            rate.points = int(request.POST['rate'])
            rate.save()
        else:
            rate = Rate(user=request.user, meal=meal, points=int(request.POST['rate']))
            rate.save()
        meal = Meal.objects.annotate(
            rate_total=Sum('rates__points'),
            rate_count=Count('rates')
        ).annotate(
            rate_average=F('rate_total')/F('rate_count')
        ).get(slug=slug)

        response = {
            "rate_average": meal.rate_average,
            "user_rate": rate.points
        }
        return JsonResponse(response)


