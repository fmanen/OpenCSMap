from django.db import models

class Search(models.Model):
    topic = models.CharField(max_length=250)
    author = models.CharField(max_length=250, null=True, blank=True)
    results_by = models.CharField(max_length=250, null=True, blank=True)
    type_of_pub = models.CharField(max_length=250, null=True, blank=True)
    from_date = models.IntegerField(null=True, blank=True)
    to_date = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.topic)

