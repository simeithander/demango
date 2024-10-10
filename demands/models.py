from django.db import models
from django.contrib.auth.models import User

class Demands(models.Model):
    STATUS_CHOICES = [
        ('Em andamento', 'Em andamento'),
        ('Em validação', 'Em validação'),
        ('Finalizada', 'Finalizada')
    ]
    
    DEMAND_CHOICES = [
        ('Projetos / Melhoria', 'Projetos / Melhoria'),
        ('QAS', 'QAS'),
        ('Outro', 'Outro')
    ]

    title = models.CharField(max_length=255)
    demand = models.CharField(max_length=100)
    url = models.CharField(max_length=255, null=True, blank=True)
    objective = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    demand_type = models.CharField(max_length=20, choices=DEMAND_CHOICES, default="Outro")
    summary = models.TextField()
    dueDate = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demands')

    def __str__(self):
        return self.title
    
class Activity(models.Model):
    title = models.CharField(max_length=255)
    time = models.CharField(max_length=20)
    date = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    demand = models.ForeignKey(Demands, on_delete=models.CASCADE, related_name='activities')

    def __str__(self):
        return self.title

