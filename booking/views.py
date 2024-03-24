import datetime
from typing import Dict, List

from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic import (DeleteView, ListView, TemplateView,
                                  UpdateView, View)
from formtools.wizard.views import SessionWizardView

from booking.forms import (BookingCustomerForm, BookingDateForm,
                           BookingSettingsForm, BookingTimeForm)
from booking.models import Booking, BookingSettings,mydoc
from booking.settings import (BOOKING_BG, BOOKING_DESC, BOOKING_DISABLE_URL,
                              BOOKING_SUCCESS_REDIRECT_URL, BOOKING_TITLE,
                              PAGINATION)
from booking.utils import BookingSettingMixin
from app.models import Employee, Detected, clients ,allocation
import datetime
from datetime import timedelta
from django.utils import timezone



def bookings(request):
    print('booking')
    b = Employee.objects.filter().values('name')
    
    if request.method == 'POST':
        nam = request.POST['nam']
        phone = request.POST['phone']
        des = request.POST['des']
        special = request.POST['special']
        a= clients.objects.create()
        b= allocation.objects.create()
        emp = Employee.objects.filter(specialist = special).values('name','count')
        for i in range(1,len(emp)):
            if emp[i]['count'] is None:
                we = emp[i]['name']
                b.emp_id = we
                b.client_BT = nam
                b.alloca_time = datetime.datetime.now(tz=timezone.utc)
                b.save()
                s=Employee.objects.filter(name=we).values_list('count')
                wee = s[0][0]
                com=Employee.objects.filter(name=we).update(count = wee+1)
            else:
                res = issame(special)
                emp1 = Employee.objects.filter(specialist = special).values_list('name','count')     
                if res == True:
                    you = emp1[0][0]
                    b.emp_id = you
                    b.client_BT = nam
                    b.alloca_time = datetime.datetime.now(tz=timezone.utc)
                    b.save()
                    w=Employee.objects.filter(name=you).values_list('count')
                    youu = w[0][0]
                    com=Employee.objects.filter(name=you).update(count = youu+1)

                if res == False:
                    for j in range(1,len(emp1)):
                        if emp1[j][1] == emp1[0][1]:
                            print('yes')
                        else:
                            you1 = emp1[j][0]
                            b.emp_id = you1
                            b.client_BT = nam
                            b.save()
                            b.alloca_time = datetime.datetime.now(tz=timezone.utc)
                            w=Employee.objects.filter(name=you1).values_list('count')
                            youu1 = w[0][0]
                            com=Employee.objects.filter(name=you1).update(count =youu1+1)
        print(allocation.objects.filter(pk=14).values('alloca_time'))
        a.clients = nam
        a.clients_des = des
        a.clients_mob = phone
        a.client_BT = datetime.datetime.today()
        gg = datetime.timedelta(minutes=30)
        booking2(a.client_BT+gg)
        a.save()
        return render(request, 'app/admin.html')
    return render(request, 'app/booking.html')

def booking2(bt):
    print(bt)
    btime = bt
    x=btime.time()
    h=x.hour
    y=x.minute
    print(format(h),":",format(y))

def issame(special):
    res = False
    emp = Employee.objects.filter(specialist = special).values('name','count')
    emp1 = Employee.objects.filter(specialist = special).values_list('name','count')
    for i in range(0, len(emp)):
        print(emp1[i][1])
        if emp1[i][1]==emp1[0][1]:
              res = True
              print('same')
        else:
            res = False
            print("no")
    return res

class BookingHomeView(BookingSettingMixin, TemplateView):
    model = Booking
    template_name = "booking/admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_bookings"] = Booking.objects.filter().order_by(
            "date", "time")[:10]
        context["waiting_bookings"] = Booking.objects.filter(
            approved=False).order_by("-date", "time")[:10]
        return context


class BookingListView(BookingSettingMixin, ListView):
    model = Booking
    template_name = "booking/admin/booking_list.html"
    paginate_by = PAGINATION


