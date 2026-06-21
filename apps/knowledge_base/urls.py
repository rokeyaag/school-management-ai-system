from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.subject_list, name='kb-subject-list'),
    path('documents/', views.document_list, name='kb-document-list'),
    path('documents/<int:pk>/', views.document_detail, name='kb-document-detail'),
    path('ask/', views.ask_textbook, name='kb-ask'),
    path('upload-pdf/', views.upload_pdf, name='kb-upload-pdf'),
    path('upload-image/', views.upload_image, name='kb-upload-image'),
    path('upload-scanned-pdf/', views.upload_scanned_pdf, name='kb-upload-scanned-pdf'),
]