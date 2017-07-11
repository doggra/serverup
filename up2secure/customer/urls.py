from django.conf.urls import url

from .views import CustomerListView, Accounting

urlpatterns = [
	url(r'^$', CustomerListView.as_view(), name='customer_list'),
	url(r'^accounting/$', Accounting.as_view(), name='accounting'),
]