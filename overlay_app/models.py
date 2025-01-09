from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    text = models.TextField()

    def __str__(self):
        return f"{self.id} - {self.text}"