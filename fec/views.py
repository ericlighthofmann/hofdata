from django.shortcuts import render

# Create your views here.

def summary_view(request):

    print ("request")

    return render(request, 'fec/summary_view.html', context)
