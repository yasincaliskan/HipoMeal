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
from django.contrib.postgres.search import SearchVector, SearchQuery


# def meal_index(request):
#     meal_list = Meal.objects.all()
#     query = request.GET.get('q')
#     if query:
#         meal_list = meal_list.filter(Q(title__icontains=query) |
#                                      Q(description__icontains=query) |
#                                      Q(ingredient__icontains=query)).distinct()
#     paginator = Paginator(meal_list, 5)
#
#     page_number = request.GET.get('page')
#     meals = paginator.get_page(page_number)
#
#     return render(request, 'meal/index.html', {'meals': meals})



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
                queryset = queryset.filter(Q(ingredients__name__icontains=key) |
                                          Q(title__icontains=key) |
                                          Q(description__icontains=key)).distinct()

        if self.request.GET.get('ingredients'):
            queryset = queryset.filter(ingredients__in=self.request.GET.get('ingredients').split(','))
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
        meal = Meal.objects.annotate(rate_average=Cast(Sum('rates__points'),
                                                       FloatField()) / Cast(Count('rates'), FloatField())).all()
        return meal

    def get_object(self, queryset=None):
        meal = super().get_object(queryset)
        meal.like_count = meal.likes.filter(liked=True).count()
        if self.request.user.is_authenticated:
            meal.is_user_liked = meal.likes.filter(user=self.request.user, liked=True).exists()
            if meal.rates.filter(user=self.request.user).exists():
                meal.user_rate = meal.rates.get(user=self.request.user).points
            else:
                meal.user_rate = None
        return meal


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


def soup_index(request):
    soups = Meal.objects.filter(category=1)
    paginator = Paginator(soups, 5)
    page_number = request.GET.get('page')
    soups = paginator.get_page(page_number)
    return render(request, 'meal/categories/soup.html', {'soups': soups})


def meals_index(request):
    meals = Meal.objects.filter(category=2)
    paginator = Paginator(meals, 5)
    page_number = request.GET.get('page')
    meals = paginator.get_page(page_number)
    return render(request, 'meal/categories/meals.html', {'meals': meals})


def snack_index(request):
    snacks = Meal.objects.filter(category=3)
    paginator = Paginator(snacks, 5)
    page_number = request.GET.get('page')
    snacks = paginator.get_page(page_number)
    return render(request, 'meal/categories/snack.html', {'snacks': snacks})


def dessert_index(request):
    desserts = Meal.objects.filter(category=4)
    paginator = Paginator(desserts, 5)
    page_number = request.GET.get('page')
    desserts = paginator.get_page(page_number)
    return render(request, 'meal/categories/dessert.html', {'desserts': desserts})


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
            like.liked = not like.liked
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


