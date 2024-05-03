from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('user_view/', views.user_view, name='user_view'),
    path('user_detail/<int:id>/', views.user_detail, name='user_detail'),
    path('document_files/', views.document_files, name='document_files'),
    path('asign_document/', views.asign_document, name='asign_document'),
    path('asign_document_detail/<int:id>/', views.asign_document_detail, name='asign_document_detail'),
    path('sign_document/', views.sign_document, name='sign_document'),
    path('sign_document_detail/<int:id>/', views.sign_document_detail, name='sign_document_detail'),
    path('signed_document/', views.signed_document, name='signed_document'),
    path('signed_document_detail/<int:id>/', views.signed_document_detail, name='signed_document_detail'),
]