from django import forms

from .models import Employee

docchoice=(
	('Cardiologists','Cardiologists'),
	('Dentist','Dentist'),
	('ENT Specialist','ENT Specialist'),
	('Gynecologist','Gynecologist'),
	('Orthopedic Surgeon','Orthopedic Surgeon'),
	('Paediatrician','Paediatrician'),
	('Psychiatrists','Psychiatrists'),
	('Veterinarian','Veterinarian'),
	('Radiologist','Radiologist'),
	('Pulmonologist','Pulmonologist'),
	('Endocrinologist','Endocrinologist'),
	('Oncologist','Oncologist'),
	('Neurologist','Neurologist')
)
ch = (('EAR','EAR'),('EYE','EYES'),('HEART','HEART'))
class EmployeeForm(forms.ModelForm):

    specialist = forms.ChoiceField(choices=docchoice)

    class Meta:
        model = Employee
        fields = ('id', 'name','specialist')