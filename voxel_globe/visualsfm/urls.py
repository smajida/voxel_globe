from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.make_order_1, name='make_order_1'),
    url(r'^order/(?P<image_set_id>\d+)$', views.make_order_2, name="make_order_2"),
    url(r'^order/(?P<image_set_id>\d+)/(?P<scene_id>\d+)$', views.make_order_3, name="make_order_3"),
    url(r'^status/(?P<task_id>[a-f\-\d]+)$', views.order_status, name='order_status')
]