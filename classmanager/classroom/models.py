from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
import misaka
import re

# Name validator
def validate_name(value):
    """Validate that name contains only letters and spaces."""
    if not re.match(r"^[a-zA-Z\s]+$", value):
        raise ValidationError('Name must contain only letters and spaces.')
    if len(value.strip()) < 2:
        raise ValidationError('Name must be at least 2 characters long.')

# Phone number validator
def validate_phone_number(value):
    """Validate that phone number has exactly 10 digits."""
    if len(str(value)) > 10:
        raise ValidationError('Phone number must not exceed 10 digits.')
    if len(str(value)) < 10:
        raise ValidationError('Phone number must be at least 10 digits.')

# Positive number validator
def validate_positive_number(value):
    """Validate that the number is positive."""
    if value < 0:
        raise ValidationError('Number must be positive.')

# Create your models here.

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,related_name='Student')
    name=models.CharField(max_length=250, validators=[validate_name])
    roll_no = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.IntegerField(validators=[validate_phone_number], unique=True)
    student_profile_pic = models.ImageField(upload_to="classroom/student_profile_pic",blank=True)

    def get_absolute_url(self):
        return reverse('classroom:student_detail',kwargs={'pk':self.pk})

    def __str__(self):
        return self.name

    @classmethod
    def generate_roll_no(cls):
        """Generate a new unique roll number with prefix STU and zero-padded number.

        Scans existing roll_no values for numeric suffixes and increments the highest.
        Falls back to 'STU0001' when none found.
        """
        pattern = re.compile(r"(\d+)$")
        max_num = 0
        for rn in cls.objects.all().values_list('roll_no', flat=True):
            if not rn:
                continue
            m = pattern.search(rn)
            if m:
                try:
                    num = int(m.group(1))
                except ValueError:
                    continue
                if num > max_num:
                    max_num = num
        next_num = max_num + 1
        return f"STU{next_num:04d}"

    class Meta:
        ordering = ['roll_no']

class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,related_name='Teacher')
    name = models.CharField(max_length=250, validators=[validate_name])
    subject_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.IntegerField(validators=[validate_phone_number], unique=True)
    teacher_profile_pic = models.ImageField(upload_to="classroom/teacher_profile_pic",blank=True)
    class_students = models.ManyToManyField(Student,through="StudentsInClass")

    def get_absolute_url(self):
        return reverse('classroom:teacher_detail',kwargs={'pk':self.pk})

    def __str__(self):
        return self.name

class StudentMarks(models.Model):
    teacher = models.ForeignKey(Teacher,related_name='given_marks',on_delete=models.CASCADE)
    student = models.ForeignKey(Student,related_name="marks",on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=250)
    marks_obtained = models.IntegerField(validators=[validate_positive_number])
    maximum_marks = models.IntegerField(validators=[validate_positive_number])

    def __str__(self):
        return self.subject_name

class StudentsInClass(models.Model):
    teacher = models.ForeignKey(Teacher,related_name="class_teacher",on_delete=models.CASCADE)
    student = models.ForeignKey(Student,related_name="user_student_name",on_delete=models.CASCADE)

    def __str__(self):
        return self.student.name

    class Meta:
        unique_together = ('teacher','student')

class MessageToTeacher(models.Model):
    student = models.ForeignKey(Student,related_name='student',on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher,related_name='messages',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable=False)

    def __str__(self):
        return self.message

    def save(self,*args,**kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args,**kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['student','message']

class ClassNotice(models.Model):
    teacher = models.ForeignKey(Teacher,related_name='teacher',on_delete=models.CASCADE)
    students = models.ManyToManyField(Student,related_name='class_notice')
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable=False)

    def __str__(self):
        return self.message

    def save(self,*args,**kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args,**kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['teacher','message']

class ClassAssignment(models.Model):
    student = models.ManyToManyField(Student,related_name='student_assignment')
    teacher = models.ForeignKey(Teacher,related_name='teacher_assignment',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    assignment_name = models.CharField(max_length=250)
    assignment = models.FileField(upload_to='assignments')

    def __str__(self):
        return self.assignment_name

    class Meta:
        ordering = ['-created_at']

class SubmitAssignment(models.Model):
    student = models.ForeignKey(Student,related_name='student_submit',on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher,related_name='teacher_submit',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    submitted_assignment = models.ForeignKey(ClassAssignment,related_name='submission_for_assignment',on_delete=models.CASCADE)
    submit = models.FileField(upload_to='Submission')

    def __str__(self):
        return "Submitted"+str(self.submitted_assignment.assignment_name)

    class Meta:
        ordering = ['-created_at']
