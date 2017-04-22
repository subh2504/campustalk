from django.db import models


class ClgCourseDepart(models.Model):
    clg_cd_id = models.IntegerField(primary_key=True)
    college = models.ForeignKey('CollegeDetail')
    course = models.ForeignKey('MasterCourse')
    depart = models.ForeignKey('MasterDepart')

    def __str__(self):
        return self.college.college_name + " " + self.course.course_name + " " + self.depart.depart_name

    


class CollegeDetail(models.Model):
    college_id = models.IntegerField(primary_key=True)
    college_name = models.CharField(unique=True, max_length=100)
    college_address = models.CharField(max_length=100)
    college_pic = models.CharField(max_length=15)

    def __str__(self):
        return self.college_name

    


class Designation(models.Model):
    desig_id = models.IntegerField(primary_key=True)
    desig_name = models.CharField(unique=True, max_length=50)
    type = models.IntegerField()

    def __str__(self):
        return self.desig_name

    


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    


class GroupDetail(models.Model):
    group_id = models.IntegerField(primary_key=True)
    group_name = models.CharField(max_length=100)
    admin = models.ForeignKey('UserRegistration')
    no_of_member = models.IntegerField()
    creation_date = models.DateField()
    allow_msg = models.IntegerField()
    notification = models.IntegerField()

   


class GroupMember(models.Model):
    member_id = models.IntegerField(primary_key=True)
    group = models.ForeignKey('GroupDetail')
    enroll = models.ForeignKey('UserRegistration')

    


class Login(models.Model):
    login = models.OneToOneField('UserRegistration', primary_key=True)
    password = models.CharField(max_length=20, blank=True)

    


class MasterCourse(models.Model):
    course_id = models.IntegerField(primary_key=True)
    course_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.course_name

   


class MasterDepart(models.Model):
    depart_id = models.IntegerField(primary_key=True)
    depart_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.depart_name

    


class UserRegistration(models.Model):
    enroll_id = models.CharField(primary_key=True, max_length=15)
    email_id = models.CharField(unique=True, max_length=30)
    contact_no = models.CharField(max_length=10)
    desig = models.ForeignKey(Designation)
    name = models.CharField(max_length=30)
    college = models.ForeignKey(CollegeDetail)
    clg_cd = models.ForeignKey(ClgCourseDepart, blank=True, null=True)
    dob = models.DateField()

    gender = models.CharField(max_length=6)
    semester = models.CharField(max_length=20, blank=True)
    status = models.IntegerField(blank=True, null=True)
    manage_by = models.CharField(max_length=30, blank=True)
    registration_id = models.CharField(max_length=500)

    def __str__(self):
        return self.enroll_id + " " + self.contact_no

    


def GetImageFolder(instance, filename):
    return "%s" % (filename)


class ProfilePicDetail(models.Model):
    enroll = models.OneToOneField('UserRegistration', primary_key=True)
    pic_link = models.ImageField(blank=True, upload_to=GetImageFolder)

    def __str__(self):
        return self.enroll.enroll_id

    
