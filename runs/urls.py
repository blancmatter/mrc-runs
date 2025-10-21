from django.urls import path
from . import views

urlpatterns = [
    path('', views.run_list, name='run_list'),
    path('signup/<int:run_id>/', views.run_signup, name='run_signup'),
    path('cancel/<int:run_id>/', views.run_cancel, name='run_cancel'),
]
