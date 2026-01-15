from .models import Category

# context processors provide data in all the templates. they have to be registered in
# settings.py templates. Now links will be available on all templates
def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
