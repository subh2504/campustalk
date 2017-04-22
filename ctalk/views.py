from django.shortcuts import render

from django.http import HttpResponse
from django.core import serializers
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from django.core.files.base import ContentFile
from django.db.models import Q
from django.db import Error
from django.conf import settings
import os
import base64
from .models import *
import json
import requests



@csrf_exempt
def check_status(request):
    m = {}
    try:
        mob = str(request.POST['mob'])
    except ValueError:
        m["Success"] = 2
        return HttpResponse(json.dumps(m))
    s = UserRegistration.objects.filter(contact_no=str(mob))
    if (s.exists()):
        m["desig"] = str(Designation.objects.filter(desig_id=s[0].desig_id)[0].desig_name)
        m["name"] = str(s[0].name)
        m['mob'] = str(s[0].contact_no)
        m['enroll_id'] = str(s[0].enroll_id)
        m['email_id'] = str(s[0].email_id)
        m['college'] = str(s[0].college.college_name)
        m['img'] = str(ProfilePicDetail.objects.filter(enroll_id=s[0].enroll_id)[0].pic_link.url)
        m["Success"] = 1
        m["Status"] = int(s[0].status)
    else:
        m["Success"] = 0
    return HttpResponse(json.dumps(m))


@csrf_exempt
def register_course(request):
    try:
        clg_name = str(request.POST['clg_name'])
        course_name = str(request.POST['course'])
        depart_name = str(request.POST['depart'])
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        ccd = {}
        clg_id = CollegeDetail.objects.values_list('college_id', flat=True).filter(college_name=str(clg_name))
        course_id = MasterCourse.objects.values_list('course_id', flat=True).filter(course_name=str(course_name))
        depart_id = MasterDepart.objects.values_list('depart_id', flat=True).filter(depart_name=str(depart_name))
        rg_course = ClgCourseDepart.objects.filter(college_id=int(clg_id[0]), course_id=int(course_id[0]),
                                                   depart_id=int(depart_id[0]))  # course already present
        if not (rg_course.exists()):
            clg_cd = ClgCourseDepart.objects.create(college_id=int(clg_id[0]), course_id=int(course_id[0]),
                                                    depart_id=int(
                                                        depart_id[0]))  # list out of index error if wrong fill
            if clg_cd > 0:
                ccd['success'] = 1
                ccd['success_msg'] = "Course Registered Successfully..."

            else:
                ccd['success'] = 0
                ccd['success_msg'] = "Course Not Registered..."
        else:
            ccd['success'] = 0
            ccd['success_msg'] = "Course Already Registered..."
        return HttpResponse(json.dumps(ccd))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
