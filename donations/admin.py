from django.contrib import admin
from .models import Donor, Donation

# Register your models here.

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'amount_dollars',
        'designation',
        'transaction_date',
    )
    list_filter = (
        'first_name',
        'last_name',
        'amount_dollars',
        'transaction_date',
    )
    search_fields = (
        'first_name',
        'last_name',
        'designation'
    )