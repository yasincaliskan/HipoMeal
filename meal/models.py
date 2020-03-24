from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator


class Ingredient(models.Model):
    name = models.CharField(max_length=70, unique=True)

    def __str__(self):
        return self.name


class Meal(models.Model):
    DIFFICULTY_CHOICES = [
        (1, "Easy"),
        (2, "Medium"),
        (3, "Hard")
    ]

    CATEGORY_CHOICES = [
        (1, "Soup"),
        (2, "Meal"),
        (3, "Snack"),
        (4, "Dessert")
    ]

    user = models.ForeignKey(User, related_name='meals', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.IntegerField(default=2, choices=CATEGORY_CHOICES)
    difficulty = models.IntegerField(default=1, choices=DIFFICULTY_CHOICES)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, blank=True, related_name='meals')
    publishing_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField()
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('meal:detail', kwargs={'slug': self.slug})

    def get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        counter = 1
        while Meal.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, counter)
            counter += 1
        return unique_slug

    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        self.slug = self.get_unique_slug()
        return super(Meal, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-publishing_date']


class Like(models.Model):
    user = models.ForeignKey(User, related_name='user_likes', on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='likes')
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "meal")


class Rate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='rates')
    points = models.IntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(1)])

    class Meta:
        unique_together = ("user", "meal")


class Comment(models.Model):
    meal = models.ForeignKey(Meal, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    content = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)