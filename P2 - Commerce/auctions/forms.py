from django import forms
from .models import Categories


class NewListingForm(forms.Form):
    # generates tuple list for choice field
    def generate_category_list():
        categories = Categories.objects.all()
        category_tuple_list = []

        for category in categories:
            category_tuple_list.append((category.pk, category.category))
        return category_tuple_list

    # form fields
    title = forms.CharField(label='Title', max_length=100)
    description = forms.CharField(label='Desctiption', widget=forms.Textarea, max_length=700)
    price = forms.FloatField(label='Starting price')
    url = forms.URLField(label='Image URL (optional)', widget=forms.URLInput, required=False)
    category = forms.ChoiceField(label='Category', choices=generate_category_list())