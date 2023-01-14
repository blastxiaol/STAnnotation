from django.db import models

# Create your models here.
class Users(models.Model):
    """
    Table Users
    """
    Roles = (
        ('Manager', 'M'),
        ('Customer', 'C'),
    )

    id = models.AutoField(primary_key=True, verbose_name='id')
    username = models.CharField(max_length=128, unique=True, verbose_name='username')
    email = models.EmailField(unique=True, verbose_name='email')
    name = models.CharField(max_length=256, verbose_name='name')
    authority = models.CharField(choices=Roles, max_length=1000, verbose_name='authority')
    password = models.CharField(max_length=256, verbose_name='password')
    annotations = models.IntegerField(default=0, verbose_name='annotations')

    def successAnnotated(self):
        self.annotations += 1
        self.save(update_fields=['annotations'])
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Users'
