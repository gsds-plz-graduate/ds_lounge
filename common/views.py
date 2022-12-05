import json

from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views import generic

from check.models import Enrollment
from common.models import Profile
from excelupload.models import Document


# Create your views here.

class customHandler404(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, "error/404.html")


def handler500(request):
    response = render(request, "error/500.html")
    response.status_code = 500
    return response


def home(request):
    return render(request, 'common/home.html')


def share(request):
    # share_id = list(Profile.objects.filter(share_timetable = True).values_list('user_id', flat = True))
    # rec_up_ids = list(Enrollment.objects.values('user_id').annotate(rec_up_id = Max('up_id')).values_list('rec_up_id', flat = True))
    # share_list = Enrollment.objects.filter(up_id__in = rec_up_ids, user_id__in = share_id).values('user_id').annotate(rec_up_id = Max('up_id'))
    share_id_list = Profile.objects.filter(share_timetable = True)
    paginator = Paginator(share_id_list, 10)
    page_obj = paginator.page(request.GET.get('page', '1'))
    return render(request, 'common/share.html', {"page_obj": page_obj})


def sharedetail(request, user_id):
    try:
        share_timetable = Profile.objects.filter(user_id = user_id).latest('updated_at').share_timetable
        if share_timetable:
            recent_up_id = Document.objects.filter(user_id = user_id).latest('updated_at').up_id
            recent_enrollments = (Enrollment.objects.filter(up_id__exact = recent_up_id).values("year", "cid", "cname", "crd", "gbn"))
            return render(request, 'common/sharedetail.html', {"recent_enrollments": recent_enrollments})
        else:
            raise Http404("This user didn't allowed to share timetable")
    except Profile.DoesNotExist:
        raise Http404("This user didn't allowed to share timetable")


def inclugrd(request):
    post = json.loads(request.body)
    Profile.objects.filter(user = request.user.id).update(include_undergrad = post['include_undergrad'])
    return HttpResponse({"result": True})


def shreyn(request):
    post = json.loads(request.body)
    Profile.objects.filter(user = request.user.id).update(share_timetable = post['share_yn'])
    return HttpResponse({"result": True})