class BookingSettingsView(BookingSettingMixin, UpdateView):
    form_class = BookingSettingsForm
    template_name = "booking/admin/booking_settings.html"

    def get_object(self):
        return BookingSettings.objects.filter().first()

    def get_success_url(self):
        return reverse("booking_settings")


class BookingDeleteView(BookingSettingMixin, DeleteView):
    mdoel = Booking
    success_url = reverse_lazy('booking_list')
    queryset = Booking.objects.filter()


class BookingApproveView(BookingSettingMixin, View):
    mdoel = Booking
    success_url = reverse_lazy('booking_list')
    fields = ("approved",)

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs.get("pk"))
        booking.approved = True
        booking.save()

        return redirect(self.success_url)


# # # # # # # #
# Booking Part
# # # # # # # #
BOOKING_STEP_FORMS = (
    ('Date', BookingDateForm),
    ('Time', BookingTimeForm),
    ('User Info', BookingCustomerForm)
)


class BookingCreateWizardView(SessionWizardView):
    template_name = "booking/user/booking_wizard.html"
    form_list = BOOKING_STEP_FORMS

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        progress_width = "6"
        # print(context)
        # print(form)
        if self.steps.current == 'Time':
            context["get_available_time"] = get_available_time(
                self.get_cleaned_data_for_step('Date')["date"])
            # print(context)
            progress_width = "30"
        if self.steps.current == 'User Info':
            progress_width = "75"
        context.update({
            'booking_settings': BookingSettings.objects.first(),
            "progress_width": progress_width,
            "booking_bg": BOOKING_BG,
            "description": BOOKING_DESC,
            "title": BOOKING_TITLE

        })
        # print(context)
        return context

    def render(self, form=None, **kwargs):
        # Check if Booking is Disable
        form = form or self.get_form()
        context = self.get_context_data(form=form, **kwargs)

        if not context["booking_settings"].booking_enable:
            return redirect(BOOKING_DISABLE_URL)

        return self.render_to_response(context)

    def done(self, form_list, **kwargs):
        data = dict((key, value) for form in form_list for key,
                    value in form.cleaned_data.items())
        # print(data)
        booking = Booking.objects.create(**data)
        date_formatted = datetime.datetime.today().date()
        det_list = Detected.objects.filter(time_stamp__date=date_formatted).order_by('time_stamp').reverse()
        for det in det_list:
            beep=det.emp_id
        date_formatted1 = datetime.datetime.strptime(str(date_formatted), "%Y-%m-%d").date()
        print(type(str(beep)))
        a=mydoc.objects.create(doc=str(beep),booking_id=booking.id,created_att=date_formatted1)
        a.save()
        print('kkm',booking.doc)
        if BOOKING_SUCCESS_REDIRECT_URL:
            return redirect(BOOKING_SUCCESS_REDIRECT_URL)

        return render(self.request, 'booking/user/booking_done.html', {
            "progress_width": "100",
            "booking_id": booking.id,
            "booking_bg": BOOKING_BG,
            "description": BOOKING_DESC,
            "title": BOOKING_TITLE
        })


def add_delta(time: datetime.time, delta: datetime.datetime) -> datetime.time:
    # transform to a full datetime first
    return (datetime.datetime.combine(
        datetime.date.today(), time
    ) + delta).time()


def get_available_time(date: datetime.date) -> List[Dict[datetime.time, bool]]:
    """
    Check for all available time for selected date
    The times should ne betwwen start_time and end_time
    If the time already is taken -> is_taken = True
    """
    booking_settings = BookingSettings.objects.first()
    t=mydoc.objects.all()[0]
    existing_bookings = Booking.objects.filter(
        date=date,doc=t.doc).values_list('time')
    print(t.booking_id)

    next_time = booking_settings.start_time   #pin 1
    time_list = []
    while True:
        is_taken = any([x[0] == next_time for x in existing_bookings])
        time_list.append(
            {"time": ":".join(str(next_time).split(":")[:-1]), "is_taken": is_taken})
        next_time = add_delta(next_time, datetime.timedelta(
            minutes=int(booking_settings.period_of_each_booking)))
        if next_time > booking_settings.end_time:
            break

    return time_list

