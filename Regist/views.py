# from django.shortcuts import render
from django.http import JsonResponse
from .models import Users
import json

# Create your views here.
def regist(request):
    data = json.loads(request.body)['data']
    username = data['username']
    email = data['email']
    password = data['password']
    name = data['name']

    information = ""
    vaild = True
    existed_username = Users.objects.filter(username=username)
    if len(existed_username) > 0:
        information += "用户名已存在\n"
        vaild = False
    
    existed_email = Users.objects.filter(email=email)
    if len(existed_email) > 0:
        information += "邮箱已存在\n"
        vaild = False
    
    if vaild:
        user = Users()
        user.username = username
        user.email = email
        user.password = password
        user.name = name
        user.authority = 'Customer'
        user.save()
    
    return JsonResponse({'message': vaild, 'information': information})