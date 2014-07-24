from django.db import models
from django.contrib.auth.models import User

class HealthWorker(User):
	post_choices = (("ASHA", "Asha_worker"),
                ("ANM", "ANM_worker"),
                ("DOC", "doctor"),
                ("MAN", "Managerial_person"),
                ("OTH", "others") )
	Post = models.CharField(choices=post_choices, max_length=6, default="ASHA")
	phone = models.CharField(max_length=30, null=False)
