from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from .models import Company, Team, Pbi, Sprint
from django.views import generic
from .forms import CompanyForm, SprintForm , TeamForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .serializers import CompanySerializer, PbiSerializer
import logging, datetime
from datetime import date, datetime, time, timedelta
from rest_framework.decorators import api_view

# Create your views here.

logger = logging.getLogger(__name__)

class IndexView(generic.ListView):
    template_name = 'burnDown/oldindex.html'
    context_object_name = 'companies_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Company.objects.order_by('-create_date')[:5]

def indexSprints(request):
    try:
        sprints = Sprint.objects.all().order_by('-end_date')
        #logger.error(sprint)
        return render(request, 'burnDown/index.html', {
            'sprints' : sprints,
        })
    except ObjectDoesNotExist:
        sprints = None
        return render(request, 'burnDown/index.html', {
            'sprints' : sprints,
        })
        
        
def indexBurnDown(request, sprint_id):
    try:
        sprint = Sprint.objects.get(pk=sprint_id)
        #logger.error(sprint)
        #pbis = Pbi.objects.filter(sprint=sprint).order_by('snapshot_date')
        _pbis = Pbi.objects.values('snapshot_date').annotate(spcount=Sum('story_points')).filter(sprint=sprint,pbi_type='US').exclude(state='CLOSED').exclude(state='RESOLVED').order_by('snapshot_date')
        pbis = list(_pbis)
        delta = sprint.end_date - sprint.start_date
        
        for i in range(delta.days + 1):
            print(sprint.start_date + timedelta(i))
            print(i)
            if (sprint.start_date + timedelta(i)).weekday() < 5 :
                if i >= len(pbis):
                    break
                if pbis[i]['snapshot_date'] == sprint.start_date + timedelta(i):
                    continue
                elif i > 0:
                    pbis.insert(i, {'snapshot_date': sprint.start_date + timedelta(i), 'spcount': 'null'})
                else:
                    pbis.insert(i, {'snapshot_date': sprint.start_date + timedelta(i), 'spcount': 0})
    
#         for pbi in pbis :
#             if pbi['snapshot_date'] == sprint.start_date:
#                 logger.debug('pouet')
            
            
        #logger.error(pbis)
        return render(request, 'burnDown/indexBurnDown.html', {
            'sprint' : sprint,
            'pbis': pbis,
        })
    except ObjectDoesNotExist:
        sprint = None
        return render(request, 'burnDown/indexBurnDown.html', {
            'sprint' : sprint,
        })

def EditView(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
        form = CompanyForm(instance=company)
        return render(request, 'burnDown/edit.html', {
            'company' : company,
            'form' : form
        })
    except ObjectDoesNotExist:
        company = None
        return render(request, 'burnDown/edit.html', {
            'company' : company,
            'error_message': "You didn't select a choice.",
        })

def ValidateView(request, company_id):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CompanyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CompanyForm()    
    return render(request, 'burnDown/mytests.html', {
            'myFormSet' : form,
            'error_message': "You didn't select a choice.",
        })


class DetailView(generic.DetailView):
    model = Company
    template_name = 'burnDown/detail.html'


class ResultsView(generic.DetailView):
    model = Company
    template_name = 'burnDown/results.html'


def vote(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    try:
        selected_team = company.team_set.get(pk=request.POST['team'])
    except (KeyError, Team.DoesNotExist):
        # Redisplay the team voting form.
        return render(request, 'burnDown/detail.html', {
            'company': company,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_team.pouet += 1
        selected_team.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('burnDown:results', args=(company.id,)))

def mytests(request):    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SprintForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SprintForm()    
    return render(request, 'burnDown/mytests.html', {
            'myFormSet' : form,
            'error_message': "You didn't select a choice.",
        })

#csrf_exempt should be renoved, add an aythent token
@csrf_exempt
def companies_list(request):
    """
    List all companies, or create a new company.
    """
    if request.method == 'GET':
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)

        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CompanySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


#csrf_exempt should be renoved, add an aythent token
@csrf_exempt
def company_detail(request, pk):
    """
    Retrieve, update or delete a company.
    """
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = CompanySerializer(company)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = CompanySerializer(company, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        company.delete()
        return HttpResponse(status=204)

#csrf_exempt should be renoved, add an aythent token
@csrf_exempt
@api_view(['GET', 'POST'])
def pbi_list(request):
    """
    List all pbis, or create a new pbis.
    """
    if request.method == 'GET':
        serializer = PbiSerializer(Pbi.get_all_pbis(), many=True)
        #logger.error(serializer.data)
        return JsonResponse(serializer.data , safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        #many=true implies we ALWAYS have an arry
        serializer = PbiSerializer(data=data, many=True)

        if serializer.is_valid():
#             Pbi.updateSerializedPbis(serializer.validated_data)
            for vData in serializer.validated_data:
                #logger.error(vData)
                _local_id = vData.get("local_id",None)
                _snapshot_date = vData.get("snapshot_date",None)
                #useless, is_valid should have checked that
                if ( _local_id != None and _local_id != '' ) and ( _snapshot_date != None and _snapshot_date != ''):
                    Pbi.objects.filter(local_id=_local_id, snapshot_date=_snapshot_date).delete()            
              
            serializer.save()
                
            return HttpResponse(status=200)
        return JsonResponse(serializer.errors, status=400, safe=False)


#csrf_exempt should be renoved, add an aythent token
@csrf_exempt
def pbi_list_date(request, sprint_id):
    """
    List all pbis, or create a new pbis.
    """

    d = datetime.strptime( request.GET['_date'], "%d %m %Y" )
    

    sprint = Sprint.objects.get(pk=sprint_id)
    
    if request.method == 'GET':
        pbis = Pbi.objects.filter(sprint=sprint,pbi_type='US',snapshot_date=d.strftime("%Y-%m-%d")).order_by('-pbi_type' ,'local_id')
        serializer = PbiSerializer(data=pbis, many=True)
        serializer.is_valid()
        return JsonResponse(serializer.data, safe=False)

#     elif request.method == 'POST':
#         data = JSONParser().parse(request)
#         serializer = PbiSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)
