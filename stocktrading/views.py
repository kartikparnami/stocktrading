from django.shortcuts   import render


def homepage(request):
    return render(request, 'order_entry/homepage.html', {})