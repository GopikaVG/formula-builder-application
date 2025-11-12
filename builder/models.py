from django.db import models

# Create your models here.
class variable(models.Model):
    name=models.CharField(max_length=100,unique=True)
    variabletype=[('CONSTANT','Constant'),('DYNAMIC','Dynamic')]
    type=models.CharField(max_length=10,choices=variabletype)
    value=models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering=['name']

class formula(models.Model):
    name=models.CharField(max_length=100)
    expression=models.TextField()

    def __str__(self):
        return self.name
    
    class Meta:
        ordering=['name']