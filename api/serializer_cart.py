from django.shortcuts import resolve_url
from django.urls.base import reverse
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from education.models import Order, Course


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('name', 'image', 'price_end')

class OrderSerializer(ModelSerializer):
    content_object = CourseSerializer()
    order_link = SerializerMethodField()
    order_delete = SerializerMethodField()
    padi_url = SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('content_object','order_link', 'padi_url','order_delete')
    
    def get_order_link(self ,obj):
        if obj.is_book:
            result = '{}'.format(reverse('api:book_single', args=[obj.content_object.slug]),)
            return result
        else:
            result = '{}'.format(reverse('api:course_single', args=[obj.content_object.slug]),)
            return result

    def get_padi_url(self, obj):
        result = '{}'.format(reverse('api:send_request', args=[obj.pk]),)
        return result
    
    def get_order_delete(self, obj):
        result = '{}'.format(reverse('api:add_to_basket', args=['delete', obj.pk]),)
        return result
        

class PaidSerializer(ModelSerializer):
    content_object = CourseSerializer()
    order_link = SerializerMethodField()
    padi_url = SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('content_object','order_link', 'padi_url')
    
    def get_order_link(self ,obj):
        if obj.is_book:
            result = '{}'.format(reverse('api:book_single', args=[obj.content_object.slug]),)
            return result
        else:
            result = '{}'.format(reverse('api:course_single', args=[obj.content_object.slug]),)
            return result

    def get_padi_url(self, obj):
        result = '{}'.format(reverse('api:send_request', args=[obj.pk]),)
        return result