from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from datetime import datetime
from rest_framework.views import APIView

from medicify_project.models import * 
from medicify_project.serializers import *
from django.db.models import Q

from django.db import connection
from django.utils import timezone
import string
import random

import uuid
import os

# from .models import Tbldoctorlocations
# from .serializers import DoctorLocationSerializer
# from .models import Tbldoctors  # Import the correct model
# from .serializers import DoctorSerializer
# from .models import Tbldoctorlocationavailability
# from .serializers import DoctorLocationAvailabilitySerializer


######################### Doctor Medicines ############################
##################### insert  ##########
@api_view(['POST'])
def fi_insert_doctor_medicines(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data
            data['isdeleted'] = 0  # Assuming isdeleted is a field in your model

            # Validations for required fields
            required_fields = ['medicine_code', 'medicine_name', 'medicine_form']
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                res = {
                    'message_code': 999,
                    'message_text': f"Missing required fields: {', '.join(missing_fields)}",
                    'message_data': {},
                    'message_debug': debug if debug else []
                }
            else:
                try:
                    # Creating a new instance of TbldoctorMedicines model
                    # doctor_medicine = TbldoctorMedicines(**data)

                    # # Saving the new instance to the database
                    # doctor_medicine.save()
                    doctorMedicinesSerializer = TbldoctorMedicinesSerializer(data=data)
                    if doctorMedicinesSerializer.is_valid():
                        instance = doctorMedicinesSerializer.save()
                        last_doctor_medicine_id = instance.doctor_medicine_id

                        res = {
                            'message_code': 1000,
                            'message_text': 'Success',
                            'message_data': last_doctor_medicine_id,
                            'message_debug': debug if debug else []
                        }
                    else:
                        res = {
                            'message_code': 2000,
                            'message_text': 'Validation Error',
                            'message_errors': doctorMedicinesSerializer.errors
                        } 
                except Exception as e:
                    res = {
                        'message_code': 999,
                        'message_text': f"Failed to insert doctor medicine. Error: {str(e)}",
                        'message_data': {},
                        'message_debug': debug if debug else []
                    }
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_insert_doctor_medicines. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_200_OK)

##################### update  ##########
@api_view(['POST'])
def fi_update_doctor_medicines(request, doctor_medicine_id):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data
            doctor_medicine_id = int(doctor_medicine_id)

            if not doctor_medicine_id:
                return Response({'message_code': 999, 'message_text': 'Doctor medicine id is required.'}, status=status.HTTP_200_OK)

            try:
                doctor_medicine = TbldoctorMedicines.objects.get(doctor_medicine_id=doctor_medicine_id)
            except TbldoctorMedicines.DoesNotExist:
                return Response({
                    'message_code': 999,
                    'message_text': f'Doctor medicine with id {doctor_medicine_id} does not exist.',
                    'message_debug': debug if debug else {}
                }, status=status.HTTP_200_OK)

            fields_to_update = ['medicine_code', 'medicine_name', 'medicine_form', 'medicine_frequency',
                                 'medicine_duration', 'medicine_dosages', 'medicine_manufacture', 'medicine_pack_size',
                                 'medicine_preservation', 'medicine_min_stock', 'medicine_gst', 'medicine_content_name','price']

            for field in fields_to_update:
                if data.get(field) is not None:
                    setattr(doctor_medicine, field, data.get(field, ''))

            doctor_medicine.save()

            serializer = TbldoctorMedicinesSerializer(doctor_medicine)

            res = {
                'message_code': 1000,
                'message_text': 'Success',
                'message_data': serializer.data,
                'message_debug': debug if debug else []
            }
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_update_doctor_medicines. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_200_OK)
##################### Delete  ##########
@api_view(['DELETE'])
def fi_delete_doctor_medicines(request, doctor_medicine_id):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'DELETE':
            if not doctor_medicine_id:
                return Response({'message_code': 999, 'message_text': 'Doctor medicine id is required.'}, status=status.HTTP_200_OK)

            try:
                # Fetching the existing TbldoctorMedicines instance from the database
                doctor_medicine = TbldoctorMedicines.objects.get(doctor_medicine_id=doctor_medicine_id)
            except TbldoctorMedicines.DoesNotExist:
                return Response({
                    'message_code': 999,
                    'message_text': f'Doctor medicine with id {doctor_medicine_id} does not exist.',
                    'message_debug': debug if debug else {}
                }, status=status.HTTP_200_OK)

            # Soft delete logic
            doctor_medicine.isdeleted = 1
            doctor_medicine.deletedby = request.user.id  # Assuming you have a user object in your request
            doctor_medicine.deletedreason = "Soft delete reason"  # Provide a reason for the deletion if necessary
            doctor_medicine.save()

            res = {
                'message_code': 1000,
                'message_text': 'Success',
                'message_data': {'doctor_medicine_id': doctor_medicine.doctor_medicine_id},
                'message_debug': debug if debug else []
            }
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_delete_doctor_medicines. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_200_OK)
##################### Get  ##########
@api_view(['POST'])
def fi_get_all_doctor_medicines(request):
    debug = ""
    res = {'message_code': 999, 'message_text': "Failure", 'message_data': {'Functional part is commented.'}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data

            doctor_medicine_id = data.get('doctor_medicine_id', '')
            if not doctor_medicine_id:
                return Response({'message_code': 999, 'message_text': 'Doctor medicine id is required.'}, status=status.HTTP_200_OK)

            try:
                # Fetching the existing TbldoctorMedicines instance from the database
                doctor_medicine = TbldoctorMedicines.objects.filter(doctor_medicine_id=doctor_medicine_id)
                serializer = TbldoctorMedicinesSerializer(doctor_medicine, many=True)

                return Response({
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': serializer.data,
                    'message_debug': debug if debug else []
                }, status=status.HTTP_200_OK)
            except TbldoctorMedicines.DoesNotExist:
                return Response({
                    'message_code': 999,
                    'message_text': f'Doctor medicine with id {doctor_medicine_id} not found.',
                    'message_data': { },
                    'message_debug': debug if debug else []
                }, status=status.HTTP_200_OK)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_get_all_doctor_medicines. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_200_OK)


#########################get all doctor medicine bydoctorid and medicinename##########################
# @api_view(['POST'])
# def fi_get_all_doctor_medicine_bydoctorid_medicinename(request):
#     debug = ""
#     res = {'message_code': 999, 'message_text': "Failure", 'message_data': {'Functional part is commented.'}, 'message_debug': debug}

#     try:
#         if request.method == 'POST':
#             data = request.data

#             doctor_id = data.get('doctor_id', '')
#             medicine_name = data.get('medicine_name', '')
#             if not doctor_id:
#                 return Response({'message_code': 999, 'message_text': 'Doctor id is required.'}, status=status.HTTP_200_OK)
#             try:
                
#                 doctor_medicines_queryset = TbldoctorMedicines.objects.filter(doctor_id=doctor_id,isdeleted=0)

#                 if medicine_name:
#                     doctor_medicines_queryset = doctor_medicines_queryset.filter(medicine_name__icontains=medicine_name)

#                 serializer = TbldoctorMedicinesSerializer(doctor_medicines_queryset, many=True)


#                 return Response({
#                     'message_code': 1000,
#                     'message_text': 'Success',
#                     'message_data': serializer.data,
#                     'message_debug': debug if debug else []
#                 }, status=status.HTTP_200_OK)
#             except TbldoctorMedicines.DoesNotExist:
#                 return Response({
#                     'message_code': 999,
#                     'message_text': f'Doctor medicine with id  not found.',
#                     'message_data': { },
#                     'message_debug': debug if debug else []
#                 }, status=status.HTTP_200_OK)
#     except Exception as e:
#         res = {
#             'message_code': 999,
#             'message_text': f'Error in fi_get_all_doctor_medicines. Error: {str(e)}',
#             'message_data': {},
#             'message_debug': debug if debug else []
#         }

#     return Response(res, status=status.HTTP_200_OK)
@api_view(['POST'])
def fi_get_all_doctor_medicine_bydoctorid_medicinename(request):
    debug = ""
    res = {'message_code': 999, 'message_text': "Failure", 'message_data': {'Functional part is commented.'}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data

            doctor_id = data.get('doctor_id', '')
            medicine_name = data.get('medicine_name', '')
            if not doctor_id:
                return Response({'message_code': 999, 'message_text': 'Doctor id is required.'}, status=status.HTTP_200_OK)
            try:
                # Modify the query to include records with doctor_id as NULL
                doctor_medicines_queryset = TbldoctorMedicines.objects.filter(
                    Q(doctor_id=doctor_id) | Q(doctor_id__isnull=True),
                    isdeleted=0
                )

                if medicine_name:
                    doctor_medicines_queryset = doctor_medicines_queryset.filter(medicine_name__icontains=medicine_name)

                serializer = TbldoctorMedicinesSerializer(doctor_medicines_queryset, many=True)

                return Response({
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': serializer.data,
                    'message_debug': debug if debug else []
                }, status=status.HTTP_200_OK)
            except TbldoctorMedicines.DoesNotExist:
                return Response({
                    'message_code': 999,
                    'message_text': 'Doctor medicine with id not found.',
                    'message_data': {},
                    'message_debug': debug if debug else []
                }, status=status.HTTP_200_OK)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_get_all_doctor_medicines. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_200_OK)


