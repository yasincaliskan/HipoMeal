from django.urls import path
from .views import *

app_name = 'meal'

urlpatterns = [
    path('', MealListView.as_view(), name="home"),
    path('create/', meal_create, name="create"),
    path('ingredient/', ingredient_create, name="ingredient"),

    path('<slug:slug>/comment/', comment_create, name="comment-create"),
    path('<slug:slug>/', MealDetailView.as_view(), name="detail"),
    path('<slug:slug>/update/', meal_update, name="update"),
    path('<slug:slug>/delete/', meal_delete, name="delete"),
    path('<slug:slug>/like/', like_meal, name="like"),
    path('<slug:slug>/rate/', rate_meal, name="rate"),

]
