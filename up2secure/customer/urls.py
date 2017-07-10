from django.conf.urls import url

from .views import CustomerListView

urlpatterns = [
	url(r'^$', CustomerListView.as_view(), name='customer_list'),
]