# shows registered clgs with courses and depart...clg->course->branch
def meta_clg_data(request):
    x = {}
    y = {}
    p = []
    a = {}
    data = {}
    clg_info = {}
    try:
        clg = CollegeDetail.objects.all()
        course = MasterCourse.objects.all()
        depart = MasterDepart.objects.all()
        ccd = ClgCourseDepart.objects.all()

        for i in clg:
            tempc = ccd.filter(college=i.college_id)
            temp = tempc.order_by().values('course').distinct()
            for co in temp:
                tempb = tempc.filter(course=co['course'])
                co_name = course.values('course_name').filter(course_id=co['course'])
                for b in tempb:
                    dp = depart.values('depart_name').filter(depart_id=b.depart_id)
                    for d in dp:
                        p.append(str(d['depart_name']))
                for cn in co_name:
                    x[str(cn['course_name'])] = p
                    p = []
            y[str(i.college_name)] = x
            x = {}
        clg_info['college'] = y
        y = {}
        if clg_info:
            a['sucess'] = 1
            a['msg'] = "got college informantion..."
            # data==serializers.serialize('json',tempc)
            return HttpResponse(json.dumps(clg_info))
        else:
            a['sucess'] = 0
            a['msg'] = "no college informantion..."
            return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def get_user_data(request):  # single prof
    prof_list = {}
    a = {}
    enroll_id = str(request.POST['enroll_id'])
    try:
        p_user = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)
        if p_user.exists():
            prof_list['enroll_id'] = str(p_user[0].enroll_id)
            prof_list['email_id'] = str(p_user[0].email_id)
            prof_list['name'] = str(p_user[0].name)
            prof_list['dob'] = str(p_user[0].dob)
            prof_list['gender'] = str(p_user[0].gender)
            prof_list['mob'] = str(p_user[0].contact_no)
            prof_list['desig'] = str(p_user[0].desig.desig_name)
            prof_list['college'] = str(p_user[0].college.college_name)
            prof_list['pic_link'] = str(ProfilePicDetail.objects.filter(enroll_id=p_user[0].enroll_id)[0].pic_link.url)
            if (p_user[0].clg_cd_id):
                prof_list['course'] = str(
                    ClgCourseDepart.objects.filter(clg_cd_id=p_user[0].clg_cd_id)[0].course.course_name)
                prof_list['department'] = str(
                    ClgCourseDepart.objects.filter(clg_cd_id=p_user[0].clg_cd_id)[0].depart.depart_name)

            else:
                prof_list['course'] = str("")
                prof_list['department'] = str("")
            prof_list['semester'] = str(p_user[0].semester)
            a['user_prof_record'] = prof_list
            a['success'] = 1
            a['msg'] = "User list.."
        else:
            a['success'] = 0
            a['msg'] = "sorry no records fetched error:User not present ..."  # if enroll_id is not given... no user
        # data=serializers.serialize('json',p_user)
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def user_registration(request):
    reg = {}
    try:
        enroll_id = str(request.POST['enroll_id']).upper()
        email_id = str(request.POST['email_id'])
        mob = str(request.POST['mob'])
        desig_name = str(request.POST['desig'])
        name = str(request.POST['name'])
        clg_name = str(request.POST['college'])
        dob = str(request.POST['dob'])
        # dob="1990-2-3"
        course_name = str(request.POST['course'])
        depart_name = str(request.POST['depart'])
        gender = str(request.POST['gender'])
        semester = str(request.POST['semester'])
        reg_id = str(request.POST['reg_id'])
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))  # list out of index if any field is empty....

    try:

        desig_id = Designation.objects.values_list('desig_id', flat=True).filter(desig_name=str(desig_name))
        clg_id = CollegeDetail.objects.values_list('college_id', flat=True).filter(college_name=str(clg_name))
        if (desig_id[0] > 3):
            course_id = MasterCourse.objects.values_list('course_id', flat=True).filter(course_name=str(course_name))
            depart_id = MasterDepart.objects.values_list('depart_id', flat=True).filter(depart_name=str(depart_name))
            clg_cd_id = ClgCourseDepart.objects.values_list('clg_cd_id', flat=True).filter(college_id=int(clg_id[0]),
                                                                                           course_id=int(course_id[0]),
                                                                                           depart_id=int(depart_id[0]))
            if clg_cd_id.exists():
                if (4 in desig_id):
                    # every clg has only one hod of particular branch
                    already_reg = UserRegistration.objects.filter(clg_cd_id=int(clg_cd_id[0]),
                                                                  desig_id=int(desig_id[0]))
                    if not already_reg.exists():
                        manager = UserRegistration.objects.values_list('enroll_id', flat=True).filter(
                            college_id=int(clg_id[0]), desig_id=2, status=1)
                        user_reg = UserRegistration.objects.create(enroll_id=str(enroll_id), email_id=str(email_id),
                                                                   contact_no=str(mob), desig_id=int(desig_id[0]),
                                                                   name=str(name), college_id=int(clg_id[0]),
                                                                   clg_cd_id=int(clg_cd_id[0]), dob=str(dob),
                                                                   gender=str(gender), status=0,
                                                                   manage_by=str(manager[0]),
                                                                   registration_id=str(reg_id))
                    else:
                        reg['msg'] = "Hod already exists"
                        reg['success'] = 0
                        return HttpResponse(json.dumps(reg))

                else:

                    manager = UserRegistration.objects.values_list('enroll_id', flat=True).filter(
                        clg_cd_id=int(clg_cd_id[0]), desig_id=4, status=1)
                    if manager:
                        if (5 in desig_id):
                            user_reg = UserRegistration.objects.create(enroll_id=str(enroll_id), email_id=str(email_id),
                                                                       contact_no=str(mob), desig_id=int(desig_id[0]),
                                                                       name=str(name), college_id=int(clg_id[0]),
                                                                       clg_cd_id=int(clg_cd_id[0]), dob=str(dob),
                                                                       gender=str(gender), status=0,
                                                                       manage_by=str(manager[0]),
                                                                       registration_id=str(reg_id))
                        else:
                            user_reg = UserRegistration.objects.create(enroll_id=str(enroll_id), email_id=str(email_id),
                                                                       contact_no=str(mob), desig_id=int(desig_id[0]),
                                                                       name=str(name), college_id=int(clg_id[0]),
                                                                       clg_cd_id=int(clg_cd_id[0]), dob=str(dob),
                                                                       gender=str(gender), semester=str(semester),
                                                                       status=0, registration_id=str(reg_id),
                                                                       manage_by=str(manager[0]))

                    else:
                        if (5 in desig_id):
                            user_reg = UserRegistration.objects.create(enroll_id=str(enroll_id), email_id=str(email_id),
                                                                       contact_no=str(mob), desig_id=int(desig_id[0]),
                                                                       name=str(name), college_id=int(clg_id[0]),
                                                                       clg_cd_id=int(clg_cd_id[0]), dob=str(dob),
                                                                       gender=str(gender), status=0,
                                                                       registration_id=str(reg_id))
                        else:
                            user_reg = UserRegistration.objects.create(enroll_id=str(enroll_id), email_id=str(email_id),
                                                                       contact_no=str(mob), desig_id=int(desig_id[0]),
                                                                       name=str(name), college_id=int(clg_id[0]),
                                                                       clg_cd_id=int(clg_cd_id[0]), dob=str(dob),
                                                                       gender=str(gender), semester=str(semester),
                                                                       status=0, registration_id=str(reg_id))

                if (user_reg):  # error if user_reg empty
                    Login.objects.create(login_id=str(enroll_id), password=str('abc'))
                    ProfilePicDetail.objects.create(enroll_id=str(enroll_id), pic_link=str('Default.jpg'))
                    reg['success'] = 1
                    reg['msg'] = "thanks Registered successfully..."

                return HttpResponse(json.dumps(reg))

        else:
            # every clg has only one pricipal/tpo
            already_reg = UserRegistration.objects.filter(college_id=int(clg_id[0]), desig_id=int(desig_id[0]))
            if not already_reg.exists():
                if (3 in desig_id):
                    manager = UserRegistration.objects.values_list('enroll_id', flat=True).filter(
                        college_id=int(clg_id[0]), desig_id=2, status=1)
                    user_reg = UserRegistration.objects.create(enroll_id=str(enroll_id), email_id=str(email_id),
                                                               contact_no=str(mob), desig_id=int(desig_id[0]),
                                                               name=str(name), college_id=int(clg_id[0]), dob=str(dob),
                                                               gender=str(gender), status=0, manage_by=str(manager[0]),
                                                               registration_id=str(reg_id))
                else:
                    user_reg = UserRegistration.objects.create(enroll_id=str(enroll_id), email_id=str(email_id),
                                                               contact_no=str(mob), desig_id=int(desig_id[0]),
                                                               name=str(name), college_id=int(clg_id[0]), dob=str(dob),
                                                               gender=str(gender), status=1,
                                                               registration_id=str(reg_id))
                if (user_reg):
                    Login.objects.create(login_id=str(enroll_id), password=str('abc'))
                    ProfilePicDetail.objects.create(enroll_id=str(enroll_id), pic_link=str('Default.jpg'))
                    reg['success'] = 1
                    reg['msg'] = "thanks Registered successfully..."
            else:
                reg['msg'] = str(desig_name) + "already exists"
                reg['success'] = 0
            return HttpResponse(json.dumps(reg))
    except IndexError as e:
        return HttpResponse(str(e))


