from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from modules.core.extras import clean_domain

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class HomePageView(TemplateView):
	def get(self, request, **kwargs):
		return render(request, 'index.html', context=None)

	def post(self, request, **kwargs):
		_clean_url = "https://%s"%(clean_domain(request.get_host()))

		return HttpResponseRedirect(_clean_url)


@csrf_exempt
def handle404(request, exception):
	return render(request, 'index.html', context=None)