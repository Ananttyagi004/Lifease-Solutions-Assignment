from django.shortcuts import render
from .models import Match

def match_list(request):
    matches = Match.objects.all()
    return render(request, 'matches/match_list.html', {'matches': matches})
