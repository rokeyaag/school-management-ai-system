from django.urls import path
from . import views
from . import bulk_upload
from . import pdf_views
from . import id_card_views
from . import report_card_views

urlpatterns = [
    path('', views.student_list, name='student-list'),
    path('generate-id/', views.generate_id, name='generate-id'),
    path('bulk-upload/', bulk_upload.bulk_upload_students, name='student-bulk-upload'),
    path('bulk-template/', bulk_upload.bulk_upload_template, name='student-bulk-template'),
    path('pdf/', pdf_views.student_list_pdf, name='student-list-pdf'),
    path('id-cards/', id_card_views.student_id_cards_pdf, name='student-id-cards'),
    path('all-report-cards/', report_card_views.all_report_cards_pdf, name='all-report-cards'),
    path('<int:pk>/', views.student_detail, name='student-detail'),
    path('<int:pk>/report-card/', report_card_views.student_report_card_pdf, name='student-report-card'),
    path('<int:pk>/guardian/', views.add_guardian, name='add-guardian'),
]