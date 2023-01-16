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
    annotations = models.IntegerField(default=0, verbose_name='有效标注量')
    sentences = models.IntegerField(default=0, verbose_name='总标注量')
    verifications = models.IntegerField(default=0, verbose_name='验证量')

    def addVerifications(self):
        self.verifications += 1
        self.save(update_fields=['verifications'])

    def addSentence(self):
        self.sentences += 1
        self.save(update_fields=['sentences'])

    def successAnnotated(self):
        self.annotations += 1
        self.save(update_fields=['annotations'])
    
    def failedAnnotated(self):
        self.annotations -= 1
        self.save(update_fields=['annotations'])
    
    def __str__(self):
        return f"{self.name} ({self.id})"
    
    class Meta:
        verbose_name_plural = 'Users'