@csrf_exempt
def login(request):
    try:
        mob = str(request.POST['mob'])
        reg_id = str(request.POST['reg_id'])
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        user_login = UserRegistration.objects.filter(contact_no=str(mob))
        # p_link=ProfilePicDetail.objects.filter(enroll_id=user_login[0].enroll_id)# index Error if mob and reg_id not given
        a = {}
        if user_login.exists():
            if (user_login[0].registration_id == reg_id):
                if (user_login[0].status == 1):
                    a['success'] = 1
                    a['desig'] = str(Designation.objects.filter(desig_id=user_login[0].desig_id)[0].desig_name)
                    a['name'] = str(user_login[0].name)
                    a['mob'] = str(user_login[0].contact_no)
                    a['enroll_id'] = str(user_login[0].enroll_id)
                    a['email_id'] = str(user_login[0].email_id)
                    a['college'] = str(user_login[0].college.college_name)
                    a['img'] = str(ProfilePicDetail.objects.filter(enroll_id=user_login[0].enroll_id)[0].pic_link.url)
                    a['status'] = str(user_login[0].status)
                    a['message'] = "Already Registered"
                    return HttpResponse(json.dumps(a))
                else:
                    a['success'] = 0
                    a['message'] = "Wait for verification..."
                    return HttpResponse(json.dumps(a))
            else:
                exist_reg = UserRegistration.objects.filter(registration_id=reg_id)
                if exist_reg.exists():
                    exist_reg.update(registration_id='', status=0)
                user = user_login.update(registration_id=str(reg_id))
                if (user_login[0].status == 1):
                    a['success'] = 1
                    a['desig'] = str(Designation.objects.filter(desig_id=user_login[0].desig_id)[0].desig_name)
                    a['name'] = str(user_login[0].name)
                    a['mob'] = str(user_login[0].contact_no)
                    a['enroll_id'] = str(user_login[0].enroll_id)
                    a['email_id'] = str(user_login[0].email_id)
                    a['college'] = str(user_login[0].college.college_name)
                    a['img'] = str(ProfilePicDetail.objects.filter(enroll_id=user_login[0].enroll_id)[0].pic_link.url)
                    a['status'] = str(user_login[0].status)
                    a['message'] = "Already Registered"
                    return HttpResponse(json.dumps(a))
                else:
                    a['success'] = 0
                    a['message'] = "Wait for verification"
                    return HttpResponse(json.dumps(a))

        else:
            a['success'] = 0
            a['message'] = "New Member"
            return HttpResponse(json.dumps(a))  # comes when status is 0
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def send_verification_list(request):  # error comes if profile img is nt present
    enroll_id = str(request.GET['enroll_id'])
    user_info = {}
    v_user_record = []
    a = {}
    try:
        user = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)
        if user.exists():
            verify_user = UserRegistration.objects.filter(manage_by=str(enroll_id), status=0)
            if verify_user.exists():
                for i in verify_user:
                    user_info['enroll_id'] = str(i.enroll_id)
                    user_info['name'] = str(i.name)
                    user_info['desig'] = str(Designation.objects.filter(desig_id=i.desig_id)[0].desig_name)
                    if (i.desig_id >= 4):
                        user_info['course'] = str(
                            ClgCourseDepart.objects.filter(clg_cd_id=i.clg_cd_id)[0].course.course_name)
                        user_info['department'] = str(
                            ClgCourseDepart.objects.filter(clg_cd_id=i.clg_cd_id)[0].depart.depart_name)
                    else:
                        user_info['course'] = str("");
                        user_info['department'] = str("");
                    if (i.desig_id == 6):
                        user_info['semester'] = str(i.semester)
                    else:
                        user_info['semester'] = str("");
                    try:
                        user_info['img'] = str(ProfilePicDetail.objects.filter(enroll_id=i.enroll_id)[0].pic_link.url)
                    except ValueError:
                        user_info['img'] = str(
                            'https://www.pythonanywhere.com/user/subh2504/files/home/subh2504/ctalk/profile/Default.jpg')
                    v_user_record.append(user_info)  # list
                    user_info = {}

                a['verification'] = v_user_record
                a['success'] = 1
                a['msg'] = "User list.."
                data = serializers.serialize('json', verify_user)
            else:
                a['success'] = 0
                a['msg'] = "No User exists for Verification.."
        else:
            a['success'] = 0
            a['msg'] = "you not permitted..."

        return HttpResponse(json.dumps(v_user_record))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def verification(request):
    enroll_id = str(request.POST['verify_list'])
    user_list = enroll_id.split(",")  # want list
    a = {}
    try:
        for i in user_list[:-1]:
            u = UserRegistration.objects.filter(enroll_id=str(i), status=0)
            if u.exists():
                if (u[0].desig_id == 4):
                    UserRegistration.objects.filter(Q(desig_id=5) | Q(desig_id=6), status=0,
                                                    clg_cd_id=u[0].clg_cd_id).update(manage_by=str(i))
                v_u = u.update(status=1)
                if v_u > 0:

                    a['success'] = 1
                    a['msg'] = "User Verified.."
                else:
                    a['success'] = 0
                    a['msg'] = "User not Verified.."
            else:
                a['success'] = 0
                a['msg'] = "User not found for verification/already verified.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def delete_verification(request):
    a = {}
    try:
        enroll_id = str(request.POST['verify_list'])
        del_list = enroll_id.split(",")  # want list
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        for i in del_list[:-1]:
            d = UserRegistration.objects.filter(enroll_id=str(i), status=0).delete()
            if not d:
                a['success'] = 1
                a['msg'] = "User deleted.."
            else:
                a['success'] = 0
                a['msg'] = "fail to deleted.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def manage_profile_list(request):  # student faculty,tpo,hod dict
    enroll_id = str(request.GET['enroll_id'])
    manage_list = {}
    m_user_record = []
    a = {}
    try:
        manager = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)
        if manager.exists():
            user_manage = UserRegistration.objects.filter(manage_by=str(enroll_id), status=1)
            if user_manage.exists():
                for i in user_manage:
                    manage_list['id'] = str(i.enroll_id)
                    manage_list['email'] = str(i.email_id)
                    manage_list['name'] = str(i.name)
                    manage_list['desig'] = str(Designation.objects.filter(desig_id=i.desig_id)[0].desig_name)
                    if (i.desig_id >= 4):
                        manage_list['course'] = str(
                            ClgCourseDepart.objects.filter(clg_cd_id=i.clg_cd_id)[0].course.course_name)
                        manage_list['department'] = str(
                            ClgCourseDepart.objects.filter(clg_cd_id=i.clg_cd_id)[0].depart.depart_name)

                    else:
                        manage_list['course'] = str("");
                        manage_list['department'] = str("");

                    if (i.desig_id == 6):
                        manage_list['semester'] = str(i.semester)
                    else:
                        manage_list['semester'] = str("");
                    manage_list['img'] = str(ProfilePicDetail.objects.filter(enroll_id=i.enroll_id)[0].pic_link.url)
                    m_user_record.append(manage_list)  # list
                    manage_list = {}
                a['manage_list'] = m_user_record
                a['success'] = 1
                a['msg'] = "User list to manage.."
            else:
                a['success'] = 0
                a['msg'] = "No User exists to manage.."
        else:
            a['success'] = 0
            a['msg'] = "you not permitted..."

        return HttpResponse(json.dumps(m_user_record))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def show_manage_profile(request):  # single prof
    prof_list = {}
    a = {}
    b = []
    enroll_id = str(request.GET['enroll_id'])
    try:
        p_user = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)
        if p_user.exists():
            prof_list['enroll_id'] = str(p_user[0].enroll_id)
            prof_list['email_id'] = str(p_user[0].email_id)
            prof_list['name'] = str(p_user[0].name)
            prof_list['dob'] = str(p_user[0].dob)
            prof_list['gender'] = str(p_user[0].gender)
            prof_list['mob'] = str(p_user[0].contact_no)
            prof_list['desig'] = str(p_user[0].desig.desig_name)
            prof_list['college'] = str(p_user[0].college.college_name)
            prof_list['img'] = str(ProfilePicDetail.objects.filter(enroll_id=p_user[0].enroll_id)[0].pic_link.url)
            if (p_user[0].desig_id >= 4):
                prof_list['course'] = str(
                    ClgCourseDepart.objects.filter(clg_cd_id=p_user[0].clg_cd_id)[0].course.course_name)
                prof_list['department'] = str(
                    ClgCourseDepart.objects.filter(clg_cd_id=p_user[0].clg_cd_id)[0].depart.depart_name)
            else:
                prof_list['course'] = str("");
                prof_list['department'] = str("");
            if (p_user[0].desig_id == 6):
                prof_list['semester'] = str(p_user[0].semester)
            else:
                prof_list['semester'] = str("");
            # a['user_prof_record']=prof_list
            # a['success']=1
            # a['msg']="User list.."
            b.append(prof_list)
            # data=serializers.serialize('json',p_user)
        else:
            a['success'] = 0
            a['msg'] = "sorry no records fetched error:User not present ..."

            b.append(a)

        return HttpResponse(json.dumps(b))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def manage_prof_update(request):
    a = {}
    try:
        enroll_id = str(request.POST['enroll_id'])
        email_id = str(request.POST['email_id'])
        name = str(request.POST['name'])
        dob = str(request.POST['dob'])
        # desig_name=str(request.POST['desig'])
        gender = str(request.POST['gender'])
        mob = str(request.POST['mob'])
        clg_name = str(request.POST['college'])
        course = str(request.POST['course'])
        depart = str(request.POST['depart'])
        semester = str(request.POST['semester'])
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        m_clg_id = CollegeDetail.objects.values_list('college_id', flat=True).filter(college_name=str(clg_name))
        m_user = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)
        m_prof = m_user.update(email_id=str(email_id), name=str(name), dob=str(dob), gender=str(gender),
                               contact_no=str(mob), college_id=int(m_clg_id[0]))
        if m_prof > 0:
            if m_user[0].desig_id >= 4:
                m_course_id = MasterCourse.objects.values_list('course_id', flat=True).filter(course_name=str(course))
                m_depart_id = MasterDepart.objects.values_list('depart_id', flat=True).filter(depart_name=str(depart))
                m_clg_cd_id = ClgCourseDepart.objects.values_list('clg_cd_id', flat=True).filter(
                    college_id=int(m_clg_id[0]), course_id=int(m_course_id[0]), depart_id=int(m_depart_id[0]))
                m_user.update(clg_cd_id=int(m_clg_cd_id[0]))
            if m_user[0].desig_id == 6:
                m_prof2 = m_user.update(semester=str(semester))
            a['svuccess'] = 1
            a['msg'] = "profile updated successfully."
        else:
            a['success'] = 0
            a['msg'] = "User not found/profile not upadated.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def delete_prof(request):  # group,,groupmem,login,prof,user_reg +no. of mem decrease
    a = {}
    try:
        enroll_id = str(request.POST['enroll_id'])
        del_list = enroll_id.split(",")  # want list
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        for i in del_list[:-1]:
            del_prof = UserRegistration.objects.filter(enroll_id=str(i), status=1).delete()
            if not del_prof:
                a['success'] = 1
                a['msg'] = "User deleted.."
            else:
                a['success'] = 0
                a['msg'] = "fail to deleted.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def user_profile_list(request):
    enroll_id = str(request.GET['enroll_id'])
    prof_list = {}
    prof_record = []
    a = {}
    try:
        p_user = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)
        if p_user.exists():
            prof_list['enroll_id'] = str(p_user[0].enroll_id)
            prof_list['email_id'] = str(p_user[0].email_id)
            prof_list['name'] = str(p_user[0].name)
            prof_list['dob'] = str(p_user[0].dob)
            prof_list['gender'] = str(p_user[0].gender)
            prof_list['mob'] = str(p_user[0].contact_no)
            prof_list['desig'] = str(p_user[0].desig.desig_name)
            prof_list['college'] = str(p_user[0].college.college_name)
            prof_list['img'] = str(ProfilePicDetail.objects.filter(enroll_id=p_user[0].enroll_id)[0].pic_link.url)
            if (p_user[0].desig_id >= 4):
                prof_list['course'] = str(
                    ClgCourseDepart.objects.filter(clg_cd_id=p_user[0].clg_cd_id)[0].course.course_name)
                prof_list['department'] = str(
                    ClgCourseDepart.objects.filter(clg_cd_id=p_user[0].clg_cd_id)[0].depart.depart_name)
            else:
                prof_list['course'] = str("");
                prof_list['department'] = str("");
            if (p_user[0].desig_id == 6):
                prof_list['semester'] = str(p_user[0].semester)
            else:
                prof_list['semester'] = str("");
                prof_record.append(prof_list)
            a['user_prof_record'] = prof_record
            a['success'] = 1
            a['msg'] = "User list.."
            # data=serializers.serialize('json',p_user)
        else:
            a['success'] = 0
            a['msg'] = "sorry no records fetched error:User not present ..."

        return HttpResponse(json.dumps(prof_record))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def update_own_prof(request):
    a = {}
    try:
        enroll_id = str(request.POST['enroll_id'])
        email_id = str(request.POST['email_id'])
        name = str(request.POST['name'])
        dob = str(request.POST['dob'])
        gender = str(request.POST['gender'])
        pic_link = str(request.POST['img'])
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        uop = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1).update(email_id=str(email_id),
                                                                                         name=str(name), dob=str(dob),
                                                                                         gender=str(
                                                                                             gender))  # invalid date formate if dob empty
        if uop:
            ProfilePicDetail.objects.filter(enroll_id=str(enroll_id)).update(pic_link=str(pic_link))
            a['success'] = 1
            a['msg'] = "profile upadated.."
        else:
            a['success'] = 0
            a['msg'] = "profile not updated .."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def group_list(request):
    enroll_id = str(request.GET['enroll_id'])

    create_grp_list = {}
    grp_record = []
    a = {}
    try:
        admin = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)
        if admin.exists():
            grp = GroupMember.objects.filter(enroll_id=str(admin[0].enroll_id))

            if grp.exists():
                for i in grp:
                    create_grp_list['admin_id'] = str(i.enroll_id)
                    create_grp_list['group_name'] = str(
                        GroupDetail.objects.filter(group_id=str(i.group_id))[0].group_name)
                    create_grp_list['group_id'] = str(i.group_id)
                    create_grp_list['img'] = str("")
                    grp_record.append(create_grp_list)  # list
                    create_grp_list = {}
                a['group_list'] = grp_record
                a['success'] = 1
                a['msg'] = "User list .."
                data = serializers.serialize('json', grp)
            else:
                a['success'] = 0
                a['msg'] = "No User exists .."
        else:
            a['success'] = 0
            a['msg'] = "you not permitted..."

        return HttpResponse(json.dumps(grp_record))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def create_group_list(request):
    enroll_id = str(request.GET['enroll_id'])
    create_grp_list = {}
    g_user_record = []
    a = {}
    try:
        manager = UserRegistration.objects.filter(enroll_id=str(enroll_id), status=1)  #
        if manager.exists():
            if (manager[0].desig_id >= 2 and manager[0].desig_id < 4):
                user_group = UserRegistration.objects.exclude(enroll_id=str(enroll_id)).filter(status=1,
                                                                                               college_id=manager[
                                                                                                   0].college_id,
                                                                                               desig_id__gte=manager[
                                                                                                   0].desig_id)
                # user_group=user_group1.exclude(enroll_id=str(enroll_id))
            else:
                if (manager[0].desig_id >= 4 and manager[0].desig_id < 6):
                    user_group = UserRegistration.objects.exclude(enroll_id=str(enroll_id)).filter(
                        Q(desig_id__gt=manager[0].desig_id, clg_cd_id=manager[0].clg_cd_id) | Q(
                            desig_id=manager[0].desig_id, college_id=manager[0].college_id), status=1)
                    # user_group=user_group1.exclude(enroll_id=str(enroll_id))
            if user_group.exists():
                for i in user_group:
                    create_grp_list['enroll_id'] = str(i.enroll_id)
                    create_grp_list['name'] = str(i.name)
                    create_grp_list['email_id'] = str(i.email_id)
                    create_grp_list['desig'] = str(Designation.objects.filter(desig_id=i.desig_id)[0].desig_name)
                    create_grp_list['college'] = str(manager[0].college.college_name)
                    if (i.desig_id >= 4):
                        create_grp_list['course'] = str(
                            ClgCourseDepart.objects.filter(clg_cd_id=i.clg_cd_id)[0].course.course_name)
                        create_grp_list['department'] = str(
                            ClgCourseDepart.objects.filter(clg_cd_id=i.clg_cd_id)[0].depart.depart_name)
                    else:
                        create_grp_list['course'] = str("");
                        create_grp_list['department'] = str("");
                    if (i.desig_id == 6):
                        create_grp_list['semester'] = str(i.semester)
                    else:
                        create_grp_list['semester'] = str("");
                    create_grp_list['img'] = str(ProfilePicDetail.objects.filter(enroll_id=i.enroll_id)[0].pic_link.url)
                    g_user_record.append(create_grp_list)  # list
                    create_grp_list = {}
                a['manage_list'] = g_user_record
                a['success'] = 1
                a['msg'] = "User list to create group.."
                data = serializers.serialize('json', user_group)
            else:
                a['success'] = 0
                a['msg'] = "No User exists to create group.."
        else:
            a['success'] = 0
            a['msg'] = "you not permitted..."

        return HttpResponse(json.dumps(g_user_record))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def create_group(request):  # same name group nt allow
    a = {}
    try:
        admin = str(request.POST['admin'])
        group_name = str(request.POST['group_name'])
        # no_members=int(request.POST['mob'])
        grp_list = str(request.POST['group_list'])
        grp_mem_list = grp_list.split(",")
    except Error as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        if not grp_list:
            a['success'] = 0
            a['msg'] = "Select the members first.."
            return HttpResponse(json.dumps(a))
        create_grp = GroupDetail.objects.create(admin_id=str(admin), group_name=str(group_name),
                                                no_of_member=int(len(grp_mem_list)), allow_msg=1, notification=1)
        if create_grp:  # same group
            c_grp_id = GroupDetail.objects.values_list('group_id', flat=True).filter(admin_id=str(admin),
                                                                                     group_name=str(group_name))
            GroupMember.objects.create(enroll_id=str(admin), group_id=c_grp_id[0])
            # adding menbers:
            for i in grp_mem_list[:-1]:
                add_grp_mem = GroupMember.objects.create(enroll_id=str(i), group_id=c_grp_id[0])
                if add_grp_mem:
                    a['success'] = 1
                    a['msg'] = "group created and members added.."
                else:
                    GroupDetail.objects.filter(enroll_id=str(admin), group_id=c_grp_id[0]).delete()
                    a['success'] = 0
                    a['msg'] = "group created but members not added.."
        else:
            a['success'] = 0
            a['msg'] = "group not created.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def delete_group(request):  # single group deleted at a time
    a = {}
    try:
        admin = str(request.POST['admin'])
        group_name = str(request.POST['group_name'])
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        del_group = GroupDetail.objects.filter(admin_id=str(admin), group_name=str(group_name)).delete()
        if not del_group:
            a['success'] = 1
            a['msg'] = "Group deleted successfully.."
        else:
            a['success'] = 0
            a['msg'] = "fail to deleted group.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


