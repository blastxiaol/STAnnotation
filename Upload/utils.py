import os
import numpy as np
import cv2
import math
import json
from .models import Scenes, Frames, Instances


EX_MATRIX = np.array([
    [0.017452406437283574, -0.999847695156391, -5.551115123125783e-17, -0.024703597383298997],
    [-0.012215140126845492, -0.00021321606402130433, -0.999925369660452, 0.03975440225788578],
    [0.9997730761834054, 0.01745110395826527, -0.012217000835247127, -0.09080308692722944]
])
IN_MATRIX = np.array([
    [1269.4,    0.     ,  942.03],
            [0.     , 1273.0,  620.65],
            [0.     ,    0.     ,    1.     ]
])

def cal_corner_after_rotation(corner, center, r):
    x1, y1 = corner
    x0, y0 = center
    x2 = math.cos(r) * (x1 - x0) - math.sin(r) * (y1 - y0) + x0
    y2 = math.sin(r) * (x1 - x0) + math.cos(r) * (y1 - y0) + y0
    return x2, y2

def eight_points(center, size, rotation=0):
    x, y, z = center
    w, l, h = size
    w = w/2
    l = l/2
    h = h/2

    x1, y1, z1 = x-w, y-l, z+h
    x2, y2, z2 = x+w, y-l, z+h
    x3, y3, z3 = x+w, y-l, z-h
    x4, y4, z4 = x-w, y-l, z-h
    x5, y5, z5 = x-w, y+l, z+h
    x6, y6, z6 = x+w, y+l, z+h
    x7, y7, z7 = x+w, y+l, z-h
    x8, y8, z8 = x-w, y+l, z-h

    if rotation != 0:
        x1, y1 = cal_corner_after_rotation(corner=(x1, y1), center=(x, y), r=rotation)
        x2, y2 = cal_corner_after_rotation(corner=(x2, y2), center=(x, y), r=rotation)
        x3, y3 = cal_corner_after_rotation(corner=(x3, y3), center=(x, y), r=rotation)
        x4, y4 = cal_corner_after_rotation(corner=(x4, y4), center=(x, y), r=rotation)
        x5, y5 = cal_corner_after_rotation(corner=(x5, y5), center=(x, y), r=rotation)
        x6, y6 = cal_corner_after_rotation(corner=(x6, y6), center=(x, y), r=rotation)
        x7, y7 = cal_corner_after_rotation(corner=(x7, y7), center=(x, y), r=rotation)
        x8, y8 = cal_corner_after_rotation(corner=(x8, y8), center=(x, y), r=rotation)

    conern1 = np.array([x1, y1, z1])
    conern2 = np.array([x2, y2, z2])
    conern3 = np.array([x3, y3, z3])
    conern4 = np.array([x4, y4, z4])
    conern5 = np.array([x5, y5, z5])
    conern6 = np.array([x6, y6, z6])
    conern7 = np.array([x7, y7, z7])
    conern8 = np.array([x8, y8, z8])
    
    eight_corners = np.stack([conern1, conern2, conern3, conern4, conern5, conern6, conern7, conern8], axis=0)
    return eight_corners

def loc_pc2img(points):
    assert len(points.shape) == 1 and len(points) > 6 
    x, y, z, w, l, h, r = points[:7]
    center = [x, y, z]
    size = [w, l, h]
    points = eight_points(center, size, r)
    points = np.insert(points, 3, values=1, axis=1)
    points_T = np.transpose(points)
    points_T[3, :] = 1.0

    # lidar2camera
    points_T_camera = np.dot(EX_MATRIX, points_T)
    # camera2pixel
    pixel = np.dot(IN_MATRIX, points_T_camera).T
    pixel_xy = np.array([x / x[2] for x in pixel])[:, 0:2]
    pixel_xy = np.around(pixel_xy).astype(int)
    
    return pixel_xy


def upload2database(data, batch=False):
    if batch:
        filepath = data
    else:
        location = data['data']['location']
        date = data['data']['date']
        filepath = data['data']['filepath']

    # 上传场景数据
    file = json.load(open(filepath))

    try:
        scene = Scenes.objects.get(annotation_path=filepath)
        return False
    except:
        scene = Scenes()
        scene.annotation_path = filepath
        if batch:
            month, day = file['data'].split('-')[:2]
            date = f'2022-{month}-{day}'
            location = file['group']
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
    
    return True