from django import forms

from booking.models import BookingSettings
from app.models import Employee,Detected
from booking.models import mydoc
import datetime
from collections import Counter

mydocss=(('EAR','EAR'),('EYE','EYES'),('HEART','HEART'))

class ChangeInputsStyle(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add common css classes to all widgets
        for field in iter(self.fields):
            # get current classes from Meta
            input_type = self.fields[field].widget.input_type
            classes = self.fields[field].widget.attrs.get("class")
            if classes is not None:
                classes += " form-check-input" if input_type == "checkbox" else " form-control  flatpickr-input"
            else:
                classes = " form-check-input" if input_type == "checkbox" else " form-control flatpickr-input"
            self.fields[field].widget.attrs.update({
                'class': classes
            })


class BookingDateForm(ChangeInputsStyle):
    date_formatted = datetime.datetime.today().date()
    a=Detected.objects.filter(time_stamp__date=date_formatted).order_by('time_stamp').reverse().values_list("emp_id",flat=True)
    date = forms.DateField(required=True)
    b=list(a)
    ch = Employee.objects.filter(id__in=b).values_list("name",flat=True)
    c=list(ch)
    # q=[(x,x) for x in c]
    o=[]
    t= mydoc.objects.all()[0]
    for i in range(0,len(c)):
        p=mydoc.objects.filter(created_att__date=date_formatted,doc=c[i]).values_list("doc",flat=True)
        r=list(p)
        for i in range(0,len(r)):
            o.append(r[i])
    counts = Counter(o)
    l=dict(counts)
    finaldoc=min(l, key=l.get)
    t.doc=finaldoc
    doc = forms.CharField(max_length=10,initial=finaldoc)
    t.save()
    # mytest=forms.CharField(max_length=100,initial=dict(counts))
    


class BookingTimeForm(ChangeInputsStyle):
    time = forms.TimeField(widget=forms.HiddenInput())

class BookingCustomerForm(ChangeInputsStyle):
    # doc = forms.ChoiceField(choices=mydocss)
    user_name = forms.CharField(max_length=250)
    user_email = forms.EmailField()
    user_mobile = forms.CharField(required=False, max_length=10)
    

class BookingSettingsForm(ChangeInputsStyle, forms.ModelForm):
    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))

    def clean(self):
        if "end_time" in self.cleaned_data and "start_time" in self.cleaned_data:
            if self.cleaned_data["end_time"] <= self.cleaned_data["start_time"]:
                raise forms.ValidationError(
                    "The end time must be later than start time."
                )
        return self.cleaned_data

    class Meta:
        model = BookingSettings
        fields = "__all__"
        exclude = [
            # TODO: Add this fields to admin panel and fix the functions
            "max_booking_per_time",
            "max_booking_per_day",
        ]