# grp_setting,deletemem,add mem
@csrf_exempt
def group_setting(request):
    a = {}
    try:
        admin = str(request.POST['admin'])
        group_name = str(request.POST['group_name'])
        allow_msg = int(request.POST['allow_msg'])
        notification = int(request.POST['notification'])
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        update_group = GroupDetail.objects.filter(admin_id=str(admin), group_name=str(group_name)).update(
            allow_msg=int(allow_msg), notification=int(notification))
        if update_group > 0:
            a['success'] = 1
            a['msg'] = "Group updated.."
        else:
            a['success'] = 0
            a['msg'] = "fail to update group.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def add_new_member(request):
    a = {}
    try:
        admin = str(request.POST['admin'])
        group_name = str(request.POST['group_name'])
        new_mem_list = str(request.POST['group_list'])
        add_mem_list = new_mem_list.split(",")
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        mem_id = GroupDetail.objects.values_list('group_id', flat=True).filter(admin_id=str(admin),
                                                                               group_name=str(group_name))
        # adding menbers:
        for i in add_mem_list:
            add_new_mem = GroupMember.objects.create(enroll_id=str(i), group_id=mem_id[0])
            if add_new_mem:
                a['success'] = 1
                a['msg'] = "New members added.."
            else:
                a['success'] = 0
                a['msg'] = "Fail to add members.."

        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def delete_exist_member(request):
    a = {}
    try:
        admin = str(request.POST['admin'])
        group_name = str(request.POST['group_name'])
        mem_list = str(request.POST['enroll_id'])
        del_mem_list = mem_list.split(",")
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({"success": 0, "msg": str(e)}))
    try:
        mem_id = GroupDetail.objects.values_list('group_id', flat=True).filter(admin_id=str(admin),
                                                                               group_name=str(group_name))
        # delete menbers:
        for i in del_mem_list:
            del_exist_mem = GroupMember.objects.filter(enroll_id=str(i), group_id=mem_id[0]).delete()
            if del_exist_mem > 0:
                a['success'] = 1
                a['msg'] = "New members added.."
            else:
                a['success'] = 0
                a['msg'] = "Fail to add members.."

        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def get_reg_id(request):
    g_id = int(request.POST['g_id'])
    s_id = str(request.POST['s_id'])
    msg = str(request.POST['msg'])
    a = {}
    id = []
    try:
        mem_id = GroupMember.objects.filter(group_id=g_id).exclude(enroll_id=s_id)
        g_name = GroupDetail.objects.filter(group_id=g_id)[0].group_name
        s_name = UserRegistration.objects.filter(enroll_id=str(s_id))[0].name
        if mem_id.exists():
            for i in mem_id:
                reg_id = UserRegistration.objects.filter(enroll_id=str(i.enroll_id), status=1)
                id.append(str(reg_id[0].registration_id))
            a["ss"] = id

        else:
            a['success'] = 0
            a['msg'] = "No user found.."
        return HttpResponse(json.dumps(a))
    except Error as e:
        return HttpResponse(str(e))


