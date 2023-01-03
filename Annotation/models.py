from django.db import models
from Regist.models import Users

# Create your models here.
class Descriptions(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    instance_id = models.IntegerField(verbose_name='instance_id')
    sentence = models.TextField(verbose_name='sentence')
    action = models.TextField(null=True, blank=True, verbose_name='action')
    user_id = models.IntegerField(verbose_name='user_id')
    veritified = models.IntegerField(verbose_name='veritified')
    passed = models.IntegerField(verbose_name='passed') # -1, 0, 1
    vertified_users = models.ManyToManyField(to=Users, blank=True, verbose_name='vertified_users')

    def add_veritified(self):
        self.veritified += 1
        self.save(update_fields=['veritified'])
    
    def set_passed(self, value):
        assert value in {-1, 0, 1}
        self.passed = value
        self.save(update_fields=['passed'])

    
    def __str__(self):
        return f"Description {self.id}"
    
    class Meta:
        verbose_name_plural = 'Descriptions'
