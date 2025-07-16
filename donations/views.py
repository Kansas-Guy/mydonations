from pydoc import describe

from django.db.models.expressions import result
from django.shortcuts import render, redirect
from django.conf import settings
import logging
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .sky_auth import get_bbms_access_token
import requests
from .models import Donation
from dateutil import parser as date_parser
from django.utils import timezone

logger = logging.getLogger(__name__)
# Create your views here.

def donate_form(request):
    return render(request, 'form.html', {
        'BBMS_PUBLIC_KEY': settings.BBMS_PUBLIC_KEY,
        'BBMS_MERCHANT_ID': settings.BBMS_MERCHANT_ID,
    })

@csrf_exempt
def donate_finalize(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("POST only")

    data = json.loads(request.body)
    token = data.get('checkoutToken')
    if not token:
        return JsonResponse({ "error": "Missing checkoutToken"}, status=400)

    access_token = get_bbms_access_token()

    designation = data.get("designation")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    amount_dollars = data.get("amount")

    # Build the BBMS API Call
    url = "https://api.sky.blackbaud.com/payments/v1/checkout/transaction"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Bb-Api-Subscription-Key": settings.BB_API_SUBSCRIPTION,
    }


    payload = {
        "authorization_token": token,
        # transaction call must be in cents
        "amount": data['amount'] * 100 ,
    }

    response = requests.post(url, json=payload, headers=headers)

    if not response.ok:
        return JsonResponse({
            "status": "error",
            "detail": response.json(),
        }, status=response.status_code)

    result = response.json()

    # 1) Dump it to the log so we can see exactly what keys & types we have:
    logger.debug("BBMS transaction response: %r", result)

    # 2) Pull out the raw value
    raw_date = result.get("transaction_date")

    # 3) If it somehow came through as bytes, decode it:
    if isinstance(raw_date, (bytes, bytearray)):
        raw_date = raw_date.decode("utf-8")
    try:
        txn_date = date_parser.isoparse(raw_date)
    except Exception:
        print("Failed to parse transaction_date %r, defaulting to now()", raw_date)
        txn_date = timezone.now()

    billing = result.get("billing_info", {})
    card = result.get("credit_card", {})


    # 4) Parse & convert
    transaction_id = result["id"]
    amount_cents = int(result["amount"])  # already in cents
    net_amount_cents = result.get("net_amount")
    total_fees_cents = result.get("total_fees")
    currency = result.get("currency", "USD")
    category = result.get("transaction_category", "donation")
    email = result.get("email_address")
    phone = result.get("phone_number")
    date_time = result.get("transaction_date")

    # 5) Create the Donation record
    donation = Donation.objects.create(
        first_name=first_name,
        last_name=last_name,
        donor_name=card.get("name"),
        email= email,
        phone = phone,
        designation = designation,
        transaction_id=transaction_id,
        amount_dollars = amount_dollars,
        amount_cents=amount_cents,
        net_amount_cents=net_amount_cents,
        total_fees_cents=total_fees_cents,
        currency=currency,
        transaction_date=date_time,
        transaction_category=category,

        billing_street=billing.get("street"),
        billing_city=billing.get("city"),
        billing_state=billing.get("state"),
        billing_post_code=billing.get("post_code"),
        billing_country=billing.get("country"),

        raw_response=result
    )

    return JsonResponse({
        "status": "success",
        "transactionId": result.get('transactionId'),
        "amount": result.get('amount')
    })
def bbms_webhook(request):
    pass

@csrf_exempt
def test_send_email(request):
    logger.debug(f"test_send_email hit with method={request.method}")
    if request.method != 'POST':
        return JsonResponse(
            {'status': "error", "message": "POST only allowed"}, status=400
        )

    try:
        payload = json.loads(request.body.decode('utf-8'))
        donor_email = payload['billing_address_email']
        donor_first_name = payload['billing_address_first_name']
        amount = payload['amount']
        designation = payload['note']

        message = Mail(
            from_email = settings.DEFAULT_FROM_EMAIL,
            to_emails = donor_email,
        )
        message.template_id = settings.SENDGRID_RECEIPT_TEMPLATE_ID
        message.dynamic_template_data = {
            "donor_first_name": donor_first_name,
            "amount": amount,
            "designation": designation,
        }

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        # decode any bytes before returning JSON
        body = getattr(response, 'body', None)
        body_str = body.decode('utf-8') if isinstance(body, (bytes, bytearray)) else str(body)

        return JsonResponse({
            "status": "success",
            "sg_status": response.status_code,
            "sg_message": body_str,
        })
    except Exception as e:
        logger.exception("Error in the test_send_email")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
