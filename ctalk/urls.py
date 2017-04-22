"""campustalk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    
    url(r'^check_status/', views.check_status),
    url(r'^login/', views.login),
    url(r'^user_registration/', views.user_registration),
    # url(r'^clg/', views.master_clg_info),
    url(r'^rc/', views.register_course),
    url(r'^gud/', views.get_user_data),
    url(r'^clg/', views.meta_clg_data),
    url(r'^svl/', views.send_verification_list),
    url(r'^verification/', views.verification),
    url(r'^dv/', views.delete_verification),
    url(r'^upl/', views.user_profile_list),
    url(r'^uop/', views.update_own_prof),
    url(r'^mpl/', views.manage_profile_list),
    url(r'^smp/', views.show_manage_profile),
    url(r'^mpu/', views.manage_prof_update),
    url(r'^delete_prof/', views.delete_prof),
    url(r'^upl/', views.user_profile_list),
    url(r'^uop/', views.update_own_prof),
    url(r'^cgl/', views.create_group_list),
    url(r'^create_group/', views.create_group),
    url(r'^delete_group/', views.delete_group),
    url(r'^group_setting/', views.group_setting),
    url(r'^anm/', views.add_new_member),
    url(r'^dem/', views.delete_exist_member),
    url(r'^gri/', views.get_reg_id),
    url(r'^gl/', views.group_list),
    url(r'^send/', views.send),
    url(r'^ui/', views.uploaded_images),
    # url(r'^fpr/', views.fetch_principal_record),
    # url(r'^ftr/', views.fetch_tpo_record),
    # url(r'^fhr/', views.fetch_hod_record),
    # url(r'^ffr/', views.fetch_faculty_record),
    # url(r'^fsr/', views.fetch_student_record),
    url(r'^test/', views.test),
]