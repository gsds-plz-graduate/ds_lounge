import json

from django.core.paginator import Paginator
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render

from check.models import Enrollment
from common.models import Profile


# Create your views here.
def home(request):
    return render(request, 'common/home.html')


def share(request):
    share_id = list(Profile.objects.filter(share_timetable = True).values_list('user_id', flat = True))
    rec_up_ids = list(Enrollment.objects.values('user_id').annotate(rec_up_id = Max('up_id')).values_list('rec_up_id', flat = True))
    share_list = Enrollment.objects.filter(up_id__in = rec_up_ids, user_id__in = share_id).values('user_id').annotate(rec_up_id = Max('up_id'))
    paginator = Paginator(share_list, 1)
    page_obj = paginator.page(request.GET.get('page', '1'))
    return render(request, 'common/share.html', {"page_obj": page_obj})


def inclugrd(request):
    post = json.loads(request.body)
    Profile.objects.filter(user = request.user.id).update(include_undergrad = post['include_undergrad'])
    return HttpResponse({"result": True})


def shreyn(request):
    post = json.loads(request.body)
    Profile.objects.filter(user = request.user.id).update(share_timetable = post['share_yn'])
    return HttpResponse({"result": True})
