from django.contrib import admin
# from .models import Account, Proposal
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# class AccountInline(admin.StackedInline):
#     model = Account
#     can_delete = False
#     verbose_name_plural = 'Accounts'

# class CustomUserAdmin (UserAdmin):
#     inlines = (AccountInline,)

# admin.site.unregister(User)
# admin.site.register(User,CustomUserAdmin)
# admin.site.register(Proposal)