######################### Doctor Medicines ############################
##################### insert  ##########
@api_view(['POST'])
def fi_insert_doctor_location(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}

    try:
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
        request.data['location_qr_url'] = 'http://15.206.32.93/drishti_bot/bot/?id='+str(random_string)
        request.data['location_token'] = str(random_string)
        serializer = DoctorLocationSerializer(data=request.data)
        # print("Request Data:", request.data)

        if serializer.is_valid():
            doctor_location = serializer.save()
            serialized_data = DoctorLocationSerializer(doctor_location).data
            res = {
                'message_code': 1000,
                'message_text': 'Success',
                'message_data': serialized_data,
                'message_debug': [{"Debug": debug}] if debug != "" else []
            }
        else:
            debug = f"Serializer errors: {serializer.errors}"
            res = {
                'message_code': 999,
                'message_text': 'Invalid data provided.',
                'message_data': {},
                'message_debug': [{"Debug": debug}] if debug != "" else []
            }
    except Exception as e:
        debug = f"Error: {str(e)}"
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_insert_doctor_location. {debug}',
            'message_data': [],
            'message_debug': [{"Debug": debug}] if debug != "" else []
        }

    return Response(res, status=status.HTTP_200_OK)

##################### update  ##########
@api_view(['POST'])
def fi_update_doctor_location(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        doctor_location_id = request.data.get('doctor_location_id')
        if doctor_location_id:
            try:
                doctor_location = Tbldoctorlocations.objects.get(doctor_location_id=doctor_location_id)
            except Tbldoctorlocations.DoesNotExist:
                res = {
                    'message_code': 999,
                    'message_text': 'Doctor location not found.',
                    'message_data': {},
                    'message_debug': debug if debug else {}
                }
                return Response(res, status=status.HTTP_404_NOT_FOUND)

            serializer = DoctorLocationSerializer(doctor_location, data=request.data, partial=True)
            if serializer.is_valid():
                updated_data = serializer.validated_data  # Get the validated data after a successful update
                serializer.save()
                res = {
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': doctor_location_id,
                    'message_debug': debug if debug else []
                }
                return Response(res, status=status.HTTP_200_OK)
            else:
                res = {
                    'message_code': 999,
                    'message_text': serializer.errors,
                    'message_data': {},
                    'message_debug': debug if debug else []
                }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_update_doctor_location. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def update_location_details(request):
    try:
        doctor_location_id = request.data.get('doctor_location_id')
        if not doctor_location_id:
            return Response({'message_code': 999, 'message_text': 'Doctor location ID is missing.', 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)

        doctor_location = Tbldoctorlocations.objects.get(doctor_location_id=doctor_location_id)

        serializer = DoctorLocationSerializer(doctor_location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated data

            return Response({'message_code': 1000, 'message_text': 'Location details updated successfully.', 'message_data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'message_code': 999, 'message_text': serializer.errors, 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)

    except Tbldoctorlocations.DoesNotExist:
        return Response({'message_code': 999, 'message_text': 'Doctor location not found.', 'message_data': {}}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'message_code': 999, 'message_text': f'Error updating location details. Error: {str(e)}', 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def update_location_image(request):
    try:
        doctor_location_id = request.data.get('doctor_location_id')
        if not doctor_location_id:
            return Response({'message_code': 999, 'message_text': 'Doctor location ID is missing.', 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)

        doctor_location = Tbldoctorlocations.objects.get(doctor_location_id=doctor_location_id)

        new_image_file = request.FILES.get('location_image')
        if new_image_file:
            # Determine the filename for the new image
            if doctor_location.location_image:
                existing_image_filename = os.path.basename(doctor_location.location_image.name)
                new_image_filename = existing_image_filename
            else:
                new_image_filename = new_image_file.name

            # Delete the old image file if it exists
            if doctor_location.location_image:
                old_image_path = doctor_location.location_image.path
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Update the location_image field with the new image file
            doctor_location.location_image.save(new_image_filename, new_image_file)

        return Response({'message_code': 1000, 'message_text': 'Location image updated successfully.', 'message_data': {}}, status=status.HTTP_200_OK)

    except Tbldoctorlocations.DoesNotExist:
        return Response({'message_code': 999, 'message_text': 'Doctor location not found.', 'message_data': {}}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'message_code': 999, 'message_text': f'Error updating location image. Error: {str(e)}', 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)


##################### Delete  ##########
@api_view(['DELETE'])
def fi_delete_doctor_location(request, doctor_location_id):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        doctor_location = Tbldoctorlocations.objects.get(doctor_location_id=doctor_location_id)
        doctor_location.isdeleted = True
        doctor_location.save()
        # doctor_location.delete()

        res = {
            'message_code': 1000,
            'message_text': 'Success',
            'message_data': {'Doctor location deleted successfully.'},
            'message_debug': [{"Debug": debug}] if debug else []
        }
    except Tbldoctorlocations.DoesNotExist:
        res = {
            'message_code': 900,
            'message_text': 'Doctor location not found.',
            'message_data': {},
            'message_debug': [{"Debug": debug}] if debug else []
        }
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_delete_doctor_location. Error: {str(e)}',
            'message_data': {},
            'message_debug': [{"Debug": debug}] if debug else []
        }

    return Response(res, status=status.HTTP_404_NOT_FOUND if res['message_code'] == 900 else status.HTTP_200_OK)
##################### Get  ##########


@api_view(['POST'])
def fi_get_all_doctor_location(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    

    doctor_location_id = request.data.get('doctor_location_id', '')
    
    if not doctor_location_id:
        res = {'message_code': 999, 'message_text': 'doctor location id is required.'}
    else:
        try:
            
            doctor_location = Tbldoctorlocations.objects.filter(
                Q(doctor_location_id=doctor_location_id,isdeleted=0)
            )

            # Serialize the data
            serializer = DoctorLocationSerializer(doctor_location, many=True)
            result = serializer.data
            # last_query = connection.queries[-1]['sql']
            # print(last_query)
            if result:
                res = {
                    'message_code': 1000,
                    'message_text': "Doctor location retrieved successfully.",
                    'message_data': result,
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "Doctor location not found.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res, status=status.HTTP_200_OK)


############################# Doctor ##################################
######################## Insert ############################
@api_view(['POST'])
def fi_insert_doctor(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        data = request.data.copy()  # Create a copy of the data to avoid modifying the original request data
        
        # Convert the date of birth to epoch time
        date_of_birth_str = data.get('doctor_dateofbirth', '')
        if date_of_birth_str:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
            epoch_time = int(date_of_birth.timestamp())
            data['doctor_dateofbirth'] = epoch_time
        
        current_datetime = datetime.now()
        data['createdon']=int(current_datetime.timestamp())
        serializer = DoctorSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            res = {
                'message_code': 1000,
                'message_text': 'Success',
                'message_data': serializer.data,
                'message_debug': debug if debug else []
            }
        else:
            errors = {field: serializer.errors[field][0] for field in serializer.errors}
            res = {
                'message_code': 999,
                'message_text': errors,
                'message_data': {},
                'message_debug': debug if debug else []
            }
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_insert_doctor. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_200_OK if res['message_code'] == 1000 else status.HTTP_400_BAD_REQUEST)

######################## Delete ############################
@api_view(['DELETE'])
def fi_delete_doctor(request, doctor_id):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        doctor = Tbldoctors.objects.get(pk=doctor_id)  # Use the correct model
        doctor.isdeleted = True  # Update the field name
        doctor.save()

        if doctor.isdeleted:
            response_data = {
                'message': f'Doctor ID {doctor_id} deleted successfully.',
            }
            res = {
                'message_code': 1000,
                'message_text': 'Success',
                'message_data': response_data,
                'message_debug': debug if debug else []
            }
        else:
            res = {
                'message_code': 999,
                'message_text': 'Doctor Id not found.',
                'message_data': {},
                'message_debug': debug if debug else []
            }
    except Tbldoctors.DoesNotExist:  # Use the correct model
        res = {
            'message_code': 999,
            'message_text': 'Doctor Id not found.',
            'message_data': {},
            'message_debug': debug if debug else []
        }
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in fi_delete_doctor. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_404_NOT_FOUND if res['message_code'] == 999 else status.HTTP_200_OK)


################################## Doctor location Availability ##########################################
######################## Insert ############################
@api_view(['POST'])
def insert_doctor_location_availability(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            
            data = request.data
            data['isdeleted',]=0
            serializer = DoctorLocationAvailabilitySerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                res = {
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': serializer.data,
                    'message_debug': debug if debug else []
                }
                return Response(res, status=status.HTTP_200_OK)
            else:
                errors = {field: serializer.errors[field][0] for field in serializer.errors}
                error_message = 'Invalid data provided. Please check the following fields:'
                for field, message in errors.items():
                    error_message += f'\n- {field}: {message}'

                res = {
                    'message_code': 999,
                    'message_text': error_message,
                    'message_data': {},
                    'message_debug': debug if debug else []
                }
                return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in insert_doctor_location_availability. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_400_BAD_REQUEST)

######################## Update ############################
@api_view(['POST'])
def update_doctor_location_availability(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data
            doctor_location_availability_id = data.get('Doctor_Location_Availability_Id', None)

            if doctor_location_availability_id is not None:
                try:
                    instance = Tbldoctorlocationavailability.objects.get(doctor_location_availability_id=doctor_location_availability_id, isdeleted=False)
                    serializer = DoctorLocationAvailabilitySerializer(instance, data=data, partial=True)

                    if serializer.is_valid():
                        updated_instance = serializer.save()
                        updated_data = {}

                        for field in serializer.fields:
                            if field in serializer.validated_data:
                                updated_data[field] = updated_instance.__getattribute__(field)

                        res = {
                            'message_code': 1000,
                            'message_text': 'Success',
                            'message_data': updated_data,
                            'message_debug': debug if debug else []
                        }
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        res['message_text'] = 'Invalid data provided.'
                        return Response(res, status=status.HTTP_400_BAD_REQUEST)
                except Tbldoctorlocationavailability.DoesNotExist:
                    res['message_text'] = 'Doctor location availability not found.'
                    return Response(res, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in update_doctor_location_availability. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_400_BAD_REQUEST)


######################## Delete ############################
@api_view(['DELETE'])
def delete_doctor_location_availability(request, doctor_location_availability_id):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'DELETE':
            try:
                instance = Tbldoctorlocationavailability.objects.get(doctor_location_availability_id=doctor_location_availability_id, isdeleted=False)
                instance.isdeleted = True
                instance.save()
                res = {
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': [{'Doctor_Location_Availability_Id': doctor_location_availability_id}],
                    'message_debug': debug if debug else []
                }
                return Response(res, status=status.HTTP_200_OK)
            except Tbldoctorlocationavailability.DoesNotExist:
                res['message_text'] = 'Doctor location availability not found.'
                return Response(res, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in delete_doctor_location_availability. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_404_NOT_FOUND if res['message_code'] == 999 else status.HTTP_200_OK)


######################## Get ############################
@api_view(['POST'])
def get_all_doctor_location_availability(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data
            doctor_location_availability_id = data.get('Doctor_Location_Availability_Id', None)

            if doctor_location_availability_id is not None:
                try:
                    instance = Tbldoctorlocationavailability.objects.get(doctor_location_availability_id=doctor_location_availability_id, isdeleted=False)
                    serializer = DoctorLocationAvailabilitySerializer(instance)
                    res = {
                        'message_code': 1000,
                        'message_text': 'Success',
                        'message_data': serializer.data,
                        'message_debug': debug if debug else []
                    }
                    return Response(res, status=status.HTTP_200_OK)
                except Tbldoctorlocationavailability.DoesNotExist:
                    res['message_text'] = 'Doctor location availability id not found.'
                    return Response(res, status=status.HTTP_404_NOT_FOUND)
            else:
                queryset = Tbldoctorlocationavailability.objects.filter(isdeleted=False)
                serializer = DoctorLocationAvailabilitySerializer(queryset, many=True)
                res = {
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': serializer.data,
                    'message_debug': debug if debug else []
                }
                return Response(res, status=status.HTTP_200_OK)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in get_all_doctor_location_availability. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def get_doctor_by_id(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    doctor_id = request.data.get('doctor_id', None)

    if not doctor_id:
        response_data = {'message_code': 999, 'message_text': 'Doctor ID is required.'}
    else:
        try:
            doctor = Tbldoctors.objects.filter(doctor_id=doctor_id)
            serializer = DoctorSerializer(doctor, many=True)
            result = serializer.data

            response_data = {
                'message_code': 1000,
                'message_text': 'Doctor details are fetched successfully',
                'message_data': result,
                'message_debug': debug
            }

        except Tbldoctors.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Doctor not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_doctor_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    doctor_id = request.data.get('doctor_id', None)
    updated_data = request.data.get('updated_data', {})

    if not doctor_id:
        response_data = {'message_code': 999, 'message_text': 'Doctor ID is required.'}
    elif not updated_data:
        response_data = {'message_code': 999, 'message_text': 'Updated data is required.'}
    else:
        try:
            doctor = Tbldoctors.objects.get(doctor_id=doctor_id)
            # Convert the date string to epoch timestamp
            date_of_birth_str = updated_data.get('doctor_dateofbirth', '')
            if date_of_birth_str:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
                epoch_time = int(date_of_birth.timestamp())
                updated_data['doctor_dateofbirth'] = epoch_time

            serializer = DoctorSerializer(doctor, data=updated_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                result = serializer.data
                response_data = {
                    'message_code': 1000,
                    'message_text': 'Doctor details updated successfully',
                    'message_data': result,
                    'message_debug': debug
                }
            else:
                response_data = {'message_code': 999, 'message_text': 'Invalid data provided.', 'message_debug': serializer.errors}

        except Tbldoctors.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Doctor not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def insert_ConsultMedic_Fees(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    data = request.data
    doctor_id = data.get('doctor_id')
    location_id = data.get('location_id')

    
    avg_time_per_patient = data.get('avg_time_per_patient')
    price = data.get('price')
    title = data.get('title')

    consultation_fee_data = data.get('consultation_fee', {})
    consultation_fee_data['doctor_id'] = doctor_id
    consultation_fee_data['location_id'] = location_id

    consultation_fee_data['avg_time_per_patient'] = avg_time_per_patient
    consultation_fee_data['price'] = price
    consultation_fee_data['title'] = title

    medical_services_fee_data = data.get('medical_services_fee', {})
    medical_services_fee_data['doctor_id'] = doctor_id
    medical_services_fee_data['location_id'] = location_id

    consultation_fee_serializer = ConsultationFeeSerializer(data=consultation_fee_data)
    medical_services_fee_serializer = MedicalServicesFeeSerializer(data=medical_services_fee_data)

    if consultation_fee_serializer.is_valid() and medical_services_fee_serializer.is_valid():
        consultaion=consultation_fee_serializer.save()
        medicalservice=medical_services_fee_serializer.save()
        response_data['message_code']= 1000
        response_data['message_text'] = 'Data successfully saved!'
        response_data['message_data']={'consultation_fee_id':consultaion.consultation_fee_id,'medical_service_fee_id':medicalservice.medical_service_fee_id}
    else:
        errors = {
            'consultation_fee_errors': consultation_fee_serializer.errors,
            'medical_services_fee_errors': medical_services_fee_serializer.errors
        }
        response_data['message_text'] = 'Failed to save data. Please check the errors.'
        response_data['errors'] = errors

    return Response(response_data, status=status.HTTP_200_OK)




# @api_view(["POST"])
# def get_doctor_profileby_token(request):
#     debug = []
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Functional part is commented.',
#         'message_data': [],
#         'message_debug': debug
#     }

#     doctor_login_token = request.data.get('doctor_login_token', None)

#     if not doctor_login_token:
#         response_data = {'message_code': 999, 'message_text': 'Doctor login token is required.'}
#     else:
#         try:
#             doctor = Tbldoctors.objects.filter(doctor_login_token=doctor_login_token)
#             serializer = DoctorSerializer(doctor, many=True)
#             result = serializer.data
#             if result:
#                 response_data = {
#                     'message_code': 1000,
#                     'message_text': 'Doctor details are fetched successfully',
#                     'message_data': result,
#                     'message_debug': debug
#                 }
#             else:
#                  response_data = {
#                     'message_code': 999,
#                     'message_text': 'no doctor token match.',
#                     'message_data': [],
#                     'message_debug': debug
#                 }

#         except Tbldoctors.DoesNotExist:
#             response_data = {'message_code': 999, 'message_text': 'no doctor token match.', 'message_debug': debug}

#     return Response(response_data, status=status.HTTP_200_OK)


############################################ Lab Investigations


@api_view(['POST'])
def fi_get_labinvestigations_by_id(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
        

    investigation_id = request.data.get('investigation_id', '')

    if not investigation_id:
        res = {'message_code': 999, 'message_text': 'investigation id is required.'}
    else:
        try:
            
            # Fetch data using Django ORM
            lab_investigation = Tbllabinvestigations.objects.filter(
                Q(investigation_id=investigation_id,isdeleted=0)
            )

            # Serialize the data
            serializer = TbllabinvestigationsSerializer(lab_investigation, many=True)
            result = serializer.data

            if result:
                res = {
                    'message_code': 1000,
                    'message_text': "Lab investigations retrieved successfully.",
                    'message_data': result,
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "Lab investigations for this investigation id not found.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def fi_insert_labinvestigations(request):
    
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
     
    # Extract data from request
    doctor_id = request.data.get('doctor_id', '')
    investigation_category = request.data.get('investigation_category', '')
    investigation_name = request.data.get('investigation_name', '')

    # Validate appointment_id
    if not doctor_id:
        res = {'message_code': 999,'message_text': 'Doctor id is required'}
    elif not investigation_category:
        res = {'message_code': 999,'message_text': 'Investigation category is required'}
    elif not investigation_name:
        res = {'message_code': 999,'message_text': 'Investigation name is required'}
    else:
        try:
            
            investigation_data = {
                'doctor_id':doctor_id,
                'investigation_category':investigation_category,
                'investigation_name':investigation_name
            }

            labinvestigationSerializer = TbllabinvestigationsSerializer(data=investigation_data)
            if labinvestigationSerializer.is_valid():
                instance = labinvestigationSerializer.save()
                last_investigation_id = instance.investigation_id

                res = {
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': [{'last_investigation_id': last_investigation_id}],
                    'message_debug': debug if debug else []
                }
            else:
                res = {
                    'message_code': 2000,
                    'message_text': 'Validation Error',
                    'message_errors': labinvestigationSerializer.errors
                }


        except Tbllabinvestigations.DoesNotExist:
            res = {'message_code': 999, 'message_text': 'Tbllabinvestigations not found'}

        except Exception as e:
            res = {'message_code': 999, 'message_text': f'Error: {str(e)}'}

    return Response(res, status=status.HTTP_200_OK)

@api_view(['POST'])
def fi_update_labinvestigations(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
     
    investigation_id = request.data.get('investigation_id', '')
    doctor_id = request.data.get('doctor_id', '')
    investigation_category = request.data.get('investigation_category', '')
    investigation_name = request.data.get('investigation_name', '')

    # Validate appointment_id
    if not investigation_id:
        res = {'message_code': 999,'message_text': 'Investigation id is required'}
    elif not doctor_id:
        res = {'message_code': 999,'message_text': 'Doctor id is required'}
    elif not investigation_category:
        res = {'message_code': 999,'message_text': 'Investigation category is required'}
    elif not investigation_name:
        res = {'message_code': 999,'message_text': 'Investigation name is required'}
    else:

        try:
            if investigation_id:
                try:
                # Get MedicineInstructions instance
                    investigation_data = {
                            'doctor_id':doctor_id,
                            'investigation_category':investigation_category,
                            'investigation_name':investigation_name
                        }
                    lab_investigation = Tbllabinvestigations.objects.get(investigation_id=investigation_id)


                    serializer = TbllabinvestigationsSerializer(lab_investigation, data=investigation_data, partial=True)
                    if serializer.is_valid():
                        updated_data = serializer.validated_data  # Get the validated data after a successful update
                        serializer.save()

                        res = {
                                'message_code': 1000,
                                'message_text': 'Success',
                                'message_data': {'investigation_id': investigation_id},
                                'message_debug': debug if debug else []
                            }
                    else:
                            res = {
                                'message_code': 2000,
                                'message_text': 'Validation Error',
                                'message_errors': serializer.errors
                            }

                    
                except Tbllabinvestigations.DoesNotExist:
                    res = {'message_code': 999, 'message_text': 'Tbllabinvestigations not found'}

        except Exception as e:
            res = {'message_code': 999, 'message_text': f'Error: {str(e)}',
                   'message_data': [],
                   'message_debug': [] if debug == "" else [{'Debug': debug}]}
    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def fi_delete_labinvestigations(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    investigation_id = request.data.get('investigation_id', '')

    if not investigation_id:
        res = {'message_code': 999, 'message_text': 'investigation id is required.'}
    else:
        try:
                    investigation_data = {
                            'isdeleted':1
                        }
                    lab_investigation = Tbllabinvestigations.objects.get(investigation_id=investigation_id)


                    serializer = TbllabinvestigationsSerializer(lab_investigation, data=investigation_data, partial=True)
                    if serializer.is_valid():
                        updated_data = serializer.validated_data  # Get the validated data after a successful update
                        serializer.save()

                        res = {
                                'message_code': 1000,
                                'message_text': 'Success',
                                'message_data': {'investigation_id': investigation_id},
                                'message_debug': debug if debug else []
                            }
                    else:
                            res = {
                                'message_code': 2000,
                                'message_text': 'Validation Error',
                                'message_errors': serializer.errors
                            }
        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res, status=status.HTTP_200_OK)

####################################new apis#############################################
@api_view(['POST'])
def get_consultation_fee_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_fee_id = request.data.get('consultation_fee_id', None)

    if not consultation_fee_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation Fee ID is required.'}
    else:
        try:
            consultation_fee = ConsultationFee.objects.get(consultation_fee_id=consultation_fee_id, is_deleted=0)
            serializer = ConsultationFeeSerializer(consultation_fee)
            result = serializer.data

            response_data = {
                'message_code': 1000,
                'message_text': 'Consultation Fee details are fetched successfully',
                'message_data': result,
                'message_debug': debug
            }

        except ConsultationFee.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Consultation Fee not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_medical_service_fee_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    medical_service_fee_id = request.data.get('medical_service_fee_id', None)

    if not medical_service_fee_id:
        response_data = {'message_code': 999, 'message_text': 'Medical Service Fee ID is required.'}
    else:
        try:
            medical_service_fee = MedicalServicesFee.objects.get(medical_service_fee_id=medical_service_fee_id, is_deleted=0)
            serializer = MedicalServicesFeeSerializer(medical_service_fee)
            result = serializer.data

            response_data = {
                'message_code': 1000,
                'message_text': 'Medical Service Fee details are fetched successfully',
                'message_data': result,
                'message_debug': debug
            }

        except MedicalServicesFee.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Medical Service Fee not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_consultation_fee_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_fee_id = request.data.get('consultation_fee_id', None)

    if not consultation_fee_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation Fee ID is required in the request body.'}
    else:
        try:
            consultation_fee = ConsultationFee.objects.get(consultation_fee_id=consultation_fee_id, is_deleted=0)
            serializer = ConsultationFeeSerializer(consultation_fee, data=request.data, partial=True)

            if serializer.is_valid():
                updated_instance = serializer.save()
                updated_data = {}

                for field in serializer.fields:
                    if field in serializer.validated_data:
                        updated_data[field] = updated_instance.__getattribute__(field)

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Consultation Fee details are updated successfully',
                    'message_data': updated_data,
                    'message_debug': debug
                }
            else:
                response_data['message_text'] = 'Invalid data provided.'

        except ConsultationFee.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Consultation Fee not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_medical_service_fee_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    medical_service_fee_id = request.data.get('medical_service_fee_id', None)

    if not medical_service_fee_id:
        response_data = {'message_code': 999, 'message_text': 'Medical Service Fee ID is required in the request body.'}
    else:
        try:
            medical_service_fee = MedicalServicesFee.objects.get(medical_service_fee_id=medical_service_fee_id, is_deleted=0)
            serializer = MedicalServicesFeeSerializer(medical_service_fee, data=request.data, partial=True)

            if serializer.is_valid():
                updated_instance = serializer.save()
                updated_data = {}

                for field in serializer.fields:
                    if field in serializer.validated_data:
                        updated_data[field] = updated_instance.__getattribute__(field)

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Medical Service Fee details are updated successfully',
                    'message_data': updated_data,
                    'message_debug': debug
                }
            else:
                response_data['message_text'] = 'Invalid data provided.'

        except MedicalServicesFee.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Medical Service Fee not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_doctor_location_availability(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': {}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data
            doctor_id = data.get('doctor_id', None)
            availability_day = data.get('availability_day', None)

            if doctor_id is not None and availability_day is not None:
                queryset = Tbldoctorlocationavailability.objects.filter(doctor_id=doctor_id, availability_day=availability_day, isdeleted=0)
                serializer = DoctorLocationAvailabilitySerializer(queryset, many=True)

                if not serializer.data:
                    res['message_text'] = 'Doctor availability not found for the given parameters.'
                    return Response(res, status=status.HTTP_404_NOT_FOUND)

                res = {
                    'message_code': 1000,
                    'message_text': 'Success',
                    'message_data': serializer.data,
                    'message_debug': debug if debug else []
                }
                return Response(res, status=status.HTTP_200_OK)
            else:
                res['message_text'] = 'Doctor ID and availability day are required parameters.'
                return Response(res, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in get_doctor_location_availability. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def insert_doctor_leave(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    doctor_leave_data = request.data

    # Convert date strings to epoch timestamps
    doctor_leave_data['leave_date'] = convert_to_epoch(doctor_leave_data.get('leave_date'))
    doctor_leave_data['updated_date'] = convert_to_epoch(datetime.today().strftime('%Y-%m-%d'))
    # print(doctor_leave_data['updated_date'])

    doctor_leave_serializer = TbldoctorleaveSerializer(data=doctor_leave_data)

    if doctor_leave_serializer.is_valid():
        doctor_leave_instance = doctor_leave_serializer.save()
        response_data['message_code'] = 1000
        response_data['message_text'] = 'Data successfully saved!'
        response_data['message_data'] = {'doctor_leave_id': doctor_leave_instance.doctor_leave_id}
    else:
        errors = {
            'doctor_leave_errors': doctor_leave_serializer.errors,
        }
        response_data['message_text'] = 'Failed to save data. Please check the errors.'
        response_data['errors'] = errors

    return Response(response_data, status=status.HTTP_200_OK)

def convert_to_epoch(date_str):
    # Convert date string to epoch timestamp
    try:
        date_object = datetime.strptime(date_str, '%Y-%m-%d')
        epoch_timestamp = int(date_object.timestamp())
        return epoch_timestamp
    except ValueError:
        return None
    

####################Get Doctor Leave details by doctor id#############
@api_view(["POST"])
def get_doctor_leave_details(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    try:
        # Get doctor ID from request data
        doctor_id = request.data.get('doctor_id')

        # Get doctor leave details by doctor ID
        doctor_leave_objects = Tbldoctorleave.objects.filter(doctor_id=doctor_id)

        # Serialize the data
        doctor_leave_serializer = TbldoctorleaveSerializer(doctor_leave_objects, many=True)

        # Convert epoch values to date format
        for entry in doctor_leave_serializer.data:
            entry['leave_date'] = datetime.fromtimestamp(entry['leave_date']).strftime("%Y-%m-%d")
            entry['updated_date'] = datetime.fromtimestamp(entry['updated_date']).strftime("%Y-%m-%d")

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Doctor leave details retrieved successfully.'
        response_data['message_data'] = doctor_leave_serializer.data

    except Tbldoctorleave.DoesNotExist:
        response_data['message_text'] = 'Doctor leave details not found.'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_doctor_leave(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    try:
        # Extract data from the request body
        leave_date = request.data.get('leave_date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        order = request.data.get('order')

        # Convert leave date to epoch value
        leave_date_epoch = int(datetime.strptime(leave_date, "%Y-%m-%d").timestamp())

        # Get doctor leave objects for the given date
        doctor_leave_objects = Tbldoctorleave.objects.filter(leave_date=leave_date_epoch, order=order)

        if not doctor_leave_objects.exists():
            response_data['message_text'] = 'No doctor leave details found for the given date.'
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        # Update doctor leave details
        for doctor_leave in doctor_leave_objects:
            # You can update any specific fields here
            doctor_leave.start_time = start_time if start_time is not None else doctor_leave.start_time
            doctor_leave.end_time = end_time if end_time is not None else doctor_leave.end_time
            doctor_leave.updated_date = int(timezone.now().timestamp())

            # Save the updated object
            doctor_leave.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Doctor leave details updated successfully.'
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        response_data['message_text'] = str(e)
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(["POST"])
# def get_doctor_profileby_token(request):
#     debug = []
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Functional part is commented.',
#         'message_data': [],
#         'message_debug': debug
#     }

#     doctor_login_token = request.data.get('doctor_login_token', None)

#     if not doctor_login_token:
#         response_data = {'message_code': 999, 'message_text': 'Doctor login token is required.'}
#     else:
#         try:
#             doctor = Tbldoctors.objects.get(doctor_login_token=doctor_login_token)
#             serializer = DoctorSerializer(doctor)
#             result = serializer.data

#             response_data = {
#                 'message_code': 1000,
#                 'message_text': 'Doctor details are fetched successfully',
#                 'message_data': result,
#                 'message_debug': debug
#             }

#         except Tbldoctors.DoesNotExist:
#             response_data = {'message_code': 999, 'message_text': 'no doctor token match.', 'message_debug': debug}

#     return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_doctor_related_info(request):
    doctor_id = request.data.get('doctor_id', None)

    if not doctor_id:
        return Response({'message': 'Doctor ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve the last inserted doctor's related information
        doctor_location = Tbldoctorlocations.objects.filter(doctor_id=doctor_id).values('doctor_location_id').first()
        doctor_availability = Tbldoctorlocationavailability.objects.filter(doctor_id=doctor_id).values('doctor_location_availability_id').first()
        medical_service_fee = MedicalServicesFee.objects.filter(doctor_id=doctor_id).values('medical_service_fee_id').first()
        consultation_fee = ConsultationFee.objects.filter(doctor_id=doctor_id).values('consultation_fee_id').first()

        # Get the last inserted availability ID, consultation fee ID, and medical service fee ID
        doctor_location_id=doctor_location['doctor_location_id']
        last_availability_id = doctor_availability['doctor_location_availability_id']+20 if doctor_availability else None
        last_medical_service_fee_id = medical_service_fee['medical_service_fee_id']+2 if medical_service_fee else None
        last_consultation_fee_id = consultation_fee['consultation_fee_id']+2 if consultation_fee else None

        response_data = {
            'doctor_location_id':doctor_location_id,
            'last_availability_id': last_availability_id,
            'last_medical_service_fee_id': last_medical_service_fee_id,
            'last_consultation_fee_id': last_consultation_fee_id,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Tbldoctors.DoesNotExist:
        return Response({'message': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def get_doctor_location_bylocationtoken(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    

    location_token = request.data.get('location_token', '')
    
    if not location_token:
        res = {'message_code': 999, 'message_text': 'doctor location token is required.'}
    else:
        try:
            
            doctor_location = Tbldoctorlocations.objects.filter(
                Q(location_token=location_token,isdeleted=0)
            )

            # Serialize the data
            serializer = DoctorLocationSerializer(doctor_location, many=True)
            result = serializer.data
            # last_query = connection.queries[-1]['sql']
            # print(last_query)
            if result:
                res = {
                    'message_code': 1000,
                    'message_text': "Doctor location retrieved successfully.",
                    'message_data': result,
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "Doctor location not found.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res, status=status.HTTP_200_OK)

@api_view(["POST"])
def insert_user(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    user_data = request.data

    # Generate a unique 32-character token for user_login_token
    user_data['user_login_token'] = uuid.uuid4().hex


    user_serializer = TblUsersSerializer(data=user_data)

    if user_serializer.is_valid():
        user_instance = user_serializer.save()
        response_data['message_code'] = 1000
        response_data['message_text'] = 'User data successfully saved!'
        response_data['message_data'] = {'user_id': user_instance.user_id}
    else:
        errors = {
            'user_errors': user_serializer.errors,
        }
        response_data['message_text'] = 'Failed to save user data. Please check the errors.'
        response_data['errors'] = errors

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def get_all_users_by_location(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    location_id = request.data.get('location_id', None)

    if not location_id:
        response_data = {'message_code': 999, 'message_text': 'Location ID is required in the request body.'}
    else:
        try:
            users = tblUsers.objects.filter(location_id=location_id)
            if not users.exists():
                response_data = {'message_code': 999, 'message_text': 'No users found for the specified location ID.'}
            else:
                serializer = TblUsersSerializer(users, many=True)
                response_data = {
                    'message_code': 1000,
                    'message_text': 'Users retrieved successfully.',
                    'message_data': serializer.data
                }
        except Exception as e:
            response_data = {'message_code': 999, 'message_text': f'Failed to retrieve users: {str(e)}'}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_user_details(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    user_id = request.data.get('user_id', None)

    if not user_id:
        response_data = {'message_code': 999, 'message_text': 'User ID is required in the request body.'}
    else:
        try:
            user_instance = tblUsers.objects.get(user_id=user_id)
            if not user_instance:
                response_data = {'message_code': 999, 'message_text': 'User not found for the specified ID.'}
            else:
                serializer = TblUsersSerializer(instance=user_instance, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    response_data = {'message_code': 1000, 'message_text': 'User details updated successfully.'}
                else:
                    response_data = {'message_code': 999, 'message_text': 'Failed to update user details.', 'errors': serializer.errors}
        except tblUsers.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'User not found for the specified ID.'}
        except Exception as e:
            response_data = {'message_code': 999, 'message_text': f'Failed to update user details: {str(e)}'}

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(["POST"])
def get_doctor_profileby_token(request):
    doctor_login_token = request.data.get('doctor_login_token', None)

    if not doctor_login_token:
        return Response({'message_code': 999, 'message_text': 'Doctor login token is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Check if the token exists in Tbldoctors
        doctor = Tbldoctors.objects.get(doctor_login_token=doctor_login_token)
        serializer = DoctorSerializer(doctor)  # Serialize doctor instance
        serialized_data = serializer.data  # Get serialized data as JSON-compatible dictionary

        response_data = {
            'message_code': 1000,
            'message_text': 'Doctor',
            'message_data': serialized_data  # Include serialized doctor data in response
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Tbldoctors.DoesNotExist:
        try:
            # If the token is not found in Tbldoctors, check in tblUsers
            user = tblUsers.objects.get(user_login_token=doctor_login_token)
            serializer = TblUsersSerializer(user)  # Serialize user instance
            serialized_data = serializer.data  # Get serialized data as JSON-compatible dictionary

            if user.location_id:
                doctor_id = user.location_id.doctor_id
                # print(doctor_id.doctor_id)
                serialized_data['doctor_id'] = doctor_id.doctor_id
            else:
                doctor_id = None

            response_data = {
                'message_code': 1001,
                'message_text': f'{get_user_role_description(user.user_role)}',
                'message_data': serialized_data  # Include serialized user data in response
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except tblUsers.DoesNotExist:
            return Response({'message_code': 999, 'message_text': 'No matching token found.'}, status=status.HTTP_404_NOT_FOUND)

def get_user_role_description(role_id):
    # Custom function to map role ID to role description
    if role_id == 1:
        return 'Reception'
    elif role_id == 2:
        return 'Compounder'
    elif role_id == 3:
        return 'Accountant'
    else:
        return 'Unknown'
    
@api_view(["POST"])
def login_desktop(request):
    mobile_number = request.data.get('mobile_number', None)
    password = request.data.get('password', None)

    if not mobile_number or not password:
        return Response({'message_code': 999, 'message_text': 'Mobile number and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Check if the mobile number and password exist in Tbldoctors
        doctor = Tbldoctors.objects.get(doctor_mobileno=mobile_number, password=password)
        serializer = DoctorSerializer(doctor)  # Serialize doctor instance
        serialized_data = serializer.data  # Get serialized data as JSON-compatible dictionary

        response_data = {
            'message_code': 1000,
            'message_text': 'Doctor',
            'message_data': serialized_data  # Include serialized doctor data in response
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Tbldoctors.DoesNotExist:
        try:
            # If not found in Tbldoctors, check in tblUsers
            user = tblUsers.objects.get(user_mobileno=password)
            serializer = TblUsersSerializer(user)  # Serialize user instance
            serialized_data = serializer.data  # Get serialized data as JSON-compatible dictionary

            if user.location_id:
                doctor_id = user.location_id.doctor_id
                serialized_data['doctor_id'] = doctor_id.doctor_id
            else:
                doctor_id = None

            response_data = {
                'message_code': 1000,
                'message_text': f'{get_user_role_description(user.user_role)}',
                'message_data': serialized_data  # Include serialized user data in response
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except tblUsers.DoesNotExist:
            return Response({'message_code': 999, 'message_text': 'No matching mobile number and password found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def insert_prescription_settings(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    serializer = PrescriptionSettingsSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            serializer.save()
            response_data.update({
                'message_code': 1000,
                'message_text': 'Prescription settings inserted successfully.',
                'message_data': serializer.data
            })
        except Exception as e:
            response_data.update({
                'message_text': f'Failed to insert prescription settings: {str(e)}'
            })
    else:
        response_data.update({
            'message_text': 'Invalid data provided.'
        })

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_prescription_settings_by_doctor(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    doctor_id = request.data.get('doctor_id', None)
    if not doctor_id:
        response_data = {'message_code': 999, 'message_text': 'Doctor ID is required in the request body.'}
    else:
        try:
            prescription_settings = PrescriptionSettings.objects.filter(doctor_id=doctor_id).first()
            if not prescription_settings:
                response_data = {'message_code': 999, 'message_text': 'Prescription settings not found for the specified doctor.'}
            else:
                serializer = PrescriptionSettingsSerializer(prescription_settings)
                response_data = {
                    'message_code': 1000,
                    'message_text': 'Prescription settings retrieved successfully.',
                    'message_data': serializer.data
                }
        except Exception as e:
            response_data = {'message_code': 999, 'message_text': f'Failed to retrieve prescription settings: {str(e)}'}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_header_image(request):
    try:
        # Get the doctor ID from the request data
        doctor_id = request.data.get('doctor_id')
        if not doctor_id:
            return Response({'message_code': 999, 'message_text': 'Doctor ID is missing.', 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)

        # Get the PrescriptionSettings object associated with the given doctor_id
        prescription_settings = PrescriptionSettings.objects.filter(doctor_id=doctor_id).first()
        if not prescription_settings:
            return Response({'message_code': 999, 'message_text': 'Prescription settings not found for the given doctor ID.', 'message_data': {}}, status=status.HTTP_404_NOT_FOUND)

        # Get the new header image file from the request
        new_image_file = request.FILES.get('header_image')
        if new_image_file:
            # Determine the filename for the new image
            if prescription_settings.header_image:
                existing_image_filename = os.path.basename(prescription_settings.header_image.name)
                new_image_filename = existing_image_filename
            else:
                new_image_filename = new_image_file.name

            # Delete the old image file if it exists
            if prescription_settings.header_image:
                old_image_path = prescription_settings.header_image.path
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Update the header_image field with the new image file
            prescription_settings.header_image.save(new_image_filename, new_image_file)
            prescription_settings.save()

        response_data = {
            'message_code': 1000,
            'message_text': 'Header image updated successfully.',
            'message_data': {}
        }

    except Exception as e:
        response_data = {
            'message_code': 999,
            'message_text': f'Error updating header image. Error: {str(e)}',
            'message_data': {}
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_prescription_details(request):
    try:
        # Get the doctor ID from the request data
        doctor_id = request.data.get('doctor_id')
        if not doctor_id:
            return Response({'message_code': 999, 'message_text': 'Doctor ID is missing.', 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)

        # Get the PrescriptionSettings object associated with the given doctor_id
        prescription_settings = PrescriptionSettings.objects.filter(doctor_id=doctor_id).first()
        if not prescription_settings:
            return Response({'message_code': 999, 'message_text': 'Prescription settings not found for the given doctor ID.', 'message_data': {}}, status=status.HTTP_404_NOT_FOUND)

        # Use the serializer to update the fields in the PrescriptionSettings object
        serializer = PrescriptionSettingsSerializer(prescription_settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            response_data = {
                'message_code': 1000,
                'message_text': 'Prescription details updated successfully.',
                'message_data': serializer.data
            }
        else:
            response_data = {
                'message_code': 999,
                'message_text': 'Invalid data provided.',
                'message_data': serializer.errors
            }

    except Exception as e:
        response_data = {
            'message_code': 999,
            'message_text': f'Error updating prescription details. Error: {str(e)}',
            'message_data': {}
        }

    return Response(response_data, status=status.HTTP_200_OK)


##################For Admin Panel
# @api_view(['POST'])
# def fetch_doctors(request):
#     try:
#         # Filter doctors where isdeleted is 0
#         doctors = Tbldoctors.objects.filter(isdeleted=0)
        
#         # Serialize the data
#         serializer = DoctorSerializer(doctors, many=True)
#         doctors_data = serializer.data
        
#         # Convert created_on epoch value to human-readable date format
#         for doctor in doctors_data:
#             if 'createdon' in doctor and doctor['createdon'] is not None:
#                 doctor['created_on_formatted'] = datetime.fromtimestamp(doctor['createdon']).strftime('%d-%m-%Y')
#             else:
#                 doctor['created_on_formatted'] = None
        
#         # Prepare the response data
#         response_data = {
#             'message_code': 1000,
#             'message_text': 'Doctors fetched successfully.',
#             'message_data': doctors_data
#         }
#     except Exception as e:
#         response_data = {
#             'message_code': 999,
#             'message_text': f'Error fetching doctors. Error: {str(e)}',
#             'message_data': {}
#         }

#     return Response(response_data, status=status.HTTP_200_OK)
@api_view(['POST'])
def fetch_doctors(request):
    try:
        # Filter doctors where isdeleted is 0 and sort by doctor_id in descending order
        doctors = Tbldoctors.objects.filter(isdeleted=0).order_by('-doctor_id')
        
        # Serialize the data
        serializer = DoctorSerializer(doctors, many=True)
        doctors_data = serializer.data
        
        # Convert created_on epoch value to human-readable date format
        for doctor in doctors_data:
            if 'createdon' in doctor and doctor['createdon'] is not None:
                doctor['created_on_formatted'] = datetime.fromtimestamp(doctor['createdon']).strftime('%d-%m-%Y')
            else:
                doctor['created_on_formatted'] = None
        
        # Prepare the response data
        response_data = {
            'message_code': 1000,
            'message_text': 'Doctors fetched successfully.',
            'message_data': doctors_data
        }
    except Exception as e:
        response_data = {
            'message_code': 999,
            'message_text': f'Error fetching doctors. Error: {str(e)}',
            'message_data': {}
        }

    return Response(response_data, status=status.HTTP_200_OK)
 
from django.shortcuts import get_object_or_404
@api_view(['POST'])
def doctors_stats(request):
    try:
        # Get the doctor ID from the request data
        doctor_id = request.data.get('doctor_id')
        if not doctor_id:
            return Response({'message_code': 999, 'message_text': 'Doctor ID is missing.', 'message_data': {}}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Count consultations for the doctor
        consultations_count = Tblconsultations.objects.filter(doctor_id=doctor_id).count()

        # 2. Count patient-doctor links for the doctor
        patient_doctor_links_count = tblPatientDoctorLink.objects.filter(doctor_id=doctor_id).count()

        # 3. Count users associated with the location (indirectly with the doctor)
        location_id = get_object_or_404(Tbldoctorlocations, doctor_id=doctor_id).doctor_location_id
        # users_count = tblUsers.objects.filter(location_id=location_id).count()


        # Prepare response data
        response_data = {
            'consultations': consultations_count if consultations_count else 0,
            'patient_linked': patient_doctor_links_count if patient_doctor_links_count else 0,
            'location_id': location_id if location_id else 0,
        }

        return Response({'message_code': 1000, 'message_text': 'Doctor counters retrieved successfully.', 'message_data': response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message_code': 999, 'message_text': f'Error retrieving doctor counters. Error: {str(e)}', 'message_data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
from datetime import timedelta
@api_view(['POST'])
def fillter_doctors(request):
    try:
        city_id = request.data.get('city_id', None)
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)

        # Convert dates from string to datetime objects
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Filter doctors where isdeleted is 0
        doctors = Tbldoctors.objects.filter(isdeleted=0)

        if city_id:
            doctors = doctors.filter(doctor_cityid=city_id)
        
        if start_date and end_date:
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int((end_date + timedelta(days=1)).timestamp()) - 1
            doctors = doctors.filter(createdon__gte=start_timestamp, createdon__lte=end_timestamp)
        elif start_date:
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int((start_date + timedelta(days=1)).timestamp()) - 1
            doctors = doctors.filter(createdon__gte=start_timestamp, createdon__lte=end_timestamp)

        # Check if doctors are found
        if not doctors.exists():
            response_data = {
                'message_code': 1001,
                'message_text': 'No doctors found for the given filters.',
                'message_data': []
            }
            return Response(response_data, status=status.HTTP_200_OK)

        # Serialize the data
        serializer = DoctorSerializer(doctors, many=True)
        doctors_data = serializer.data

        # Convert created_on epoch value to human-readable date format
        for doctor in doctors_data:
            if 'createdon' in doctor and doctor['createdon'] is not None:
                doctor['created_on_formatted'] = datetime.fromtimestamp(doctor['createdon']).strftime('%d-%m-%Y')
            else:
                doctor['created_on_formatted'] = None

        # Prepare the response data
        response_data = {
            'message_code': 1000,
            'message_text': 'Doctors fetched successfully.',
            'message_data': doctors_data
        }
    except Exception as e:
        response_data = {
            'message_code': 999,
            'message_text': f'Error fetching doctors. Error: {str(e)}',
            'message_data': {}
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_nonleaved_dates(request):
    doctor_id = request.data.get('doctor_id', None)

    if not doctor_id:
        return Response({'error': 'Doctor Id is required'}, status=status.HTTP_400_BAD_REQUEST)

    # try:
    #     doctor_location = Tbldoctorlocations.objects.get(doctor_id=doctor_id)
    # except Tbldoctorlocations.DoesNotExist:
    #     return Response({'error': 'Invalid location token'}, status=status.HTTP_404_NOT_FOUND)

    #doctor_id = doctor_location.doctor_id

    # Calculate date range (current date to next 10 days)
    current_date = datetime.now().date()
    end_date = current_date + timedelta(days=10)

    # Fetch doctor leave records within the specified date range
    doctor_leaves = Tbldoctorleave.objects.filter(
        doctor_id=doctor_id,
        leave_date__gte=(datetime.now() - timedelta(days=1)).timestamp(),
        leave_date__lt=(datetime.now() + timedelta(days=10)).timestamp()
    )
    #print(doctor_leaves)
    # Prepare a set to track unique leave dates with non-zero start/end times
    valid_leave_dates = set()

    for leave in doctor_leaves:
        if leave.start_time != 0 and leave.end_time != 0:  # Only consider if start_time and end_time are non-zero
            leave_date = datetime.fromtimestamp(leave.leave_date).date()
            valid_leave_dates.add(leave_date.strftime('%d-%m-%Y'))  # Add formatted date string to the set.
    
    valid_leave_dates=list(valid_leave_dates)
    #print(valid_leave_dates)
    leave_details=[]
    for leave_date in valid_leave_dates:  
            # Construct leave detail entry
            leave_details.append(leave_date)

    # Generate list of all dates within the date range (including current date)
    all_dates = [current_date + timedelta(days=i) for i in range(10)]  # 11 days including current date

    # Prepare non-leave date details with structured format
    nonleaved_dates_details = []
    for date in all_dates:
        if date not in [datetime.fromtimestamp(leave.leave_date).date() for leave in doctor_leaves]:
            # Determine time suffix based on day of the week (Monday to Sunday)
            day_of_week = date.weekday() + 1  # Monday is 0, so add 1 to match your day numbering
            availability = Tbldoctorlocationavailability.objects.filter(doctor_id=doctor_id, availability_day=day_of_week).first()
            if availability and availability.availability_starttime != 0 and availability.availability_endtime != 0:
                    
                # Construct non-leave detail entry
                nonleaved_dates_details.append(date.strftime('%d-%m-%Y'))

    # Combine leave and non-leave date details into a single list
    script_options = leave_details + nonleaved_dates_details
    # Prepare response data with the desired structure
    response_data = {
        'message_code': 1000,
        'message_text': 'Non-leaved and leave details retrieved successfully.',
        'message_data': {
            'nonleaved_dates':script_options,
            'leave_details': list(valid_leave_dates)  # Convert set to list to maintain unique dates
        },
        'message_debug': ""
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_leave_or_availability(request):
    doctor_id = request.data.get('doctor_id', None)
    date_string = request.data.get('date', None)

    if not doctor_id or not date_string:
        return Response({'error': 'Doctor ID and date are required'}, status=status.HTTP_400_BAD_REQUEST)


    try:
        # Parse the provided date string into a datetime object
        date = datetime.strptime(date_string, "%d-%m-%Y").date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use dd-MM-YYYY'}, status=status.HTTP_400_BAD_REQUEST)

    # Convert the date to a Unix timestamp (epoch time)
    leave_timestamp = datetime.timestamp(datetime.combine(date, datetime.min.time()))

    # Check if there are doctor leaves for the specified date
    doctor_leaves = Tbldoctorleave.objects.filter(
        doctor_id=doctor_id,
        leave_date=leave_timestamp
    )

    if doctor_leaves.exists():
        # Doctor leave details found for the date
        leave_details = []
        for leave in doctor_leaves:
            if leave.start_time != 0 and leave.end_time != 0:
                # Determine time suffix based on order (1: AM, 2 or 3: PM)
                if leave.order == 1:
                    time_suffix = " AM"
                else:
                    time_suffix = " PM"

                start_time_str = f"{leave.start_time}{time_suffix}"
                end_time_str = f"{leave.end_time}{time_suffix}"

                leave_details.append(f"{start_time_str} to {end_time_str}")

        # Prepare response data with structured format
        response_data = {
            'message_code': 1000,
            'message_text': 'Response Retrieval Successfully.',
            'message_data': {
                'Slots': leave_details
            },
            'message_debug': []
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        # No doctor leaves found, check doctor location availability for the day of the week
        day_of_week = date.weekday() + 1  # Monday is 0, so add 1 to match your day numbering

        availabilities = Tbldoctorlocationavailability.objects.filter(
            doctor_id=doctor_id,
            availability_day=day_of_week
        )

        if availabilities.exists():
            availability_details = []
            for availability in availabilities:
                if availability.availability_starttime != 0 and availability.availability_endtime != 0:
                    # Determine time suffix based on order (1: AM, 2 or 3: PM)
                    if availability.availability_order == 1:
                        time_suffix = " AM"
                    else:
                        time_suffix = " PM"

                    start_time_str = f"{availability.availability_starttime}{time_suffix}"
                    end_time_str = f"{availability.availability_endtime}{time_suffix}"

                    availability_details.append(f"{start_time_str} to {end_time_str}")

            # Prepare response data with structured format
            response_data = {
                'message_code': 1000,
                'message_text': 'Response Retrieval Successfully.',
                'message_data': {
                    'Slots': availability_details
                },
                'message_debug': []
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'No availability information found for the date'}, status=status.HTTP_404_NOT_FOUND)



####################EmergencyGroupDoctor#####################
@api_view(["POST"])
def insert_emergency_group_doctor(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': []
    }
    
    try:
        doctor_id = request.data.get('doctor_id')
        doctor_name = request.data.get('doctor_name')
        doctor_mobileno = request.data.get('doctor_mobileno')

        # Validate required fields
        if not doctor_id or not doctor_name or not doctor_mobileno:
            response_data['message_text'] = 'Doctor ID, name, and mobile number are required.'
            return Response(response_data, status=status.HTTP_200_OK)
        
        # Check if doctor_id and doctor_mobileno combination already exists
        if EmergencyGroupDoctors.objects.filter(doctor_id=doctor_id, doctor_mobileno=doctor_mobileno,is_deleted=0).exists():
            response_data['message_code'] = 1004
            response_data['message_text'] = 'This doctor id  and mobile number record is already present.'
            return Response(response_data, status=status.HTTP_200_OK)
        
        # Prepare data for serialization
        data = {
            "doctor_id": doctor_id,
            "doctor_name": doctor_name,
            "doctor_mobileno": doctor_mobileno,
        }

        # Serialize and save the data
        serializer = EmergencyGroupDoctorsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Emergency group doctor added successfully.'
            response_data['message_data'] = serializer.data
        else:
            response_data['message_text'] = 'Invalid data provided.'
            response_data['message_data'] = serializer.errors
    
    except Exception as e:
        response_data['message_text'] = str(e)
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_emergency_group_doctors(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': []
    }

    try:
        doctor_id = request.data.get('doctor_id')
        emergency_groupdoctor_id = request.data.get('emergency_groupdoctor_id')

        # Validate that at least one parameter is provided
        if not (doctor_id or emergency_groupdoctor_id):
            response_data['message_text'] = 'Provide doctor_id or emergency_groupdoctor_id.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Query emergency group doctors using flexible filtering
        emergency_group_doctors = EmergencyGroupDoctors.objects.filter(
            Q(doctor_id=doctor_id) | Q(emergency_groupdoctor_id=emergency_groupdoctor_id),
            is_deleted=0
        )

        if not emergency_group_doctors.exists():
            response_data['message_code'] = 1001
            response_data['message_text'] = 'No records found.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Serialize and return the results
        serializer = EmergencyGroupDoctorsSerializer(emergency_group_doctors, many=True)
        response_data['message_code'] = 1000
        response_data['message_text'] = 'Records fetched successfully.'
        response_data['message_data'] = serializer.data

    except Exception as e:
        response_data['message_text'] = str(e)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_emergency_group_doctor(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': None
    }

    try:
        emergency_groupdoctor_id = request.data.get('emergency_groupdoctor_id')
        doctor_name = request.data.get('doctor_name')
        doctor_mobileno = request.data.get('doctor_mobileno')

        # Validate that emergency_groupdoctor_id is provided
        if not emergency_groupdoctor_id:
            response_data['message_text'] = 'Emergency Group Doctor ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the existing record
        try:
            emergency_doctor = EmergencyGroupDoctors.objects.get(
                emergency_groupdoctor_id=emergency_groupdoctor_id,
                is_deleted=0  # Ensure it's not deleted
            )
        except EmergencyGroupDoctors.DoesNotExist:
            response_data['message_code'] = 1001
            response_data['message_text'] = 'No record found for the given ID.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Check if the provided mobile number is already linked to the same doctor_id
        if doctor_mobileno:
            existing_record = EmergencyGroupDoctors.objects.filter(
                doctor_id=emergency_doctor.doctor_id,
                doctor_mobileno=doctor_mobileno,
                is_deleted=0
            ).exclude(emergency_groupdoctor_id=emergency_groupdoctor_id).first()

            if existing_record:
                response_data['message_code'] = 1002
                response_data['message_text'] = 'This mobile number is already linked to the same doctor.'
                return Response(response_data, status=status.HTTP_200_OK)

        # Update only provided fields
        if doctor_name:
            emergency_doctor.doctor_name = doctor_name
        if doctor_mobileno:
            emergency_doctor.doctor_mobileno = doctor_mobileno

        # Save changes
        emergency_doctor.save()

        # Serialize updated data
        serializer = EmergencyGroupDoctorsSerializer(emergency_doctor)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Record updated successfully.'
        response_data['message_data'] = serializer.data  # Return updated record

    except Exception as e:
        response_data['message_text'] = str(e)

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["POST"])
def delete_emergency_group_doctor(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': None
    }

    try:
        emergency_groupdoctor_id = request.data.get('emergency_groupdoctor_id')
        deleted_by = request.data.get('deleted_by')  # Optional: ID of user performing the delete
        deleted_reason = request.data.get('deleted_reason', '')

        # Validate required fields
        if not emergency_groupdoctor_id:
            response_data['message_text'] = 'Emergency Group Doctor ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch record
        try:
            emergency_doctor = EmergencyGroupDoctors.objects.get(
                emergency_groupdoctor_id=emergency_groupdoctor_id,
                is_deleted=0  # Ensure it's not already deleted
            )
        except EmergencyGroupDoctors.DoesNotExist:
            response_data['message_code'] = 1001
            response_data['message_text'] = 'No record found for the given ID.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Perform soft delete
        emergency_doctor.is_deleted = 1
        emergency_doctor.deleted_on = datetime.now()
        emergency_doctor.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Record deleted successfully.'
        response_data['message_data'] = {
            'emergency_groupdoctor_id': emergency_doctor.emergency_groupdoctor_id,
            'deleted_on': emergency_doctor.deleted_on,
            'deleted_by': emergency_doctor.deleted_by,
            'deleted_reason': emergency_doctor.deleted_reason
        }

    except Exception as e:
        response_data['message_text'] = str(e)

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(["POST"])
# def insert_emergency_support_message(request):
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Error occurred.',
#         'message_data': []
#     }

#     try:
#         doctor_id = request.data.get("doctor_id")
#         appointment_id = request.data.get("appointment_id")

#         if not doctor_id or not appointment_id:
#             response_data['message_text'] = "doctor_id and appointment_id are required."
#             return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

#         # Check if the doctor has emergency group doctors
#         emergency_doctors = EmergencyGroupDoctors.objects.filter(
#             doctor_id=doctor_id, is_deleted=0
#         )

#         if not emergency_doctors.exists():
#             response_data['message_text'] = "Doctor has not added any emergency member."
#             return Response(response_data, status=status.HTTP_200_OK)

#         # Fetch the appointment details
#         appointment = Tbldoctorappointments.objects.filter(appointment_id=appointment_id).first()
#         if not appointment:
#             response_data['message_text'] = "Appointment not found."
#             return Response(response_data, status=status.HTTP_200_OK)

#         # Fetch the patient ID from patient vitals
#         patient_vital = Tblpatientvitals.objects.filter(appointment_id=appointment_id).first()
#         patient_id = patient_vital.patient_id.patient_id if patient_vital else None

#         # Get the patient name from appointment
#         patient_name = appointment.appointment_name

#         # Get doctor details
#         doctor = Tbldoctors.objects.filter(doctor_id=doctor_id).first()
#         if not doctor:
#             response_data['message_text'] = "Doctor not found."
#             return Response(response_data, status=status.HTTP_200_OK)

#         doctor_name = f"{doctor.doctor_firstname} {doctor.doctor_lastname}"
#         doctor_mobile = doctor.doctor_mobileno

#         created_messages = []

#         # Insert emergency support messages for each emergency doctor
#         for emergency_doctor in emergency_doctors:
#             message_body = (
#                 f"Hi {emergency_doctor.doctor_name}, the patient named {patient_name} "
#                 f"requires urgent support. Please contact Dr. {doctor_name} at {doctor_mobile}."
#             )

#             emergency_message = EmergencySupportMessage.objects.create(
#                 doctor_id=doctor,
#                 target_doctor=emergency_doctor,
#                 target_doctor_name=emergency_doctor.doctor_name,
#                 target_doctor_mobileno=emergency_doctor.doctor_mobileno,
#                 send_message=message_body,
#                 send_time= datetime.now(),
#                 patient_id=patient_id,
#                 appointment_id=appointment_id,
#                 patient_name=patient_name
#             )

#             created_messages.append({
#                 "emergency_supportmessage_id": emergency_message.emergency_supportmessage_id,
#                 "message": message_body
#             })

#         response_data['message_code'] = 1000
#         response_data['message_text'] = "Emergency messages sent successfully."
#         response_data['message_data'] = created_messages

#     except Exception as e:
#         response_data['message_text'] = str(e)

#     return Response(response_data, status=status.HTTP_200_OK)

@api_view(["POST"])
def insert_emergency_support_message(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': []
    }

    try:
        doctor_id = request.data.get("doctor_id")
        appointment_id = request.data.get("appointment_id")

        if not doctor_id or not appointment_id:
            response_data['message_text'] = "doctor_id and appointment_id are required."
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Check if an emergency message already exists for this appointment
        last_emergency_message = EmergencySupportMessage.objects.filter(
            appointment_id=appointment_id
        ).order_by("-send_time").first()  # Get the latest record

        if last_emergency_message:
            IST_OFFSET = timedelta(hours=5, minutes=30)  # IST is UTC +5:30
            send_time_ist = last_emergency_message.send_time + IST_OFFSET  # Convert to IST

            time_difference = timezone.now() - last_emergency_message.send_time  # Use timezone-aware now()
            if time_difference.total_seconds() < 18000:  # Less than 5 hours (5 * 60 * 60 = 18000 seconds)
                wait_time_hours = 5 - (time_difference.total_seconds() // 3600)
                response_data['message_text'] = (
                    f"You have already sent a message at {send_time_ist.strftime('%d-%m-%Y %I:%M %p')}. "
                    f"Please wait for {int(wait_time_hours)} more hours before sending another one."
                )
                return Response(response_data, status=status.HTTP_200_OK)

        # Check if the doctor has emergency group doctors
        emergency_doctors = EmergencyGroupDoctors.objects.filter(
            doctor_id=doctor_id, is_deleted=0
        )

        if not emergency_doctors.exists():
            response_data['message_text'] = "Doctor has not added any emergency member."
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the appointment details
        appointment = Tbldoctorappointments.objects.filter(appointment_id=appointment_id).first()
        if not appointment:
            response_data['message_text'] = "Appointment not found."
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the patient ID from patient vitals
        patient_vital = Tblpatientvitals.objects.filter(appointment_id=appointment_id).first()
        patient_id = patient_vital.patient_id.patient_id if patient_vital else None

        # Get the patient name from appointment
        patient_name = appointment.appointment_name

        # Get doctor details
        doctor = Tbldoctors.objects.filter(doctor_id=doctor_id).first()
        if not doctor:
            response_data['message_text'] = "Doctor not found."
            return Response(response_data, status=status.HTTP_200_OK)

        doctor_name = f"{doctor.doctor_firstname} {doctor.doctor_lastname}"
        doctor_mobile = doctor.doctor_mobileno

        created_messages = []

        # Insert emergency support messages for each emergency doctor
        for emergency_doctor in emergency_doctors:
            message_body = (
                f"Hi {emergency_doctor.doctor_name}, the patient named {patient_name} "
                f"requires urgent support. Please contact Dr. {doctor_name} at {doctor_mobile}."
            )

            emergency_message = EmergencySupportMessage.objects.create(
                doctor_id=doctor,
                target_doctor=emergency_doctor,
                target_doctor_name=emergency_doctor.doctor_name,
                target_doctor_mobileno=emergency_doctor.doctor_mobileno,
                send_message=message_body,
                send_time=timezone.now(),  # Use timezone-aware now()
                patient_id=patient_id,
                appointment_id=appointment_id,
                patient_name=patient_name
            )

            created_messages.append({
                "emergency_supportmessage_id": emergency_message.emergency_supportmessage_id,
                "message": message_body
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = "Emergency messages sent successfully."
        response_data['message_data'] = created_messages

    except Exception as e:
        response_data['message_text'] = str(e)

    return Response(response_data, status=status.HTTP_200_OK)