from materials.views.index import index


def search(request):

    return index(request, format="json")
