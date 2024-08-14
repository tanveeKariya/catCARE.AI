from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome),
    path('login/', views.user_login),
    path('register/',views.register),
    path('logout/', views.user_logout),
    path('success/', views.success),
    path('about/', views.about),
    path('contact', views.contact),
    path('history', views.history),
    path('product/', views.product),
    path('predict/', views.predict),
    path('sendmail', views.sendmail, name='sendmail'),
    path('chat/', views.chat_view, name='chat'),

]