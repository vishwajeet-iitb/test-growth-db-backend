from django.db import models
# from django.contrib.auth.models import User

# from dashboard.models import Proposals 

# class Proposal(models.Model):
#     proposalNum = models.CharField(max_length=30)
#     #Can include description
#     class Meta:
#         ordering = ['proposalNum']

#     def __str__(self):
#         return self.proposalNum

# class Account(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     proposalPermission = models.ManyToManyField(Proposal)

#     def __str__(self):
#         return self.user.username