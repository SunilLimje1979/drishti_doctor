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
        request.data['location_qr_url'] = 'http://13.233.211.102/boat_api/bot/?id='+str(random_string)
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




