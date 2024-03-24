from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from .facerec.faster_video_stream import stream
from .facerec.click_photos import click
from .facerec.train_faces import trainer
from .models import Employee, Detected, clients ,allocation,hpadmin
from .forms import EmployeeForm
import cv2
import pickle
import face_recognition
import datetime
from cachetools import TTLCache
from datetime import timedelta
from booking import views as views2
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from booking.utils import BookingSettingMixin
from django.views.generic import (DeleteView, ListView, TemplateView,
                                  UpdateView, View)
                                
from booking.models import mydoc


cache = TTLCache(maxsize=20, ttl=60)


# def bookings(request):
#     print('booking')
#     b = Employee.objects.filter().values('name')
    
#     if request.method == 'POST':
#         nam = request.POST['nam']
#         phone = request.POST['phone']
#         des = request.POST['des']
#         special = request.POST['special']
#         a= clients.objects.create()
#         b= allocation.objects.create()
#         emp = Employee.objects.filter(specialist = special).values('name','count')
#         for i in range(1,len(emp)):
#             if emp[i]['count'] is None:
#                 we = emp[i]['name']
#                 b.emp_id = we
#                 b.client_BT = nam
#                 b.alloca_time = datetime.datetime.now(tz=timezone.utc)
#                 b.save()
#                 s=Employee.objects.filter(name=we).values_list('count')
#                 wee = s[0][0]
#                 com=Employee.objects.filter(name=we).update(count = wee+1)
#             else:
#                 res = issame(special)
#                 emp1 = Employee.objects.filter(specialist = special).values_list('name','count')     
#                 if res == True:
#                     you = emp1[0][0]
#                     b.emp_id = you
#                     b.client_BT = nam
#                     b.alloca_time = datetime.datetime.now(tz=timezone.utc)
#                     b.save()
#                     w=Employee.objects.filter(name=you).values_list('count')
#                     youu = w[0][0]
#                     com=Employee.objects.filter(name=you).update(count = youu+1)

#                 if res == False:
#                     for j in range(1,len(emp1)):
#                         if emp1[j][1] == emp1[0][1]:
#                             print('yes')
#                         else:
#                             you1 = emp1[j][0]
#                             b.emp_id = you1
#                             b.client_BT = nam
#                             b.save()
#                             b.alloca_time = datetime.datetime.now(tz=timezone.utc)
#                             w=Employee.objects.filter(name=you1).values_list('count')
#                             youu1 = w[0][0]
#                             com=Employee.objects.filter(name=you1).update(count =youu1+1)
#         print(allocation.objects.filter(pk=14).values('alloca_time'))
#         a.clients = nam
#         a.clients_des = des
#         a.clients_mob = phone
#         a.client_BT = datetime.datetime.today()
#         gg = datetime.timedelta(minutes=30)
#         booking2(a.client_BT+gg)
#         a.save()
#         return render(request, 'app/admin.html')
#     return render(request, 'app/booking.html')

# def booking2(bt):
#     print(bt)
#     btime = bt
#     x=btime.time()
#     h=x.hour
#     y=x.minute
#     print(format(h),":",format(y))

# def issame(special):
#     res = False
#     emp = Employee.objects.filter(specialist = special).values('name','count')
#     emp1 = Employee.objects.filter(specialist = special).values_list('name','count')
#     for i in range(0, len(emp)):
#         print(emp1[i][1])
#         if emp1[i][1]==emp1[0][1]:
#               res = True
#               print('same')
#         else:
#             res = False
#             print("no")
#     return res
   

emplist=[]

def admin(request):
    if request.method == 'POST':
        return render(request,'app/booking.html')
    return render(request,'app/admin.html')

class adminstra(BookingSettingMixin,TemplateView):
    template_name = "app/admin1.html"

def identify1(frame, name, buf, buf_length, known_conf):

    if name in cache:
        return
    count = 0
    for ele in buf:
        count += ele.count(name)
    
    if count >= known_conf:
        timestamp = datetime.datetime.now(tz=timezone.utc)
        print(name, timestamp)
        cache[name] = 'detected'
        path = 'detected/{}_{}.jpg'.format(name, timestamp)
        write_path = 'media/' + path
        cv2.imwrite(write_path, frame)
        try:
            emp = Employee.objects.get(name=name)
            emp.detected_set.create(time_stamp=timestamp, photo=path)
        except:
            pass 	        




def predict(rgb_frame, knn_clf=None, model_path=None, distance_threshold=0.5):

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Load image file and find face locations
    # X_img = face_recognition.load_image_file(X_img_path)
    X_face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=2)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test iamge
    faces_encodings = face_recognition.face_encodings(rgb_frame, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]
    # print(closest_distances)
    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]



def identify_faces(video_capture):

    buf_length = 10
    known_conf = 6
    buf = [[]] * buf_length
    i = 0

    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = small_frame[:, :, ::-1]

        if process_this_frame:
            predictions = predict(rgb_frame, model_path="app/facerec/models/trained_model.clf")
            # print(predictions)

        process_this_frame = not process_this_frame

        face_names = []

        for name, (top, right, bottom, left) in predictions:

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            identify1(frame, name, buf, buf_length, known_conf)

            face_names.append(name)

        buf[i] = face_names
        i = (i + 1) % buf_length


        # print(buf)


        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()



def index(request):
    a=datetime.datetime.now()
    # print(a.strftime("%M"))
    if(request.method=='POST'):
        user=request.POST.get('username')
        passw=request.POST.get('pass')
        if hpadmin.objects.filter(username=user,password=passw).exists():
            return render(request,'app/index.html')
    return render(request, 'app/booking1.html')


def video_stream(request):
    stream()
    return HttpResponseRedirect(reverse('index'))


def add_photos(request):
	emp_list = Employee.objects.all()
	return render(request, 'app/add_photos.html', {'emp_list': emp_list})


def click_photos(request, emp_id):
	cam = cv2.VideoCapture(0)
	emp = get_object_or_404(Employee, id=emp_id)
	click(emp.name, emp.id, cam)
	return HttpResponseRedirect(reverse('add_photos'))


def train_model(request):
	trainer()
	return HttpResponseRedirect(reverse('index'))


def detected(request):
	if request.method == 'GET':
		date_formatted = datetime.datetime.today().date()
		date = request.GET.get('search_box', None)
		if date is not None:
			date_formatted = datetime.datetime.strptime(date, "%Y-%m-%d").date()
		det_list = Detected.objects.filter(time_stamp__date=date_formatted).order_by('time_stamp').reverse()

	# det_list = Detected.objects.all().order_by('time_stamp').reverse()
	return render(request, 'app/detected.html', {'det_list': det_list, 'date': date_formatted})


def identify(request):
	video_capture = cv2.VideoCapture(0)
	identify_faces(video_capture)
	return HttpResponseRedirect(reverse('index'))

def staff(request):
    if request.method == 'POST':
        staffs= Employee.objects.filter(name=request.POST.get('user')).values()
        bookings = mydoc.objects.filter(doc=request.POST.get('user')).values()
        print(bookings)
        return render(request,"app/staff.html",{'staffs':staffs,'bookings':bookings})
    return render(request,"app/staff.html")

def add_emp(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            print('hello')
            emp = form.save()
            # post.author = request.user
            # post.published_date = timezone.now()
            # post.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = EmployeeForm()
    return render(request, 'app/add_emp.html', {'form': form})




