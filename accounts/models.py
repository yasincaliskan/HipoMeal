from django.db import models
from django.contrib.auth.models import User
from meal.models import Meal


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    meals = models.ForeignKey(Meal, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.user.username

