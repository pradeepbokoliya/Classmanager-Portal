from django import forms
from django.contrib.auth.forms import UserCreationForm
from classroom.models import User,Teacher,Student,StudentMarks,MessageToTeacher,ClassNotice,ClassAssignment,SubmitAssignment
from django.db import transaction

## User Login Form (Applied in both student and teacher login)
class UserForm(UserCreationForm):
    class Meta():
        model = User
        fields = ['username','password1','password2']
        widgets = {
                'username': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter username', 'required':'required'}),
                'password1': forms.PasswordInput(attrs={'class':'answer', 'placeholder':'Enter password (min 8 chars)', 'required':'required'}),
                'password2': forms.PasswordInput(attrs={'class':'answer', 'placeholder':'Confirm password', 'required':'required'}),
                }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different username.')
        return username
        
## Teacher Registration Form 
class TeacherProfileForm(forms.ModelForm):
    class Meta():
        model =  Teacher
        fields = ['name','subject_name','phone','email']
        widgets = {
                'name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter full name', 'required':'required'}),
                'subject_name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter subject name', 'required':'required'}),
                'phone': forms.TextInput(attrs={'class':'answer', 'type':'tel', 'placeholder':'Enter 10-digit phone number', 'maxlength':'10', 'pattern':'[0-9]{10}', 'required':'required'}),
                'email': forms.EmailInput(attrs={'class':'answer', 'placeholder':'Enter valid email', 'required':'required'}),
                }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Teacher.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already registered.')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Teacher.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

## Teacher Profile Update Form
class TeacherProfileUpdateForm(forms.ModelForm):
    class Meta():
        model = Teacher
        fields = ['name','subject_name','email','phone','teacher_profile_pic']
        widgets = {
                'name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter full name', 'required':'required'}),
                'subject_name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter subject name', 'required':'required'}),
                'phone': forms.TextInput(attrs={'class':'answer', 'type':'tel', 'placeholder':'Enter 10-digit phone number', 'maxlength':'10', 'pattern':'[0-9]{10}', 'required':'required'}),
                'email': forms.EmailInput(attrs={'class':'answer', 'placeholder':'Enter valid email', 'required':'required'}),
                'teacher_profile_pic': forms.FileInput(attrs={'accept':'image/*'}),
                }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Teacher.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This phone number is already registered by another teacher.')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Teacher.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already registered by another teacher.')
        return email

## Student Registration Form
class StudentProfileForm(forms.ModelForm):
    class Meta():
        model =  Student
        fields = ['name','phone','email']
        widgets = {
            'name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter full name', 'required':'required'}),
            'phone': forms.TextInput(attrs={'class':'answer', 'type':'tel', 'placeholder':'Enter 10-digit phone number', 'maxlength':'10', 'pattern':'[0-9]{10}', 'required':'required'}),
            'email': forms.EmailInput(attrs={'class':'answer', 'placeholder':'Enter valid email', 'required':'required'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Student.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already registered.')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Student.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

## Student profile update form
class StudentProfileUpdateForm(forms.ModelForm):
    class Meta():
        model = Student
        fields = ['name','roll_no','email','phone','student_profile_pic']
        widgets = {
            'name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter full name', 'required':'required'}),
            'roll_no': forms.TextInput(attrs={'class':'answer', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class':'answer', 'placeholder':'Enter valid email', 'required':'required'}),
            'phone': forms.TextInput(attrs={'class':'answer', 'type':'tel', 'placeholder':'Enter 10-digit phone number', 'maxlength':'10', 'pattern':'[0-9]{10}', 'required':'required'}),
            'student_profile_pic': forms.FileInput(attrs={'accept':'image/*'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Student.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This phone number is already registered by another student.')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Student.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already registered by another student.')
        return email
        
## Form for uploading marks and also for updating it.
class MarksForm(forms.ModelForm):
    class Meta():
        model = StudentMarks
        fields = ['subject_name','marks_obtained','maximum_marks']
        widgets = {
            'subject_name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter subject name', 'required':'required'}),
            'marks_obtained': forms.NumberInput(attrs={'class':'answer', 'placeholder':'Enter marks obtained', 'min':'0', 'required':'required'}),
            'maximum_marks': forms.NumberInput(attrs={'class':'answer', 'placeholder':'Enter maximum marks', 'min':'0', 'required':'required'}),
        }

## Writing message to teacher        
class MessageForm(forms.ModelForm):
    class Meta():
        model = MessageToTeacher
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class':'answer', 'placeholder':'Write your message here...', 'rows':'5', 'required':'required'}),
        }

## Writing notice in the class        
class NoticeForm(forms.ModelForm):
    class Meta():
        model = ClassNotice
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class':'answer', 'placeholder':'Write notice message here...', 'rows':'5', 'required':'required'}),
        }

## Form for uploading or updating assignment (teachers only)       
class AssignmentForm(forms.ModelForm):
    class Meta():
        model = ClassAssignment
        fields = ['assignment_name','assignment']
        widgets = {
            'assignment_name': forms.TextInput(attrs={'class':'answer', 'placeholder':'Enter assignment name', 'required':'required'}),
            'assignment': forms.FileInput(attrs={'accept':'.pdf,.doc,.docx,.txt', 'required':'required'}),
        }

## Form for submitting assignment (Students only)        
class SubmitForm(forms.ModelForm):
    class Meta():
        model = SubmitAssignment
        fields = ['submit']
        widgets = {
            'submit': forms.FileInput(attrs={'accept':'.pdf,.doc,.docx,.txt,.zip', 'required':'required'}),
        }
