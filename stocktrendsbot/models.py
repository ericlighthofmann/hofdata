from django.db import models

class Company(models.Model):

    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    ipo_year = models.CharField(max_length=10)
    sector = models.CharField(max_length=55)
    industry = models.CharField(max_length=55)

    def __str__(self):
        return self.name

class PostRepliedTo(models.Model):

    submission_id = models.IntegerField()

    def __str__(self):
        return self.submission_id
