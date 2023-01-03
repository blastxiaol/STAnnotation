# from django.shortcuts import render
from django.http import JsonResponse
import os
import json
import numpy as np
import cv2
from .models import Scenes, Frames, Instances
from .utils import loc_pc2img

# Create your views here.
def upload(request):
    # ################# 权限判断 ################# #
    data = json.loads(request.body)
    output = {
        'result': False
    }
    if data['authority'] != 'Manager':
         return JsonResponse(output)
    # ########################################### #
    location = data['data']['location']
    date = data['data']['date']
    date = date.split('T')[0]
    filepath = data['data']['filepath']
    

    file = json.load(open(filepath))
    # 上传场景数据
    try:
        scene = Scenes.objects.get(location=location, date=date)
    except:
        scene = Scenes()
        scene.location = location
        scene.date = date
        scene.save()
        
    scene_id = scene.id
    group = file['group']
    for frame_data in file['frames']:
        timestamp = frame_data['timestamp']
        pc_path = frame_data['pc_name']
        img_path = frame_data['image_name']
        img_path = os.path.join(f'/Users/apple/Desktop/test/123/test_folder/{group}', img_path.split('/')[-1])
        try:
            frame = Frames.objects.get(pc_path=pc_path)
        except:
            frame = Frames()
            frame.scene_id = scene_id
            frame.timestamp = timestamp
            frame.pc_path = pc_path
            frame.img_path = img_path
            frame.save()

        frame_id = frame.id
        instance_list = frame_data['instance']
        image = cv2.imread(str(frame.img_path))
        for instance_data in instance_list:
            category = instance_data['category']
            if category != 'person':
                continue
            object_key = instance_data['id']
            occlusion = True if instance_data['occlusion'] == 1 else False

            center = instance_data['position']
            boundingbox3d = instance_data['boundingbox3d']
            rotation = instance_data['rotation']
            box3d = [center['x'], center['y'], center['z'], boundingbox3d['x'], boundingbox3d['y'], boundingbox3d['z'], rotation]
            box2d = loc_pc2img(np.array(box3d))
            # 过滤中心不在图片上的点
            left_up = box2d[:, 0].min(), box2d[:, 1].min()
            right_down = box2d[:, 0].max(), box2d[:, 1].max()
            cy, cx = (np.array(right_down) + np.array(left_up)) / 2
            if cx < 0 or cx >= image.shape[0] or cy <0 or cy >= image.shape[1]:
                continue
            box2d = box2d[[6, 7, 3, 2, 5, 4, 0, 1]]

            box2d = box2d.reshape(-1)
            box2d = ','.join([str(_) for _ in box2d.tolist()])
            box3d = ','.join([str(_) for _ in box3d])
            # box2d = np.array([int(_) for _ in box2d.split(',')]).reshape(-1, 2) # 还原框
            try:
                instance = Instances.objects.get(
                    frame_id=frame_id,
                    object_key=object_key,
                )
            except:
                instance = Instances()
                instance.frame_id = frame_id
                instance.object_key = object_key
                instance.box2d = box2d
                instance.box3d = box3d
                instance.occlusion = occlusion
                instance.described = False
                instance.save()
    
    ## 检查前后frame
    for frame_data in file['frames']:
        pc_path = frame_data['pc_name']
        previous_pc_path = frame_data['previous_pc']
        next_pc_path = frame_data['next_pc']
        frame = Frames.objects.get(pc_path=pc_path)
        if previous_pc_path:
            previous_frame = Frames.objects.get(pc_path=previous_pc_path)
            frame.prev_frame_id = previous_frame.id
        if next_pc_path:
            next_frame = Frames.objects.get(pc_path=next_pc_path)
            frame.next_frame_id = next_frame.id
        frame.save()
        
    output['result'] = True
    return JsonResponse(output)