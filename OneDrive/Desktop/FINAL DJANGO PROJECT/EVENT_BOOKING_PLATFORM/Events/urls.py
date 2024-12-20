# Step 9: Configure URLs in booking/urls.py
from django.urls import path

from . import views
from .views import event_list, book_event

urlpatterns = [
    path('',views.index,name='index'),
    path('event_list/', event_list, name='event_list'),
    path('book/<int:event_id>/', views.book_event, name='book_event'),

    path('pay/<int:event_id>/', views.pay, name='pay'),

    path('stk/', views.stk, name="stk"),
    path('about/', views.about, name='about'),
    path('contact_us/', views.contact, name='contact_us'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
     path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
  ]
