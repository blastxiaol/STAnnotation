# from django.shortcuts import render
from django.http import JsonResponse
import json
from Regist.models import Users

# Create your views here.
def login(request):
    data = json.loads(request.body)['data']
    username = data['username']
    password = data['password']

    valid = False
    try:
        user = Users.objects.get(username=username)
    except:
        output = {'valid': valid, 'information': '用户名不存在\n'}
        return JsonResponse(output)
    if password != user.password:
        output = {'valid': valid, 'information': '密码不正确\n'}
        return JsonResponse(output)
    valid = True
    output = {
        'login': valid,
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'name': user.name,
        'authority': user.authority,
        'annotations': user.annotations,
        'sentences': user.sentences,
        'password': user.password,
    }
    return JsonResponse(output)