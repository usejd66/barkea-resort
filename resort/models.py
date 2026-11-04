from django.db import models


class ContactMessage(models.Model):
    fullname = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.fullname} ({self.email})"