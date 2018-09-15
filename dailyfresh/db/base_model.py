from django.db import models
class BaseModel(models.Model):
    '''bastract'''
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name="update_time")
    is_delete = models.BooleanField(default=False,verbose_name="False_not_del")
    class Meta:
        abstract = True