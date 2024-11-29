from django.urls import path
from .views import (fi_insert_doctor_medicines,fi_get_all_doctor_medicines,fi_update_doctor_medicines,fi_delete_doctor_medicines)
from .views import fi_insert_doctor_location, fi_update_doctor_location, fi_delete_doctor_location, fi_get_all_doctor_location
from .views import fi_insert_doctor, fi_delete_doctor
from .views import (insert_doctor_location_availability,update_doctor_location_availability,delete_doctor_location_availability,get_all_doctor_location_availability,)
from .views import *

urlpatterns = [    
               
    ######################### Doctor Medicines ############################
    path('insert_doctor_medicine/', fi_insert_doctor_medicines, name='insert_doctor_medicines'),
    path('update_doctor_medicine/<int:doctor_medicine_id>/', fi_update_doctor_medicines, name='update_doctor_medicine'),
    path('delete_doctor_medicine/<int:doctor_medicine_id>/', fi_delete_doctor_medicines, name='delete_doctor_medicine'),
    path('get_all_doctor_medicines/', fi_get_all_doctor_medicines, name='get_all_doctor_medicines'),
    path('get_all_doctor_medicine_bydoctorid_medicinename/', fi_get_all_doctor_medicine_bydoctorid_medicinename, name='get_all_doctor_medicine_bydoctorid_medicinename'),
     
    ######################### Doctor Location ############################
    path('insert_doctor_location/', fi_insert_doctor_location),
    path('update_doctor_location/', fi_update_doctor_location),
    path('delete_doctor_location/<int:doctor_location_id>/', fi_delete_doctor_location),
    path('get_all_doctor_location/', fi_get_all_doctor_location),
    
    ######################### Doctor  ############################    
    path('insert_doctor/', fi_insert_doctor, name='fi_insert_doctor'),
    path('delete_doctor/<int:doctor_id>/', fi_delete_doctor, name='fi_delete_doctor'),
    path("get_doctor_by_id/",get_doctor_by_id),
    path("update_doctor_details/",update_doctor_details),
    # path("get_doctor_profileby_token/",get_doctor_profileby_token),

    ############################# Doctor location Availability #################################
    path('insert_doctor_location_availability/', insert_doctor_location_availability, name='insert_doctor_location_availability'),
    path('update_doctor_location_availability/', update_doctor_location_availability, name='update_doctor_location_availability'),
    path('delete_doctor_location_availability/<int:doctor_location_availability_id>/', delete_doctor_location_availability, name='delete_doctor_location_availability'),
    path('get_all_doctor_location_availability/', get_all_doctor_location_availability, name='get_all_doctor_location_availability'),
    
    path("insert_consultAndMedic_fees/",insert_ConsultMedic_Fees),

    #################################Lab Investigations#########################################
    path('insert_labinvestigations/', fi_insert_labinvestigations, name='fi_insert_labinvestigations'),
    path('delete_labinvestigations/', fi_delete_labinvestigations, name='fi_delete_labinvestigations'),
    path("get_labinvestigations_by_id/",fi_get_labinvestigations_by_id, name='fi_get_labinvestigations_by_id'),
    path("update_labinvestigations/",fi_update_labinvestigations, name='fi_update_labinvestigations'),

    
    #########################New Urls####################################
    path("get_medical_service_fee_details/",get_medical_service_fee_details),
    path("get_consultation_fee_details/",get_consultation_fee_details),
    path("update_consultation_fee_details/",update_consultation_fee_details),
    path("update_medical_service_fee_details/",update_medical_service_fee_details),
    path("get_doctor_location_availability/",get_doctor_location_availability),#new
    path("insert_doctor_leave/",insert_doctor_leave),
    path("get_doctor_leave_details/",get_doctor_leave_details),
    path("update_doctor_leave/",update_doctor_leave),
    path("get_doctor_profileby_token/",get_doctor_profileby_token),
    path("get_doctor_related_info/",get_doctor_related_info),

    
    path('get_doctor_location_bylocationtoken/', get_doctor_location_bylocationtoken),

    path("insert_user/",insert_user),
    path("get_all_users_by_location/",get_all_users_by_location),
    path("update_user_details/", update_user_details),
    path("update_location_details/",update_location_details),
    path("update_location_image/",update_location_image),
    path("insert_prescription_settings/",insert_prescription_settings),
    path("get_prescription_settings_by_doctor/",get_prescription_settings_by_doctor),
    path("update_header_image/",update_header_image),
    path("update_prescription_details/",update_prescription_details),
    path('fetch_doctors/',fetch_doctors,name='fetch_doctors'),
    path('doctors_stats/',doctors_stats,name='doctors_stats'),
    path('fillter_doctors/',fillter_doctors,name='fillter_doctors'),
    path('login_desktop/',login_desktop,name='login_desktop'),
    
 
]

