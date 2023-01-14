from django.http import JsonResponse
from Regist.models import Users
from Annotation.models import Descriptions
from Upload.models import Instances, Frames
from Regist.models import Users
from django.db.models import Q
import json
import numpy as np
import cv2
import base64
from Annotation.utils import draw_projected_box3d

# Create your views here.
def get_data(request):
    data = json.loads(request.body)
    # ################# 权限判断 ################# #
    try:
        user = Users.objects.get(id=data['user_id'])
    except:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})

    if user.password != data['password']:
            return JsonResponse({'result': False, 'information': '用户权限不足\n'})
    ##############################################
    descriptions_list = Descriptions.objects.filter(~(Q(user_id=user.id)|Q(vertified_users=user)), passed=0)
    try:
        index = np.random.randint(0, len(descriptions_list))
        description = descriptions_list[index]
        # description = descriptions_list[0]
    except:
        return JsonResponse({'result': False, 'information': '当前没有可用的描述验证\n'})
    instance_id = description.instance_id
    instance = Instances.objects.get(id=instance_id)

    frame_id = instance.frame_id
    frame = Frames.objects.get(id=frame_id)
    image_path = str(frame.img_path)
    box2d = instance.box2d
    box2d = np.array([int(_) for _ in box2d.split(',')]).reshape(-1, 2)
    image = cv2.imread(image_path)
    image_base = cv2.imencode('.jpg', image)[1] #  image为cv2.imread后的结果
    image_stream = 'data:image/jpeg;base64,'+base64.encodebytes(image_base).decode()    

    target_id = instance_id

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

    object_list = Instances.objects.filter(frame_id=frame_id)
    object_image_list = []
    for instance in object_list:
        box2d = instance.box2d
        box2d = np.array([int(_) for _ in box2d.split(',')]).reshape(-1, 2)
        image_box = draw_projected_box3d(image.copy(), box2d, (0, 255, 0), 2)
        image_box = cv2.imencode('.jpg', image_box)[1] #  image为cv2.imread后的结果
        image_stream_box = 'data:image/jpeg;base64,'+base64.encodebytes(image_box).decode() 
        object_image_list.append({
            'id': instance.id,
            'image': image_stream_box,
        })

    output = {
        'result': True,
        'description_id': description.id,
        'sentence': description.sentence,
        'action': description.action,
        'image':[
            {'image': image_stream1},
            {'image': image_stream2},
            ],
        'object': [{'id': -1, 'image': image_stream}] + object_image_list,
        'target_id': target_id,
        }
    return JsonResponse(output)


def post_data(request):
    data = json.loads(request.body)
    # ################# 权限判断 ################# #
    try:
        user = Users.objects.get(id=data['user_id'])
    except:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})

    if user.password != data['password']:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})
    # ########################################### #
    
    description_id = data['description_id']
    description = Descriptions.objects.get(id=description_id)
    description.vertified_users.add(user.id)
    if data['pass']:
        description.add_veritified()
    else:
        if description.passed == 1:            
            user.failedAnnotated()
        description.set_passed(-1)

    if description.veritified >= 2:
        description.set_passed(1)
        user.successAnnotated()

    return JsonResponse({'result': True, 'information': '提交成功\n'})