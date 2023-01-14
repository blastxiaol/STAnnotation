from django.db import models

# Create your models here.
class Scenes(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    location = models.CharField(max_length=128, verbose_name='location')
    date = models.DateTimeField(verbose_name='date')
    annotation_path = models.FileField(unique=True, verbose_name='annotation_path')
    
    def __str__(self):
        return f"Scene {self.location}-({self.date})"
    
    class Meta:
        verbose_name_plural = 'Scenes'

class Frames(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    scene_id = models.IntegerField(verbose_name='scene_id')
    timestamp = models.CharField(max_length=128, verbose_name='timestamp')
    pc_path = models.FileField(unique=True, verbose_name='pc_path')
    img_path = models.FileField(unique=True, verbose_name='img_path')
    prev_frame_id = models.IntegerField(null=True, verbose_name='prev_frame_id')
    next_frame_id = models.IntegerField(null=True, verbose_name='next_frame_id')
    
    def __str__(self):
        return f"Frame {self.id}"
    
    class Meta:
        verbose_name_plural = 'Frames'


class Instances(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    frame_id = models.IntegerField(verbose_name='frame_id')
    object_key = models.CharField(max_length=128, verbose_name='object_key')
    box3d = models.TextField(verbose_name='box3d')
    box2d = models.TextField(verbose_name='box2d')
    occlusion = models.BooleanField(verbose_name='occlusoin')
    described = models.IntegerField(verbose_name='described')
    
    def __str__(self):
        return f"instance {self.id}"
    
    class Meta:
        verbose_name_plural = 'Instances'

    def add_description(self):
        self.described += 1
        self.save(update_fields=['described'])

