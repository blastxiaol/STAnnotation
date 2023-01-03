from django.http import JsonResponse
from Regist.models import Users
from Annotation.models import Descriptions
from Upload.models import Instances, Frames
import json
import numpy as np 
import cv2
import base64
from Annotation.utils import draw_projected_box3d


# Create your views here.
def get_list(request, user_id):
    try:
        user = Users.objects.get(id=user_id)
    except:
        return JsonResponse({'descriptions': []})
    
    description_list = Descriptions.objects.filter(user_id=user_id, passed=-1)[:10]
    descriptions = []
    for description in description_list:
        descriptions.append({
            'id': description.id,
            'sentence': description.sentence,
            'action': description.action,
        })

    return JsonResponse({'descriptions': descriptions})

def get_instance(request):
    data = json.loads(request.body)
    # ################# 权限判断 ################# #
    try:
        user = Users.objects.get(id=data['user_id'])
    except:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})

    if user.password != data['password']:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})
    ##############################################

    description_id = data['description_id']
    description = Descriptions.objects.get(id=description_id)
    instance_id = description.instance_id
    instance = Instances.objects.get(id=instance_id)
    frame_id = instance.frame_id
    frame = Frames.objects.get(id=frame_id)
    image_path = str(frame.img_path)
    box2d = instance.box2d
    box2d = np.array([int(_) for _ in box2d.split(',')]).reshape(-1, 2)
    image = cv2.imread(image_path)
    image = draw_projected_box3d(image, box2d, (0, 255, 0), 2)
    image = cv2.imencode('.jpg', image)[1] #  image为cv2.imread后的结果
    image_stream3 = 'data:image/jpeg;base64,'+base64.encodebytes(image).decode()

    prev_frame_id = frame.prev_frame_id
    if prev_frame_id:
        prev_frame = Frames.objects.get(id=prev_frame_id)
        prev_image_path = str(prev_frame.img_path)
        prev_image = cv2.imread(prev_image_path)
        prev_image = cv2.imencode('.jpg', prev_image)[1] #  image为cv2.imread后的结果
        image_stream2 = 'data:image/jpeg;base64,'+base64.encodebytes(prev_image).decode()
        prev_prev_frame_id = prev_frame.prev_frame_id
    else:
        prev_prev_frame_id = None
        image_stream2 = 'error'
    if prev_prev_frame_id:
        prev_prev_frame = Frames.objects.get(id=prev_prev_frame_id)
        prev_prev_image_path = str(prev_prev_frame.img_path)
        prev_prev_image = cv2.imread(prev_prev_image_path)
        prev_prev_image = cv2.imencode('.jpg', prev_prev_image)[1] #  image为cv2.imread后的结果
        image_stream1 = 'data:image/jpeg;base64,'+base64.encodebytes(prev_prev_image).decode()
    else:
        image_stream1 = 'error'
    output = {
        'result': True,
        'instance_id': instance_id,
        'image':[
            {'image': image_stream1},
            {'image': image_stream2},
            {'image': image_stream3},
            ]
        }
    
    return JsonResponse(output)

def submit_data(request):
    data = json.loads(request.body)
    # ################# 权限判断 ################# #
    try:
        user = Users.objects.get(id=data['user_id'])
    except:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})

    if user.password != data['password']:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})
    ##############################################
    print(data)
    description_id = data['description_id']
    description = Descriptions.objects.get(id=description_id)
    description.action = data['action']
    description.sentence = data['sentence']
    description.passed = 0
    description.vertified_users.clear()
    description.save()
    
    return JsonResponse({'result': True, 'information': '提交成功\n'})
