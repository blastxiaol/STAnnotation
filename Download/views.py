from django.http import JsonResponse
import json
from Annotation.models import Descriptions
from Regist.models import Users
from Upload.models import Instances, Frames, Scenes
import os
import json

# Create your views here.
def download(request):
    # ################# 权限判断 ################# #
    data = json.loads(request.body)
    output = {
        'result': False,
        'information': '权限不足'
    }
    if data['authority'] != 'Manager':
         return JsonResponse(output)
    # ########################################### #

    if 'path' in data['data']:
        path = data['data']['path']
    else:
        path = 'referring.json'
    
    description_list = Descriptions.objects.filter(passed=1)

    refer_output = []
    for description in description_list:
        ann_id = description.id
        sentence = description.sentence
        action = description.action.split(';')
        if len(action) == 1 and action[0] == '':
            action = []
        token = sentence.replace(',', ' , ').replace('.', ' . ').lower().split()

        user = Users.objects.get(id=description.user_id)
        user_email = user.email
        
        instance = Instances.objects.get(id=description.instance_id)
        object_id = instance.object_key
        bbox = instance.box3d.split(',')
        bbox = [float(i) for i in bbox]

        frame = Frames.objects.get(id=instance.frame_id)
        pc_path = str(frame.pc_path).split('/')[-1][:-4]

        scene = Scenes.objects.get(id=frame.scene_id)
        annotation_path = str(scene.annotation_path)
        annotation_file = json.load(open(annotation_path))
        date=annotation_file['data']

        refer_output.append(dict(
            date=date,
            pc_path=pc_path,
            bbox=bbox,
            object_id=object_id,
            ann_id=ann_id,
            description=sentence,
            token=token,
            action=action,
            user_email=user_email,            
        ))

    with open(path, 'w') as f:
        file = json.dumps(refer_output)
        f.write(file)

    output = {
        'result': True,
        'information': f'下载成功，位置在{path}'
    }
    return JsonResponse(output)