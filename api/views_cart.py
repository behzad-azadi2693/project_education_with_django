from requests.api import get
from education.models import Order, Book, Course
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view
from .serializer_cart import OrderSerializer,PaidSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.shortcuts import redirect
import requests
import json
from django.core.mail import send_mail
from datetime import datetime

@api_view(['GET',])
def add_to_basket(request, name, pk):
    if name == 'course':
        file = get_object_or_404(Course, pk=pk, is_free = False)
        order = file.courses.filter(user = request.user)
        if order:
            return redirect('api:course_single', file.slug)
        else:
            basket = Order(content_object = file, user = request.user, is_book = False)
            basket.save()
            return redirect('api:course_single', file.slug)
    if name == 'book':
        file = get_object_or_404(Book, pk=pk, is_free = False)
        order = file.books.filter(user=request.user)
        if order:
            return redirect('api:book_single', file.slug)
        else:
            basket = Order(content_object = file , user = request.user, is_book = True)
            basket.save()
            return redirect('api:book_single', file.slug)

    if name == 'delete':
        order = get_object_or_404(Order, is_paid = False)
        order.delete()
        return redirect('api:basket')


@api_view(['GET'])
def basket(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')

    orders = Order.objects.filter(user = request.user, is_paid = False)
    srz = OrderSerializer(orders, many=True)

    return Response(srz.data , status=status.HTTP_200_OK)


@api_view(['GET',])
def order(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')
    
    orders = Order.objects.filter(user=request.user, is_paid=True)

    srz = PaidSerializer(orders, many=True).data
    return Response(srz, status=status.HTTP_200_OK)


MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
email = 'email@example.com'  # Optional
mobile = '09123456789'  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://localhost:8000/verify'

@api_view(['GET',])
def send_request(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    amount = order.content_object.price_end()
    req_data = {
        "merchant_id": MERCHANT,
        "amount": int(amount),
        "callback_url": f'{CallbackURL}/{pk}/',
        "description": description,
        "metadata": {"mobile": mobile, "email": email}
    }
    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
        req_data), headers=req_header)
    authority = req.json()['data']['authority']
    if len(req.json()['errors']) == 0:
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


@api_view(['GET', ])
def verify(request, pk):
    order = get_object_or_404(Order, pk=pk)
    amount = order.content_object.price_end()

    t_status = request.GET.get('Status')
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req_data = {
            "merchant_id": MERCHANT,
            "amount": int(amount),
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                order.is_paid = True
                order.price_paide = int(amount)
                order.code_payment = req.json()['data']['ref_id']
                order.save()
                subject = f'payment cache in {datetime.now()}'
                message = f'this {order.user.email} buy {order.content_object.name} paied {amount} RefId {order.code_payment}'
                email = ['admin@gmail.com']
                if not order.is_book:
                    email.append(order.content_object.teacher.user.email)
                send_mail(
                    subject,
                    message,
                    'Education Site',
                    email,
                    fail_silently=False,
                )
                return HttpResponse('Transaction success.\nRefID: ' + str(
                    req.json()['data']['ref_id']
                ))
            elif t_status == 101:
                return HttpResponse('Transaction submitted : ' + str(
                    req.json()['data']['message']
                ))
            else:
                return HttpResponse('Transaction failed.\nStatus: ' + str(
                    req.json()['data']['message']
                ))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
    else:
        return HttpResponse('Transaction failed or canceled by user')