from django.contrib import admin
from .models import Donor, Donation
import csv
from django.http import HttpResponse

def export_as_csv(modeladmin, request, queryset):
    """
    Admin action to export selected Donation records as a CSV file.
    """
    # Create the HttpResponse with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=donations_export.csv'

    writer = csv.writer(response)
    # Write header row (adjust column names to your model fields)
    writer.writerow([
        'Gift Date and Time',
        'Donor First Name',
        'Donor Last Name',
        'Gift Amount',
        'Designation',
        'Email',
        'Phone',
        'Address',
        'City',
        'State',
        'Zip Code',
        'Card Name'
        'Transaction ID',
        # …any other fields you care about…
    ])

    # Write data rows
    for donation in queryset:
        writer.writerow([
            donation.transaction_date,
            donation.first_name,
            donation.last_name,
            donation.amount_dollars,
            donation.designation,
            donation.email,
            donation.phone,
            donation.billing_street,
            donation.billing_city,
            donation.billing_state,
            donation.billing_post_code,
            donation.donor_name,
            donation.transaction_id,
            # …and so on…
        ])

    return response

export_as_csv.short_description = "Export selected donations as CSV"

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
    actions = [export_as_csv]

    ordering = ['-transaction_date']