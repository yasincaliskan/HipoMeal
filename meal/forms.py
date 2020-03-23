from django import forms
from .models import Meal, Ingredient, Comment


class MealForm(forms.ModelForm):

    class Meta:
        model = Meal
        fields = [
            'title',
            'description',
            'difficulty',
            'category',
            'image',
            'ingredients',
        ]


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            'name'
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'name',
            'content'
        ]