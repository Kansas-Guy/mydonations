from django.db import models

# Create your models here.

class Donor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} <{self.email}>"

class Donation(models.Model):
    # Donor Information
    first_name = models.CharField(max_length=30, default='John')
    last_name = models.CharField(max_length=30, default='Doe')
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=20)

    #Donation Information
    designation = models.CharField(max_length=50, null=True,)
    amount_dollars = models.DecimalField(max_digits=15, decimal_places=2)
    amount_cents = models.IntegerField()
    net_amount_cents = models.IntegerField(null=True, blank=True)
    total_fees_cents = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3)
    transaction_date = models.CharField(max_length=100)
    transaction_id = models.UUIDField(primary_key=True)
    transaction_category = models.CharField(max_length=50, default="donation")

    # Billing info
    donor_name = models.CharField(max_length=50)
    billing_street = models.TextField(null=True, blank=True)
    billing_city = models.CharField(max_length=100, null=True, blank=True)
    billing_state = models.CharField(max_length=100, null=True, blank=True)
    billing_post_code = models.CharField(max_length=20, null=True, blank=True)
    billing_country = models.CharField(max_length=50, null=True, blank=True)

    # Full response for back up
    raw_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_id} — {self.amount_cents/100:.2f} {self.currency}"