@csrf_exempt
def send(request):
    g_id = int(request.POST['g_id'])
    s_id = str(request.POST['s_id'])
    msg = str(request.POST['msg'])
    a = {}
    id = []
    try:
        mem_id = GroupMember.objects.filter(group_id=g_id).exclude(enroll_id=s_id)
        g_name = GroupDetail.objects.filter(group_id=g_id)[0].group_name
        s_name = UserRegistration.objects.filter(enroll_id=str(s_id))[0].name
        if mem_id.exists():
            for i in mem_id:
                reg_id = UserRegistration.objects.filter(enroll_id=str(i.enroll_id), status=1)
                id.append(str(reg_id[0].registration_id))
            a["ss"] = id
    except Error as e:
        return HttpResponse({"response": "Failure"})
    extra = {"msg": msg, "s_name": s_name, "s_id": s_id, "g_name": g_name, "g_id": g_id}
    dataRaw = {"data": extra, "registration_ids": id}
    key = "AIzaSyBSKp3pkMOL9CLUTPeNpIlWMWS53TbE4-E"
    headers = {"Content-Type": "application/json", "Authorization": "key={}".format(key)}
    result = requests.post("https://android.googleapis.com/gcm/send", headers=headers, data=json.dumps(dataRaw))
    return HttpResponse(json.dumps({'response': "Success", 'result': result.text, 'id': a["ss"]}))
    # return HttpResponse(json.dumps(a))


