from django.http import JsonResponse
from Upload.models import Instances, Frames
from .models import Descriptions
from Regist.models import Users
from Upload.models import Instances
import numpy as np
import cv2
import base64
import json
from .utils import draw_projected_box3d

# Create your views here.
def add(request):
    if request.method == 'GET':
        instance_list = Instances.objects.filter(described__lt=2, hard__lt=5)
        if len(instance_list) <= 0:
            output = {
            'result': False,
            'instance_id': -1,
            'image':[
                {'image': 'error'},
                {'image': 'error'},
                {'image': 'error'},
                ]
            }
            return JsonResponse(output)
        index = np.random.randint(0, len(instance_list))
        instance = instance_list[index]

        instance_id = instance.id
        object_key = instance.object_key
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
            try:
                prev_instance = Instances.objects.get(object_key=object_key, frame_id=prev_frame_id)
                prev_box2d = prev_instance.box2d
                prev_box2d = np.array([int(_) for _ in prev_box2d.split(',')]).reshape(-1, 2)
                prev_image = draw_projected_box3d(prev_image, prev_box2d, (0, 255, 0), 2)
            except:
                pass
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
            try:
                prev_prev_instance = Instances.objects.get(object_key=object_key, frame_id=prev_prev_frame_id)
                prev_prev_box2d = prev_prev_instance.box2d
                prev_prev_box2d = np.array([int(_) for _ in prev_prev_box2d.split(',')]).reshape(-1, 2)
                prev_prev_image = draw_projected_box3d(prev_prev_image, prev_prev_box2d, (0, 255, 0), 2)
            except:
                pass
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
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        # ################# 权限判断 ################# #
        try:
            user = Users.objects.get(id=data['user']['user_id'])
        except:
            return JsonResponse({'result': False, 'information': '用户权限不足\n'})

        if user.password != data['user']['password']:
             return JsonResponse({'result': False, 'information': '用户权限不足\n'})
        ##############################################
        descriptions_list = data['description']
        instance_id = data['instance_id']
        try:
            instance = Instances.objects.get(id=instance_id)
        except:
            return JsonResponse({'result': False, 'information': 'Instance错误\n'})
        
        valid_input = 0
        for i, description_element in enumerate(descriptions_list):
            sentence = description_element['description']
            action = description_element['action']
            existed_sentence_list= Descriptions.objects.filter(sentence=sentence, instance_id=instance_id)
            if len(existed_sentence_list) > 0:
                return JsonResponse({'result': False, 'information': f'第{i+1}条描述重复\n'})

            if not sentence.isspace() and sentence != '':
                description = Descriptions()
                description.sentence = sentence
                if not action.isspace():
                    description.action = action
                description.instance_id = instance_id
                description.user_id = data['user']['user_id']
                description.veritified = 0
                description.passed = 0
                description.save()
                # description.vertified_users.add(user)
                description.vertified_users.clear()
                instance.add_description()
                user.addSentence()
                valid_input += 1

        if valid_input == 0:
            return JsonResponse({'result': False, 'information': f'数据为空\n'})
                
        return JsonResponse({'result': True})

def ishard(request):
    data = json.loads(request.body)
    # ################# 权限判断 ################# #
    try:
        user = Users.objects.get(id=data['user']['user_id'])
    except:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})

    if user.password != data['user']['password']:
        return JsonResponse({'result': False, 'information': '用户权限不足\n'})
    ##############################################
    instance_id = data['instance_id']
    try:
        instance = Instances.objects.get(id=instance_id)
    except:
        return JsonResponse({'result': False, 'information': 'Instance错误\n'})

    instance.ishard()

    return JsonResponse({'result': True, 'information': ''})