# from django.shortcuts import render
import os
from django.http import JsonResponse
import json
from .utils import upload2database

# Create your views here.
def upload(request):
    # ################# 权限判断 ################# #
    data = json.loads(request.body)
    output = {
        'result': False,
        'information': '权限不足'
    }
    if data['authority'] != 'Manager':
         return JsonResponse(output)
    if not os.path.exists(data['data']['filepath']):
        output['information'] = '路径错误'
        return JsonResponse(output)
    # ########################################### #
    
    
    result = upload2database(data)
        
    output['result'] = result
    if result == False:
        output['information'] = '场景已存在'
    else:
        output['information'] = '上传成功'
    return JsonResponse(output)

def batch_upload(request):
    data = json.loads(request.body)
    output = {
        'result': False,
        'information': '权限不足'
    }
    if data['authority'] != 'Manager':
         return JsonResponse(output)
    if not os.path.exists(data['data']['folderpath']):
        output['information'] = '路径错误'
        return JsonResponse(output)
    ##########################################

    filelist = os.listdir(data['data']['folderpath'])
    valid = 0
    invalid = 0
    for filepath in filelist:
        if not filepath.endswith('.json'):
            continue
        filepath = os.path.join(data['data']['folderpath'], filepath)
        result = upload2database(filepath, True)
        if result:
            valid += 1
        else:
            invalid += 1


    output['result'] = True if valid > 0 else False
    output['information'] = f'上传{valid}条数据，已存在{invalid}条数据'
    if output['result'] == False:
        output['information'] = '上传失败\n' + output['information']
    else:
        output['information'] = '上传成功\n' + output['information']
    return JsonResponse(output)