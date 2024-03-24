from django.db import models
from datetime import datetime
import os

# Create your models here.

# sex_choice = (
#     ('Male', 'Male'),
#     ('Female', 'Female')
# )

class Employee(models.Model):
	id = models.CharField(primary_key=True, max_length=10)
	name = models.CharField(max_length=50)
	count= models.IntegerField(max_length=50,null=True)
	specialist = models.CharField(max_length=10 , null=True)
	# contact_number = models.CharField(max_length=50)
	# date_of_birth = models.CharField(max_length=50)
	# date_of_joining = models.CharField(max_length=50)
	# department = models.CharField(max_length=50)
	# designation = models.CharField(max_length=50)
	# gender = models.CharField(max_length=50, choices=sex_choice, default='Male')
	# team = models.CharField(max_length=50)

	def __str__(self):
		return self.name

	def num_photos(self):
		try:
			DIR = f"app/facerec/dataset/{self.name}_{self.id}"
			img_count = len(os.listdir(DIR))
			return img_count
		except:
			return 0 
	class meta:
		abstract=True


class Detected(models.Model):
	emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
	time_stamp = models.DateTimeField()
	photo = models.ImageField(upload_to='detected/', default='app/facerec/detected/noimg.png')

	def __str__(self):
		emp = Employee.objects.get(name=self.emp_id)
		return f"{emp.name} {self.time_stamp}"


class clients(models.Model):
	emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
	clients = models.CharField(max_length=10)
	clients_mob = models.IntegerField(max_length=10 , null=True)
	clients_des = models.CharField(max_length=50 , null=True)
	client_BT = models.DateTimeField(null=True)

	def __str__(self):
		return self.clients

	

class allocation(models.Model):
	client_BT = models.CharField(max_length=100 , null=True)
	emp_id = models.CharField(max_length=100 ,null=True)
	count = models.IntegerField(max_length=10 , null=True)
	alloca_time = models.DateTimeField(null=True)

class hpadmin(models.Model):
	username=models.CharField(max_length=20)
	password=models.CharField(max_length=20)
	
