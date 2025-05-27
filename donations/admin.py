from django.contrib import admin
from .models import Donor, Donation

# Register your models here.

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'donor_name',
        'amount_cents',
        'designation',
        'transaction_date',
        'transaction_category',
    )
    list_filter = (
        'currency',
        'transaction_category',
        'transaction_date',
    )
    search_fields = (
        'donor_name',
    )