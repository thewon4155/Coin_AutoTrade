from django.shortcuts import render
from django.http import JsonResponse
from .models import Signal

def index(request):
    signals = Signal.objects.all()  # Retrieve all signals
    return render(request, 'signals/index.html', {'signals': signals})

def chart_data(request):
    signals = Signal.objects.all().order_by('timestamp')
    data = {
        "timestamps": [signal.timestamp for signal in signals],
        "prices": [signal.price for signal in signals],
        "balances": [signal.balance for signal in signals],
        "actions": [signal.action for signal in signals]
    }
    return JsonResponse(data)

