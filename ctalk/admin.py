from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(CollegeDetail)
admin.site.register(ClgCourseDepart)
admin.site.register(Designation)
admin.site.register(GroupDetail)
admin.site.register(GroupMember)
admin.site.register(Login)
admin.site.register(MasterCourse)
admin.site.register(MasterDepart)
admin.site.register(UserRegistration)
admin.site.register(ProfilePicDetail)