@csrf_exempt
def uploaded_images(request):
    if request.method == 'POST':
        # saving base string from post data
        try:
            base64_string = request.POST['image']
            filename = request.POST['filename']
            a = str(request.POST['enroll'])

            base64_string += "=" * ((4 - len(base64_string) % 4) % 4)
            # decoding base string to image and saving in to your media root folder
            # fh = open(os.path.join(settings.MEDIA_ROOT, filename), "wb")
            # fh.write(base64.b64decode(base64_string))

            # fh.close()

            # saving decoded image to database
            decoded_image = base64.b64decode(base64_string)
            # new_image=ProfilePicDetail()
            # new_image.pic_link.url = ContentFile(decoded_image, filename)
            # new_image.save()


            img = ProfilePicDetail.objects.get(enroll_id=a)
            if (img.pic_link == filename):
                os.remove(os.path.join(settings.MEDIA_ROOT, filename))
            img.pic_link = ContentFile(decoded_image, filename)
            img.save()
            return HttpResponse(json.dumps({'response': "Success"}))
        except Error as e:
            return HttpResponse(json.dumps({'response': str(e)}))


@csrf_exempt
def test(request):
    return HttpResponse("hy6gbygbyhbtggvtgbnuhbtg6vbgyhunugtgybnujvtfgbnu8hn6tgh7y8uh")
