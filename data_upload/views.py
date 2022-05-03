
from uwa.settings import js
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import *
from.models import *
import pandas as pd
import re
from rest_framework.views import APIView
from rest_framework_tracking.mixins import LoggingMixin
import re
from datetime import datetime
from django.db.models import Q
from cerberus import Validator
import re


class CsvUpload(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)

	serializer_class = bothserializer
	def post(self,request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		data =serializer.data
		dic={v["upload_identifier"]: v for v in data['files']}
		res = list(dic.keys())
		u=None
		for data in res:
			u=data
		msg=js['csv_file_uploaded_successfully']
		return Response({'status':True,'message':msg,'upload_identifier':u}, status=status.HTTP_200_OK)



				
class ColumnHeaderMatching(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = ColumnHeaderMatchingSerializer
	def post(self, request):
		request_data = request.data  
		serializer = self.serializer_class(data=request_data)
		serializer.is_valid(raise_exception=True)
		get_file_instance=get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type=request_data['csv_type'])
		csvreader = pd.read_csv(get_file_instance.csv_file,encoding='ISO-8859-1')
		if csvreader.empty :
			raise serializers.ValidationError(code='Blank_csv_file')
	
		file_columns=[]
		for data in csvreader.columns:
			file_columns.append(data)
		headers=None
		if CsvFileHeaders.objects.filter(csv_file_type=request_data['csv_type']).exists():
			file_headers=get_object_or_404(CsvFileHeaders,csv_file_type=request_data['csv_type'])

			headers=eval(file_headers.csv_file_headers)
			if 'Deployment MetaData' == request_data['csv_type']:
				if len(headers) < 30: #maximum 61 columns
					raise serializers.ValidationError(code='less_columns')
			elif 'Device MetaData' == request_data['csv_type']:
				if len(headers) < 20:#maximum 50 columns
					raise serializers.ValidationError(code='less_columns')
			elif 'Input Data' == request_data['csv_type']:
				if len(headers) < 10:#maximum 19 columns
					raise serializers.ValidationError(code='less_columns')
		# for data in CsvFileData.objects.filter(upload_identifier=request_data['upload_identifier']):

		# 	instance=get_object_or_404(CsvFileData,id=data.id)
			# imported the requests library
		import requests
			
		r = requests.get(get_file_instance.csv_file.url)
		with open("media/"+str(get_file_instance.csv_file),'wb') as f:
			f.write(r.content)
		return Response({'status':True,'Column_from_Csv':file_columns,'Matching_form_field':headers},status=status.HTTP_200_OK,)


#=================================Validation Rules Start==============================================================================

to_bool = lambda v: v.lower() in ('')
to_date = lambda s: datetime.strptime(s, '%d-%m-%Y %H:%M')
decimal_type = cerberus.TypeDefinition('decimal', (Decimal,), ())
Validator.types_mapping['decimal'] = decimal_type


Schema={}
DevicementMetadataSchema={}
InputDataSchema={}




def is_integer(n):
			try:
				float(n)
			except ValueError:
				return False
			else:
				return float(n).is_integer()
def is_float(n):
			try:
				float(n)
				return True
			except ValueError:
				return False

import re

def isdigit(string):
    return bool(re.match(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)', string))

def isAlphaNumericStr(text):
   if(re.match("^[a-zA-Z0-9]*$", text) != None):
     return True
   return False

def boolean(field, value, error):
	if value == None:
		error(field, f"Field '{field}' expected boolean but got '{value}'")
	else:
		if value.lower() != 'no' and value.lower() != 'yes' and value.lower() != 'y' and value.lower() != 'n':
			error(field, f"Field '{field}' expected boolean but got '{value}'")

def boolean_for_null(field, value, error):
	if value == None:
		pass
	else:
		if value.lower() != 'no' and value.lower() != 'yes' and value.lower() != 'y' and value.lower() != 'n':
			error(field, f"Field '{field}' expected boolean but got '{value}'")

def decimal(field, value, error):
	if value == None:
		error(field, f"Field '{field}' expected decimal but got '{value}'")
	else:
		if not isdigit(value):
			error(field, f"Field '{field}' expected decimal but got '{value}'")
		# if value.isnumeric():
			
		# 	if not value.isdecimal():
		# 		error(field, f"Field '{field}' expected decimal but got '{value}'")
		# elif value.lstrip("-").isdigit():
		# 	if not value.lstrip("-").isdecimal():
		# 		error(field, f"Field '{field}' expected decimal but got '{value}'")
		# else:
		# 	error(field, f"Field '{field}' expected decimal but got '{value}'")
				# value=float(value)
		# if not isinstance(value, float):
		# print(value)
		# if not isinstance(value, float):
		# 		print(type(value),value)
		# 		error(field, f"Field '{field}' expected decimal but got '{value}'")

def decimal_for_null(field, value, error):
	if value == None:
		pass
	else:
		if not isdigit(value):
			error(field, f"Field '{field}' expected decimal but got '{value}'")	
		# if value.isnumeric():
		# 	print('decimal',value)
		# 	if not value.isdecimal():
		# 		error(field, f"Field '{field}' expected decimal but got '{value}'")
		# elif value.lstrip("-").isdigit():
		# 	if not value.lstrip("-").isdecimal():
		# 		error(field, f"Field '{field}' expected decimal but got '{value}'")
		# else:
		# 	error(field, f"Field '{field}' expected decimal but got '{value}'")
				# value=float(value)
		# if not isinstance(value, float):
		# print(value)
		# if not isinstance(value, float):
		# 		print(type(value),value)
		# 		error(field, f"Field '{field}' expected decimal but got '{value}'")

def string(field, value, error):
	if value == None:
		error(field, f"Field '{field}' expected string but got '{value}'")
	else:
		if not isinstance(value, str):
			error(field, f"Field '{field}' expected string but got '{value}'")
		elif field == 'argosFilderMethod':
			if value.lower() != 'least squares' and value.lower() != 'kalman' :
				error(field, f"Field '{field}' expected string(e.g least squares ,kalman) but got '{value}'")
		elif field == 'organismSex':
			if value.lower() != 'm' and value.lower() != 'f' and value.lower() != 'u':
				error(field, f"Field '{field}' expected string(e.g M,F,U) but got '{value}'")
		# elif field == 'license':
		# 	if not value in list(x.name for x in License.objects.all()):
		# 		error(field, f"Field '{field}' expected string(e.g'{list(x.name for x in License.objects.all())}') but got '{value}'")
		elif field == 'trackingDevice':
			if value.lower() != 'argos' and value.lower() != 'gls' and value.lower() != 'gps' and value.lower() != 'fastloc-gps' and value.lower() != 'acoustic':
				error(field, f"Field '{field}' expected string(e.g Argos, GLS, GPS, Fastloc-GPS, acoustic) but got '{value}'")

def string_for_null(field, value, error):
	if value == None:
		pass
	else:
		if not isinstance(value, str):
			error(field, f"Field '{field}' expected string but got '{value}'")
		elif field == 'deploymentEndType':
			if value.lower() != 'removal' and value.lower() != 'equipment failure' and value.lower() != 'fall off':
				error(field, f"Field '{field}' expected string(e.g removal,equipment failure ,fall off) but got '{value}'")
		elif field == 'organismAgeReproductiveClass':
			if value.lower() != 'adu' and value.lower() != 'sub' and value.lower() != 'juv' and value.lower() != 'new' and value.lower() != 'unk':
				error(field, f"Field '{field}' expected string(e.g adu, sub, juv, new, unk) but got '{value}'")
		elif field == 'verticalSensorUnitsReported':
			if value.lower() != 'meters':
				error(field, f"Field '{field}' expected string(e.g meters) but got '{value}'")
		elif field == 'argosLC':
			if value != 'Z' and value != 'B' and value != 'A' and value != '0' and value != '1' and value != '2' and value != '3' and value != 'G' and value != '-1' and value != '-2' and value != '-9999/-9/-99/-999' and value != 'LCA'  and value != 'LCB'  and value != 'LCZ'  and value != 'LCG' :
				error(field, f"Field '{field}' expected string(e.g Z, B, A, 0, 1, 2, 3, G,-1,-2,-9999/-9/-99/-999) but got '{value}'")
		




def integer(field, value, error):
	
	if value == None:
		error(field, f"Field '{field}' expected integer but got '{value}'")
	else:
		if value.isnumeric():
			value=int(value)
		if not isinstance(value, int):
			error(field, f"Field '{field}' expected integer but got '{value}'")

def integer_for_null(field, value, error):
	
	if value == None:
		pass
	else:
		if value.isnumeric():
			value=int(value)
		# else:
		# 	error(field, f"Field '{field}' expected integer but got '{value}'")
		if not isinstance(value, int):
			error(field, f"Field '{field}' expected integer but got '{value}'")
		elif 'gpsSatelliteCount' == field:
			if value >= 99 or value <=1 :
			 	error(field, f"Field '{field}' expected integer between 0-99 but got '{value}'")

def isfloat(field, value, error):
	if value == None:
		error(field, f"Field '{field}' expected float but got '{value}'")
	else:
		if isdigit(value):
			if field == 'temperatureGLS':
					if (float(value) >= -30 or float(value) <= 999):
						error(field, f"Field '{field}' expected float value between -30 to 999 but got '{value}'")
			elif re.match(r'^-?\d+(?:\.\d+)$', value) is None :
				error(field, f"Field '{field}' expected float but got '{value}'")
		else:
			error(field, f"Field '{field}' expected float but got '{value}'")

def float_for_null(field, value, error):
	if value == None:
		pass
	else:
		if isdigit(value):
			if field == 'temperatureGLS':
					if (float(value) <= -30 or float(value) >= 999):
						error(field, f"Field '{field}' expected float value between -30 to 999 but got '{value}'")
			elif field == 'residualsGPS(rapid acquisition GPS)' :
				if float(value) <= 0 or float(value) >= 999999 :
						error(field, f"Field '{field}' expected float value between 0 to 999999 but got '{value}'")
			elif field == 'depthGLS' :
				if float(value) <= 0 or float(value) >= 4000 :
						error(field, f"Field '{field}' expected float value between 0 to 4000 but got '{value}'")
			elif re.match(r'^-?\d+(?:\.\d+)$', value) is None :
				error(field, f"Field '{field}' expected float but got '{value}'")
		else:
			error(field, f"Field '{field}' expected float but got '{value}'")

def isalphnumric(field, value, error):
	if value == None:
		error(field, f"Field '{field}' expected Alphanumeric but got '{value}'")
	
	else:
		if not value.isalnum() or value.isalpha() or value.isdigit():
			error(field, f"Field '{field}' expected Alphanumeric but got '{value}'")


def isalphnumric_for_null(field, value, error):

	if value == None:
		pass
	else:
		if not value.isalnum() or value.isalpha() or value.isdigit():
			error(field, f"Field '{field}' expected Alphanumeric but got '{value}'")
#=================================Validation Rules End==============================================================================


DeploymentMetadataSchema={	
	'deploymentID':{'check_with':isalphnumric,'nullable': True},#this field is required
	'instrumentID':{'check_with':isalphnumric,'nullable': True},#this field is required
	'ptt': {'check_with':integer,'nullable': True},#this field is required,
	'transmissionSettings':{'check_with':integer_for_null, 'nullable': True,'min':999,'max':9999,},
	'transmissionMode':{'check_with':integer_for_null, 'nullable': True,'min': 999},
	'dutyCycle':{'check_with':string_for_null, 'nullable': True},
	'instrumentSettings': {'check_with':string_for_null, 'nullable': True},
	'deploymentDateTime':{'nullable': True,'coerce': to_date},#this field is required,
	'deploymentLatitude': {'check_with':decimal,'nullable': True},#this field is required,
	'deploymentLongitude': {'check_with':decimal,'nullable': True},#this field is required,
	'deploymentEndType':{'check_with':string_for_null, 'nullable': True,},
	'detachmentDateTime':{ 'nullable': True,'coerce': to_date},
	'detachmentDetails':{'check_with':string_for_null, 'nullable': True},
	'detachmentLatitude':{'check_with':decimal, 'nullable': True},
	'detachmentLongitude':{'check_with':decimal, 'nullable': True},
	'trackStartTime':{'nullable': True,'coerce': to_date},#this field is required,
	'trackStartLatitude':{'check_with':decimal,'nullable': True},#this field is required,
	'trackStartLongitude':{'check_with':decimal,'nullable': True},#this field is required ,
	'trackEndTime': {'nullable': True,'coerce': to_date},#this field is required,
	'trackEndLatitude': {'check_with':decimal,'nullable': True},#this field is required,
	'trackEndLongitude': {'check_with':decimal,'nullable': True},#this field is required,
	'sunElevationAngle':{'check_with':isfloat,'nullable': True,'min':0,'max':90},#this field is required,
	'argosFilderMethod': {'check_with':string,'nullable': True},#this field is required,
	'organismID':{'check_with':string,'nullable': True},#this field is required
	'scientificName':{'check_with':string,'nullable': True},#this field is required
	'scientificNameSource':{'check_with':string_for_null, 'nullable': True},
	'commonName':{'check_with':string,'nullable': True},#this field is required
	'organismSex':{'check_with':string,'nullable': True},#this field is required
	'organismWeightAtDeployment':{'check_with':float_for_null, 'nullable': True,'min':0,'max': 9999999},
	'organismWeightRemeasurement': {'check_with':float_for_null, 'nullable': True,'min':0,'max': 9999999},
	'organismWeightRemeasurementTime': { 'nullable': True,'coerce': to_date},
	'organismSize':{'check_with':float_for_null, 'nullable': True,'min':0,'max':99},
	'organismSizeMeasurementType':{'check_with':string_for_null, 'nullable': True},
	'organismSizeMeasurementDescription':{'check_with':string_for_null, 'nullable': True},
	'organismSizeMeasurementTime':{ 'nullable': True,'coerce': to_date},
	'organismAgeReproductiveClass':{'check_with':string_for_null, 'nullable': True},
	'trappingMethodDetails':{'check_with':string_for_null, 'nullable': True},
	'attachmentMethod':{'check_with':string, 'nullable': True},
	'environmentalCalibrationsDone':{'check_with':string_for_null, 'nullable': True},
	'environmentalQcDone': {'check_with': boolean,'nullable': True,},#this field is required
	'environmentalQcProblemsFound':{'check_with': boolean,'nullable': True,},#this field is required
	'environmentalQcNotes':{'check_with':string,'nullable': True},#this field is required,
	'physiologicalCalibrationsDone':{'check_with':string_for_null, 'nullable': True},
	'physiologicalQcDone':{'check_with': boolean,'nullable': True,},#this field is required,
	'physiologicalQcProblemsFound':{'check_with': boolean,'nullable': True,},#this field is required,
	'physiologicalQcNotes':{'check_with':string,'nullable': True},#this field is required
	'accelerometryPositionOfAccelerometerOnOrganism':{'check_with':string_for_null, 'nullable': True},
	'accelerometryOrientationOfAccelerometerOnOrganism':{'check_with':string_for_null, 'nullable': True},
	'accelerometryCalibrationsDone':{'check_with':string_for_null, 'nullable': True},
	'accelerometryQcDone': {'check_with': boolean_for_null,'nullable': True,},
	'accelerometryQcProblemsFound': {'check_with': boolean_for_null, 'nullable': True,},
	'accelerometryQcNotes':{'check_with':string_for_null, 'nullable': True},
	'ownerName':{'check_with':string,'nullable': True},#this field is required
	'ownerEmailContact':{'check_with':string,'nullable': True},#this field is required
	'ownerInstitutionalContact':{'check_with':string,'nullable': True},#this field is required
	'ownerPhoneContact':{'check_with':string,'nullable': True},#this field is required
	'license':{'check_with':string,'nullable': True},#this field is required
	'otherRelevantIdentifiers': {'check_with':string_for_null, 'nullable': True},
	'otherDataTypesAssociatedWithDeployment': {'check_with':string_for_null, 'nullable': True},
	'references': {'check_with':string_for_null, 'nullable': True},
	'citation': {'check_with':string_for_null, 'nullable': True},

}


DevicementMetadataSchema={	
	'instrumentID':{'check_with':isalphnumric,'nullable': True},#this field is required
	'instrumentType':{'check_with':string,'nullable': True},#this field is required
	'instrumentModel':{'check_with':string_for_null, 'nullable': True},
	'instrumentManufacturer':{'check_with':string_for_null, 'nullable': True},
	'instrumentSerialNumber':{'check_with':string_for_null, 'nullable': True},
	'trackingDevice':{'check_with':string,'nullable': True},#this field is required
	'horizontalSensorUplinkInterval':{'check_with':integer_for_null, 'nullable': True,'min':0,'max':9999999},
	'horizontalSensorUplinkIntervalUnits':{'check_with':string_for_null, 'nullable': True},
	'verticalSensorUnitsReported':{'check_with':string_for_null, 'nullable': True},
	'resolution':{'check_with':float_for_null, 'nullable': True},
	'verticalLowerSensorDetectionLimit':{'check_with':integer_for_null, 'nullable': True},
	'verticalUpperSensorDetectionLimit':{'check_with':integer_for_null, 'nullable': True},
	'verticalSensorPrecision':{'check_with':string_for_null, 'nullable': True},
	'verticalSensorSamplingFrequency':{'check_with':integer_for_null, 'nullable': True},
	'verticalSensorDutyCycling':{'check_with':integer_for_null, 'nullable': True},
	'verticalSensorCalibrationDate':{ 'nullable': True,'coerce': to_date},
	'verticalSensorCalibrationDetails':{'check_with':string_for_null, 'nullable': True},
	'environmentalSensorType':{'check_with':string_for_null, 'nullable': True} ,
	'environmentalSensorManufacturer':{'check_with':string_for_null, 'nullable': True},
	'environmentalSensorModel':{'check_with':string_for_null, 'nullable': True},
	'environmentalSensorUnitsReported':{'check_with':string_for_null, 'nullable': True},
	'environmentalLowerSensorDetectionLimit':{'check_with':string_for_null, 'nullable': True},
	'environmentalUpperSensorDetectionLimit':{'check_with':string_for_null, 'nullable': True},
	'environmentalSensorPrecision':{'check_with':string_for_null, 'nullable': True},
	'environmentalSensorSamplingFrequency':{'check_with':string_for_null, 'nullable': True},
	'environmentalSensorDutyCycling':{'check_with':string_for_null, 'nullable': True},
	'environmentalSensorCalibrationDate':{ 'nullable': True,'coerce': to_date},
	'environmentalSensorCalibrationDetails':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorType':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorManufacturer':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorModel':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorUnitsReported':{'check_with':string_for_null, 'nullable': True},
	'physiologicalLowerSensorDetectionLimit':{'check_with':string_for_null, 'nullable': True},
	'physiologicalUpperSensorDetectionLimit':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorPrecision':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorSamplingFrequency':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorDutyCycling':{'check_with':string_for_null, 'nullable': True},
	'physiologicalSensorCalibrationDate':{ 'nullable': True,'coerce': to_date},
	'physiologicalSensorCalibrationDetails':{'check_with':string_for_null, 'nullable': True},
	'accelerometrySensorManufacturer':{'check_with':string_for_null, 'nullable': True},
	'accelerometrySensorModel':{'check_with':string_for_null, 'nullable': True},
	'axes':{'check_with':string_for_null, 'nullable': True},
	'accelerometrySensorUnitsReported':{'check_with':string_for_null, 'nullable': True},
	'accelerometryLowerSensorDetectionLimit':{'check_with':integer_for_null, 'nullable': True},
	'accelerometryUpperSensorDetectionLimit':{'check_with':integer_for_null, 'nullable': True},
	'accelerometrySensorPrecision':{'check_with':integer_for_null, 'nullable': True},
	'accelerometrySensorSamplingFrequency':{'check_with':integer_for_null, 'nullable': True},
	'accelerometrySensorDutyCycling':{'check_with':string_for_null, 'nullable': True},
	'accelerometrySensorCalibrationDate': { 'nullable': True,'coerce': to_date},
	'accelerometrySensorCalibrationDetails':{'check_with':string_for_null, 'nullable': True},

}


InputDataSchema={	
	'instrumentID':{'check_with':isalphnumric,'nullable': True,},#this field is required,
	'deploymentID':{'check_with':isalphnumric,'nullable': True,},#this field is required
	'organismID':{'check_with':isalphnumric,'nullable': True},#this field is required
	'organismIDSource':{'check_with':string_for_null, 'nullable': True},
	'time':{'nullable': True,'coerce': to_date},#this field is required
	'latitude':{'check_with':decimal,'nullable': True},
	'longitude': {'check_with':decimal,'nullable': True},
	'argosLC':{'check_with':string_for_null, 'nullable': True},
	'argosErrorRadius':{'check_with':string_for_null, 'nullable': True},
	'argosSemiMajor':{'check_with':float_for_null, 'nullable': True},
	'argosSemiMinor':{'check_with':integer_for_null, 'nullable': True},
	'argosOrientation':{'check_with':integer_for_null, 'nullable': True},
	'argosGDOP':{'check_with':string_for_null, 'nullable': True},
	'gpsSatelliteCount':{'check_with':integer_for_null, 'nullable': True},
	'residualsGPS(rapid acquisition GPS)':{'check_with':float_for_null, 'nullable': True},
	'temperatureGLS':{'check_with':float_for_null, 'nullable': True},
	'depthGLS':{'check_with':float_for_null, 'nullable': True},
	'sensorIType': {'check_with':string_for_null, 'nullable': True},
	'sensorIMeasurement':{'check_with':string_for_null, 'nullable': True},
}




class ValidateMatching(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = ValidateMatchingSerializer
	def post(self, request):
		deployment_unique_values_list = []
		organism_unique_values_list = []
		row_count=0
		no_error_row_count=0
		row_data_list=[]
		request_data = request.data
		serializer = self.serializer_class(data=request_data)
		serializer.is_valid(raise_exception=True)
		get_file_instance=get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type=request_data['csv_type'])
		
		df=pd.read_csv(get_file_instance.csv_file, encoding = "ISO-8859-1", error_bad_lines=False)
		df = df.fillna('')
		df_dic=df.to_dict(orient='records')
		for dicts in df_dic:
			for keys in dicts:
				if is_integer(dicts[keys]):
					dicts[keys]=int(dicts[keys])
				elif is_float(dicts[keys]):
					dicts[keys]=float(dicts[keys])
				elif dicts[keys]=='' :
					dicts[keys]=None

		if request_data['csv_type'] == 'Deployment MetaData':
			v=Validator(DeploymentMetadataSchema)
			CsvFileData.objects.filter(upload_identifier=request_data['upload_identifier']).filter(csv_type=request_data['csv_type']).update(matchedcolums=request_data['MatchedColumns'])
			CsvFileData.objects.filter(upload_identifier=request_data['upload_identifier']).update(fileuploadstatus_id=get_object_or_404(FileUploadStatus,id=request_data['fileuploadstatus_id']))
			row_count=0
			no_error_row_count=0
			get_file_instance=get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type=request_data['csv_type'])
			# print(get_file_instance.csv_file.path)
			try:
				import requests
				r = requests.get(get_file_instance.csv_file.url)
				with open("media/"+str(get_file_instance.csv_file),'wb') as f:
					f.write(r.content)
				with open('media/'+str(get_file_instance.csv_file), 'r', newline='', encoding='ISO-8859-1') as file:
					csvreader = csv.reader(file)
					header = next(csvreader)
					MatchedColumns=request_data['MatchedColumns']
					if not len(set(list(MatchedColumns.values()))) == len(header):
						raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched') 
					for row in csvreader:
						row_count=row_count+1
						error_list=[]
						detail_data=dict(zip(header,row))
						if request_data['csv_type'] == 'Deployment MetaData':
							for f in header:
								if f == MatchedColumns['deploymentID']:
										deployment_unique_values_list.append(detail_data[MatchedColumns['deploymentID']])
										if not v.validate({'deploymentID':detail_data[MatchedColumns['deploymentID']]}):
											error_list.append({'Label':'deploymentID','key':'deploymentID','message':' '.join(map(str, v.errors['deploymentID']))})
										elif DeploymentMetadata.objects.filter(deployment_id=detail_data[MatchedColumns['deploymentID']]).filter(~Q(upload_identifier=request_data['upload_identifier'])).exists():
											error_list.append({'Label':'Deployment ID','key':'deploymentID','message': f"Field '{f}' expected Unique Alphanumeric but '{detail_data[MatchedColumns['deploymentID']]}' already exists"})
										else:
											pass
								
								elif f == MatchedColumns['instrumentID']:
										if not v.validate({'instrumentID':detail_data[MatchedColumns['instrumentID']]}):
											error_list.append({'Label':'Instrument ID','key':'instrumentID','message':' '.join(map(str, v.errors['instrumentID']))})
										else:
											pass
							
								elif f == MatchedColumns['ptt']:
										if not v.validate({'ptt':detail_data[MatchedColumns['ptt']]}):
											error_list.append({'Label':'PTT','key':'ptt','message':' '.join(map(str, v.errors['ptt']))})
										else:
											pass

								elif f == MatchedColumns['transmissionSettings']:
										if not v.validate({'transmissionSettings':detail_data[MatchedColumns['transmissionSettings']]}):
											error_list.append({'Label':'Transmission Settings','key':'transmissionSettings','message':' '.join(map(str, v.errors['transmissionSettings']))})
										else:
											pass

								elif f == MatchedColumns['transmissionMode']:
										if not v.validate({'transmissionMode':detail_data[MatchedColumns['transmissionMode']]}):
											error_list.append({'Label':'Transmission Mode','key':'transmissionMode','message':' '.join(map(str, v.errors['transmissionMode']))})
										else:
											pass
								
								elif f == MatchedColumns['dutyCycle']:
										if not v.validate({'dutyCycle':detail_data[MatchedColumns['dutyCycle']]}):
											error_list.append({'Label':'Duty Cycle','key':'dutyCycle','message':' '.join(map(str, v.errors['dutyCycle']))})
										else:
											pass
								
								elif f == MatchedColumns['instrumentSettings']:
										if not v.validate({'instrumentSettings':detail_data[MatchedColumns['instrumentSettings']]}):
											error_list.append({'Label':'Instrument Settings','key':'instrumentSettings','message':' '.join(map(str, v.errors['instrumentSettings']))})
										else:
											pass

								elif f == MatchedColumns['deploymentDateTime']:
										if not v.validate({'deploymentDateTime':detail_data[MatchedColumns['deploymentDateTime']]}):
											error_list.append({'Label':'Deployment Date Time','key':'deploymentDateTime','message':' '.join(map(str, v.errors['deploymentDateTime']))})
										else:
											pass
									
								elif f == MatchedColumns['deploymentLatitude']:
										if not v.validate({'deploymentLatitude':detail_data[MatchedColumns['deploymentLatitude']]}):
											error_list.append({'Label':'Deployment Latitude','key':'deploymentLatitude','message':' '.join(map(str, v.errors['deploymentLatitude']))})
										else:
											pass
								
								elif f == MatchedColumns['deploymentLongitude']:
										if not v.validate({'deploymentLongitude':detail_data[MatchedColumns['deploymentLongitude']]}):
											error_list.append({'Label':'Deployment Longitude','key':'deploymentLongitude','message':' '.join(map(str, v.errors['deploymentLongitude']))})
										else:
											pass

								elif f == MatchedColumns['deploymentEndType']:
										# print("deploymentEndType")
										if not v.validate({'deploymentEndType':detail_data[MatchedColumns['deploymentEndType']]}):
											error_list.append({'Label':'Deployment EndType','key':'deploymentEndType','message':' '.join(map(str, v.errors['deploymentEndType']))})
										else:
											pass

								elif f == MatchedColumns['detachmentDateTime']:
										if not v.validate({'detachmentDateTime':detail_data[MatchedColumns['detachmentDateTime']]}):
											error_list.append({'Label':'Detachment Date Time','key':'detachmentDateTime','message':' '.join(map(str, v.errors['detachmentDateTime']))})
										else:
											pass

								elif f == MatchedColumns['detachmentDetails']:
										if not v.validate({'detachmentDetails':detail_data[MatchedColumns['detachmentDetails']]}):
											error_list.append({'Label':'DetachmentDetails','key':'detachmentDetails','message':' '.join(map(str, v.errors['detachmentDetails']))})
										else:
											pass
								
								elif f == MatchedColumns['detachmentLatitude']:
										if not v.validate({'detachmentLatitude':detail_data[MatchedColumns['detachmentLatitude']]}):
											error_list.append({'Label':'Detachment Latitude','key':'detachmentLatitude','message':' '.join(map(str, v.errors['detachmentLatitude']))})
										else:
											pass
							
								elif f == MatchedColumns['detachmentLongitude']:
										if not v.validate({'detachmentLongitude':detail_data[MatchedColumns['detachmentLongitude']]}):
											error_list.append({'Label':'Detachment Longitude','key':'detachmentLongitude','message':' '.join(map(str, v.errors['detachmentLongitude']))})
										else:
											pass

								elif f == MatchedColumns['trackStartTime']:
										# print( MatchedColumns['trackStartTime'])
										if not v.validate({'trackStartTime':detail_data[MatchedColumns['trackStartTime']]}):
											error_list.append({'Label':'Track Start Time','key':'trackStartTime','message':' '.join(map(str, v.errors['trackStartTime']))})
										else:
											pass
		
								elif  f ==  MatchedColumns['trackStartLatitude']:
										if not v.validate({'trackStartLatitude':detail_data[MatchedColumns['trackStartLatitude']]}):
											error_list.append({'Label':'Track Start Latitude','key':'trackStartLatitude','message':' '.join(map(str, v.errors['trackStartLatitude']))})
										else:
											pass

								elif f == MatchedColumns['trackStartLongitude']:
										if not v.validate({'trackStartLongitude':detail_data[MatchedColumns['trackStartLongitude']]}):
											error_list.append({'Label':'Track Start Longitude','key':'trackStartLongitude','message':' '.join(map(str, v.errors['trackStartLongitude']))})
										else:
											pass

								elif f == MatchedColumns['trackEndTime']:
										if not v.validate({'trackEndTime':detail_data[MatchedColumns['trackEndTime']]}):
											error_list.append({'Label':'Track End Time','key':'trackEndTime','message':' '.join(map(str, v.errors['trackEndTime']))})
										else:
											pass

								elif f == MatchedColumns['trackEndLatitude']:
										if not v.validate({'trackEndLatitude':detail_data[MatchedColumns['trackEndLatitude']]}):
											error_list.append({'Label':'Track End Latitude','key':'trackEndLatitude','message':' '.join(map(str, v.errors['trackEndLatitude']))})
										else:
											pass

								elif f == MatchedColumns['trackEndLongitude']:
										if not v.validate({'trackEndLongitude':detail_data[MatchedColumns['trackEndLongitude']]}):
											error_list.append({'Label':'Track End Longitude','key':'trackEndLongitude','message':' '.join(map(str, v.errors['trackEndLongitude']))})
										else:
											pass

								elif f == MatchedColumns['sunElevationAngle']:
										if not v.validate({'sunElevationAngle':detail_data[MatchedColumns['sunElevationAngle']]}):
											error_list.append({'Label':'Sun Elevation Angle','key':'sunElevationAngle','message':' '.join(map(str, v.errors['sunElevationAngle']))})
										else:
											pass
								
								elif f == MatchedColumns['argosFilderMethod']:
										if not v.validate({'argosFilderMethod':detail_data[MatchedColumns['argosFilderMethod']]}):
											error_list.append({'Label':'Argos Filder Method','key':'argosFilderMethod','message':' '.join(map(str, v.errors['argosFilderMethod']))})
										else:
											pass
								
								elif f == MatchedColumns['organismID']:
										if not v.validate({'organismID':detail_data[MatchedColumns['organismID']]}):
											error_list.append({'Label':'Organism ID','key':'organismID','message':' '.join(map(str, v.errors['organismID']))})
										else:
											pass
									
								elif f == MatchedColumns['scientificName']:
										if not v.validate({'scientificName':detail_data[MatchedColumns['scientificName']]}):
											error_list.append({'Label':'Scientific Name','key':'scientificName','message':' '.join(map(str, v.errors['scientificName']))})
										else:
											pass
								
								elif f == MatchedColumns['scientificNameSource']:
										if not v.validate({'scientificNameSource':detail_data[MatchedColumns['scientificNameSource']]}):
											error_list.append({'Label':'Scientific Name Source','key':'scientificNameSource','message':' '.join(map(str, v.errors['scientificNameSource']))})
										else:
											pass
								
								elif f == MatchedColumns['commonName']:
										if not v.validate({'commonName':detail_data[MatchedColumns['commonName']]}):
											error_list.append({'Label':'Common Name','key':'commonName','message':' '.join(map(str, v.errors['commonName']))})
										else:
											pass
								
								elif f == MatchedColumns['organismSex']:
										if not v.validate({'organismSex':detail_data[MatchedColumns['organismSex']]}):
											error_list.append({'Label':'Organism Sex','key':'organismSex','message':' '.join(map(str, v.errors['organismSex']))})
										else:
											pass
								
								elif f == MatchedColumns['organismWeightAtDeployment']:
										if not v.validate({'organismWeightAtDeployment':detail_data[MatchedColumns['organismWeightAtDeployment']]}):
											error_list.append({'Label':'Organism Weight At Deployment','key':'organismWeightAtDeployment','message':' '.join(map(str, v.errors['organismWeightAtDeployment']))})
										else:
											pass
								
								elif f == MatchedColumns['organismWeightRemeasurement']:
										if not v.validate({'organismWeightRemeasurement':detail_data[MatchedColumns['organismWeightRemeasurement']]}):
											error_list.append({'Label':'Organism Weight Remeasurement','key':'organismWeightRemeasurement','message':' '.join(map(str, v.errors['organismWeightRemeasurement']))})
										else:
											pass
								
								elif f == MatchedColumns['organismWeightRemeasurementTime']:
										if not v.validate({'organismWeightRemeasurementTime':detail_data[MatchedColumns['organismWeightRemeasurementTime']]}):
											error_list.append({'Label':'Organism Weight Remeasurement Time','key':'organismWeightRemeasurementTime','message':' '.join(map(str, v.errors['organismWeightRemeasurementTime']))})
										else:
											pass
								
								elif f == MatchedColumns['organismSize']:
										if not v.validate({'organismSize':detail_data[MatchedColumns['organismSize']]}):
											error_list.append({'Label':'Organism Size','key':'organismSize','message':' '.join(map(str, v.errors['organismSize']))})
										else:
											pass
								
								elif f == MatchedColumns['organismSizeMeasurementType']:
										if not v.validate({'organismSizeMeasurementType':detail_data[MatchedColumns['organismSizeMeasurementType']]}):
											error_list.append({'Label':'Organism Size Measurement Type','key':'organismSizeMeasurementType','message':' '.join(map(str, v.errors['organismSizeMeasurementType']))})
										else:
											pass
								
								elif f == MatchedColumns['organismSizeMeasurementDescription']:
										if not v.validate({'organismSizeMeasurementDescription':detail_data[MatchedColumns['organismSizeMeasurementDescription']]}):
											error_list.append({'Label':'Organism Size Measurement Description','key':'organismSizeMeasurementDescription','message':' '.join(map(str, v.errors['organismSizeMeasurementDescription']))})
										else:
											pass
								
								elif  f ==  MatchedColumns['organismSizeMeasurementTime']:
										if not v.validate({'organismSizeMeasurementTime':detail_data[MatchedColumns['organismSizeMeasurementTime']]}):
											error_list.append({'Label':'Organism Size Measurement Time','key':'organismSizeMeasurementTime','message':' '.join(map(str, v.errors['organismSizeMeasurementTime']))})
										else:
											pass

								elif  f ==  MatchedColumns['organismAgeReproductiveClass']:
										if not v.validate({'organismAgeReproductiveClass':detail_data[MatchedColumns['organismAgeReproductiveClass']]}):
											error_list.append({'Label':'Organism Age Reproductive Class','key':'organismAgeReproductiveClass','message':' '.join(map(str, v.errors['organismAgeReproductiveClass']))})
										else:
											pass
								elif f == MatchedColumns['trappingMethodDetails']:
										if not v.validate({'trappingMethodDetails':detail_data[MatchedColumns['trappingMethodDetails']]}):
											error_list.append({'Label':'Trapping Method Details','key':'trappingMethodDetails','message':' '.join(map(str, v.errors['trappingMethodDetails']))})
										else:
											pass
								
								elif f == MatchedColumns['attachmentMethod']:
										if not v.validate({'attachmentMethod':detail_data[MatchedColumns['attachmentMethod']]}):
											error_list.append({'Label':'Attachment Method','key':'attachmentMethod','message':' '.join(map(str, v.errors['attachmentMethod']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalCalibrationsDone']:
										if not v.validate({'environmentalCalibrationsDone':detail_data[MatchedColumns['environmentalCalibrationsDone']]}):
											error_list.append({'Label':'Environmental Calibrations Done','key':'environmentalCalibrationsDone','message':' '.join(map(str, v.errors['environmentalCalibrationsDone']))})
										else:
											pass
		
								
								elif f == MatchedColumns['environmentalQcDone']:
										if not v.validate({'environmentalQcDone':detail_data[MatchedColumns['environmentalQcDone']]}):
											error_list.append({'Label':'Environmental QcDone','key':'environmentalQcDone','message':' '.join(map(str, v.errors['environmentalQcDone']))})
										else:
											pass
							
								
								elif f == MatchedColumns['environmentalQcProblemsFound']:
										if not v.validate({'environmentalQcProblemsFound':detail_data[MatchedColumns['environmentalQcProblemsFound']]}):
											error_list.append({'Label':'Environmental QcProblems Found','key':'environmentalQcProblemsFound','message':' '.join(map(str, v.errors['environmentalQcProblemsFound']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalQcNotes']:
										if not v.validate({'environmentalQcNotes':detail_data[MatchedColumns['environmentalQcNotes']]}):
											error_list.append({'Label':'Environmental QcNotes','key':'environmentalQcNotes','message':' '.join(map(str, v.errors['environmentalQcNotes']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalCalibrationsDone']:
										if not v.validate({'physiologicalCalibrationsDone':detail_data[MatchedColumns['physiologicalCalibrationsDone']]}):
											error_list.append({'Label':'Physiological Calibrations Done','key':'physiologicalCalibrationsDone','message':' '.join(map(str, v.errors['physiologicalCalibrationsDone']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalQcDone']:
										if not v.validate({'physiologicalQcDone':detail_data[MatchedColumns['physiologicalQcDone']]}):
											error_list.append({'Label':'Physiological QcDone','key':'physiologicalQcDone','message':' '.join(map(str, v.errors['physiologicalQcDone']))})
										else:
											pass
					
								elif f == MatchedColumns['physiologicalQcProblemsFound']:
										if not v.validate({'physiologicalQcProblemsFound':detail_data[MatchedColumns['physiologicalQcProblemsFound']]}):
											error_list.append({'Label':'Physiological QcProblems Found','key':'physiologicalQcProblemsFound','message':' '.join(map(str, v.errors['physiologicalQcProblemsFound']))})
										else:
											pass
							
								elif f == MatchedColumns['physiologicalQcNotes']:
										if not v.validate({'physiologicalQcNotes':detail_data[MatchedColumns['physiologicalQcNotes']]}):
											error_list.append({'Label':'Physiological QcNotes','key':'physiologicalQcNotes','message':' '.join(map(str, v.errors['physiologicalQcNotes']))})
										else:
											pass
								elif f == MatchedColumns['accelerometryPositionOfAccelerometerOnOrganism']:
										if not v.validate({'accelerometryPositionOfAccelerometerOnOrganism':detail_data[MatchedColumns['accelerometryPositionOfAccelerometerOnOrganism']]}):
											error_list.append({'Label':'AccelerometryPosition Of Accelerometer On Organism','key':'accelerometryPositionOfAccelerometerOnOrganism','message':' '.join(map(str, v.errors['accelerometryPositionOfAccelerometerOnOrganism']))})
										else:
											pass

								elif f == MatchedColumns['accelerometryOrientationOfAccelerometerOnOrganism']:
										if not v.validate({'accelerometryOrientationOfAccelerometerOnOrganism':detail_data[MatchedColumns['accelerometryOrientationOfAccelerometerOnOrganism']]}):
											error_list.append({'Label':'Accelerometry Orientation Of AccelerometerOnOrganism','key':'accelerometryOrientationOfAccelerometerOnOrganism','message':' '.join(map(str, v.errors['accelerometryOrientationOfAccelerometerOnOrganism']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometryCalibrationsDone']:
										if not v.validate({'accelerometryCalibrationsDone':detail_data[MatchedColumns['accelerometryCalibrationsDone']]}):
											error_list.append({'Label':'Accelerometry Calibrations Done','key':'accelerometryCalibrationsDone','message':' '.join(map(str, v.errors['accelerometryCalibrationsDone']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometryQcDone']:
										if not v.validate({'accelerometryQcDone':detail_data[MatchedColumns['accelerometryQcDone']]}):
											error_list.append({'Label':'Accelerometry QcDone','key':'accelerometryQcDone','message':' '.join(map(str, v.errors['accelerometryQcDone']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometryQcProblemsFound']:
										if not v.validate({'accelerometryQcProblemsFound':detail_data[MatchedColumns['accelerometryQcProblemsFound']]}):
											error_list.append({'Label':'Accelerometry QcProblems Found','key':'accelerometryQcProblemsFound','message':' '.join(map(str, v.errors['accelerometryQcProblemsFound']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometryQcNotes']:
										if not v.validate({'accelerometryQcNotes':detail_data[MatchedColumns['accelerometryQcNotes']]}):
											error_list.append({'Label':'AccelerometryQcNotes','key':'accelerometryQcNotes','message':' '.join(map(str, v.errors['accelerometryQcNotes']))})
										else:
											pass
								
								elif  f ==  MatchedColumns['ownerName']:
										if not v.validate({'ownerName':detail_data[MatchedColumns['ownerName']]}):
											error_list.append({'Label':'Owner Name','key':'ownerName','message':' '.join(map(str, v.errors['ownerName']))})
										else:
											pass
								
								elif f == MatchedColumns['ownerEmailContact']:
										if not v.validate({'ownerEmailContact':detail_data[MatchedColumns['ownerEmailContact']]}):
											error_list.append({'Label':'Owner Email Aontact','key':'ownerEmailContact','message':' '.join(map(str, v.errors['ownerEmailContact']))})
										else:
											pass
								
								elif f == MatchedColumns['ownerInstitutionalContact']:
										if not v.validate({'ownerInstitutionalContact':detail_data[MatchedColumns['ownerInstitutionalContact']]}):
											error_list.append({'Label':'Owner Institutional Contact','key':'ownerInstitutionalContact','message':' '.join(map(str, v.errors['ownerInstitutionalContact']))})
										else:
											pass
								
								elif f == MatchedColumns['ownerPhoneContact']:
										if not v.validate({'ownerPhoneContact':detail_data[MatchedColumns['ownerPhoneContact']]}):
											error_list.append({'Label':'Owner Phone Contact','key':'ownerPhoneContact','message':' '.join(map(str, v.errors['ownerPhoneContact']))})
										else:
											pass
								
								elif f == MatchedColumns['license']:
										if not v.validate({'license':detail_data[MatchedColumns['license']]}):
											error_list.append({'Label':'License','key':'license','message':' '.join(map(str, v.errors['license']))})
										else:
											pass
								
								elif f == MatchedColumns['otherRelevantIdentifiers']:
										if not v.validate({'otherRelevantIdentifiers':detail_data[MatchedColumns['otherRelevantIdentifiers']]}):
											error_list.append({'Label':'Other Relevant Identifiers','key':'otherRelevantIdentifiers','message':' '.join(map(str, v.errors['otherRelevantIdentifiers']))})
										else:
											pass
								
								elif f == MatchedColumns['otherDataTypesAssociatedWithDeployment']:
										if not v.validate({'otherDataTypesAssociatedWithDeployment':detail_data[MatchedColumns['otherDataTypesAssociatedWithDeployment']]}):
											error_list.append({'Label':'Other DataTypes AssociatedWithDeployment','key':'otherDataTypesAssociatedWithDeployment','message':' '.join(map(str, v.errors['otherDataTypesAssociatedWithDeployment']))})
										else:
											pass
							
								elif f == MatchedColumns['references']:
										if not v.validate({'references':detail_data[MatchedColumns['references']]}):
											error_list.append({'Label':'References','key':'references','message':' '.join(map(str, v.errors['references']))})
										else:
											pass
								
								elif f == MatchedColumns['citation']:
										if not v.validate({'citation':detail_data[MatchedColumns['citation']]}):
											error_list.append({'Label':'Citation','key':'citation','message':' '.join(map(str, v.errors['citation']))})
										else:
											pass
							row_data_list.append({**detail_data, **{'errors':error_list}})
			except:
				raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched')         

		elif request_data['csv_type'] == 'Device MetaData':
			v=Validator(DevicementMetadataSchema)
			CsvFileData.objects.filter(upload_identifier=request_data['upload_identifier']).filter(csv_type=request_data['csv_type']).update(matchedcolums=request_data['MatchedColumns'])
			CsvFileData.objects.filter(upload_identifier=request_data['upload_identifier']).update(fileuploadstatus_id=get_object_or_404(FileUploadStatus,id=request_data['fileuploadstatus_id']))
		
			row_count=0
			no_error_row_count=0
			get_file_instance=get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type=request_data['csv_type'])
			try:
				import requests
				r = requests.get(get_file_instance.csv_file.url)
				with open("media/"+str(get_file_instance.csv_file),'wb') as f:
					f.write(r.content)
				with open('media/'+str(get_file_instance.csv_file), 'r', newline='', encoding='ISO-8859-1') as file:
					csvreader = csv.reader(file)
					header = next(csvreader)
					MatchedColumns=request_data['MatchedColumns']
					if not len(set(list(MatchedColumns.values()))) == len(header):
						raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched')
					for row in csvreader:
						row_count=row_count+1
						error_list=[]
						detail_data=dict(zip(header,row))
						if request_data['csv_type'] == 'Device MetaData':
							for f in header:
								if f == MatchedColumns['instrumentID']:
										if not v.validate({'instrumentID':detail_data[MatchedColumns['instrumentID']]}):
											error_list.append({'Label':'Instrument ID','key':'instrumentID','message':' '.join(map(str, v.errors['instrumentID']))})
										else:
											pass
								
								elif f == MatchedColumns['instrumentType']:
										if not v.validate({'instrumentType':detail_data[MatchedColumns['instrumentType']]}):
											error_list.append({'Label':'Instrument Type','key':'instrumentType','message':' '.join(map(str, v.errors['instrumentType']))})
										else:
											pass
								
								elif f == MatchedColumns['instrumentModel']:
										if not v.validate({'instrumentModel':detail_data[MatchedColumns['instrumentModel']]}):
											error_list.append({'Label':'Instrument Model','key':'instrumentModel','message':' '.join(map(str, v.errors['instrumentModel']))})
										else:
											pass
								
								elif f == MatchedColumns['instrumentManufacturer']:
										if not v.validate({'instrumentManufacturer':detail_data[MatchedColumns['instrumentManufacturer']]}):
											error_list.append({'Label':'Instrument Manufacturer','key':'instrumentManufacturer','message':' '.join(map(str, v.errors['instrumentManufacturer']))})
										else:
											pass
								
								elif f == MatchedColumns['instrumentSerialNumber']:
										if not v.validate({'instrumentSerialNumber':detail_data[MatchedColumns['instrumentSerialNumber']]}):
											error_list.append({'Label':'Instrument Serial Number','key':'instrumentSerialNumber','message':' '.join(map(str, v.errors['instrumentSerialNumber']))})
										else:
											pass
								
								elif f == MatchedColumns['trackingDevice']:
										if not v.validate({'trackingDevice':detail_data[MatchedColumns['trackingDevice']]}):
											error_list.append({'Label':'Tracking Device','key':'trackingDevice','message':' '.join(map(str, v.errors['trackingDevice']))})
										else:
											pass
								
								elif f == MatchedColumns['horizontalSensorUplinkInterval']:
										if not v.validate({'horizontalSensorUplinkInterval':detail_data[MatchedColumns['horizontalSensorUplinkInterval']]}):
											error_list.append({'Label':'Horizontal Sensor Uplink Interval','key':'horizontalSensorUplinkInterval','message':' '.join(map(str, v.errors['horizontalSensorUplinkInterval']))})
										else:
											pass
								
								elif f == MatchedColumns['horizontalSensorUplinkIntervalUnits']:
										if not v.validate({'horizontalSensorUplinkIntervalUnits':detail_data[MatchedColumns['horizontalSensorUplinkIntervalUnits']]}):
											error_list.append({'Label':'Horizontal Sensor Uplink Interval Units','key':'horizontalSensorUplinkIntervalUnits','message':' '.join(map(str, v.errors['horizontalSensorUplinkIntervalUnits']))})
										else:
											pass
								
								elif f == MatchedColumns['verticalSensorUnitsReported']:
										if not v.validate({'verticalSensorUnitsReported':detail_data[MatchedColumns['verticalSensorUnitsReported']]}):
											error_list.append({'Label':'Vertical Sensor Units Reported','key':'verticalSensorUnitsReported','message':' '.join(map(str, v.errors['verticalSensorUnitsReported']))})
										else:
											pass
								
								elif f == MatchedColumns['resolution']:
										if not v.validate({'resolution':detail_data[MatchedColumns['resolution']]}):
											error_list.append({'Label':'Resolution','key':'resolution','message':' '.join(map(str, v.errors['resolution']))})
										else:
											pass
								
								elif f == MatchedColumns['verticalLowerSensorDetectionLimit']:
										if not v.validate({'verticalLowerSensorDetectionLimit':detail_data[MatchedColumns['verticalLowerSensorDetectionLimit']]}):
											error_list.append({'Label':'Vertical Lower Sensor Detection Limit','key':'verticalLowerSensorDetectionLimit','message':' '.join(map(str, v.errors['verticalLowerSensorDetectionLimit']))})
										else:
											pass
								
								elif f == MatchedColumns['verticalUpperSensorDetectionLimit']:
										if not v.validate({'verticalUpperSensorDetectionLimit':detail_data[MatchedColumns['verticalUpperSensorDetectionLimit']]}):
											error_list.append({'Label':'Vertical Upper Sensor Detection Limit','key':'verticalUpperSensorDetectionLimit','message':' '.join(map(str, v.errors['verticalUpperSensorDetectionLimit']))})
										else:
											pass
								
								elif f == MatchedColumns['verticalSensorPrecision']:
										if not v.validate({'verticalSensorPrecision':detail_data[MatchedColumns['verticalSensorPrecision']]}):
											error_list.append({'Label':'Vertical Sensor Precision','key':'verticalSensorPrecision','message':' '.join(map(str, v.errors['verticalSensorPrecision']))})
										else:
											pass
								
								elif f == MatchedColumns['verticalSensorSamplingFrequency']:
										if not v.validate({'verticalSensorSamplingFrequency':detail_data[MatchedColumns['verticalSensorSamplingFrequency']]}):
											error_list.append({'Label':'Vertical Sensor Sampling Frequency','key':'verticalSensorSamplingFrequency','message':' '.join(map(str, v.errors['verticalSensorSamplingFrequency']))})
										else:
											pass
								
								elif f == MatchedColumns['verticalSensorDutyCycling']:
										if not v.validate({'verticalSensorDutyCycling':detail_data[MatchedColumns['verticalSensorDutyCycling']]}):
											error_list.append({'Label':'Vertical Sensor Duty Cycling','key':'verticalSensorDutyCycling','message':' '.join(map(str, v.errors['verticalSensorDutyCycling']))})
										else:
											pass
								
								elif f == MatchedColumns['verticalSensorCalibrationDate']:
										if not v.validate({'verticalSensorCalibrationDate':detail_data[MatchedColumns['verticalSensorCalibrationDate']]}):
											error_list.append({'Label':'Vertical Sensor Calibration Date','key':'verticalSensorCalibrationDate','message':' '.join(map(str, v.errors['verticalSensorCalibrationDate']))})
										else:
											pass
								
								elif  f ==  MatchedColumns['verticalSensorCalibrationDetails']:
										if not v.validate({'verticalSensorCalibrationDetails':detail_data[MatchedColumns['verticalSensorCalibrationDetails']]}):
											error_list.append({'Label':'Vertical Sensor Calibration Details','key':'verticalSensorCalibrationDetails','message':' '.join(map(str, v.errors['verticalSensorCalibrationDetails']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorType']:
										if not v.validate({'environmentalSensorType':detail_data[MatchedColumns['environmentalSensorType']]}):
											error_list.append({'Label':'Environmental Sensor Type','key':'environmentalSensorType','message':' '.join(map(str, v.errors['environmentalSensorType']))})
										else:
											pass     
								
								elif f == MatchedColumns['environmentalSensorManufacturer']:
										if not v.validate({'environmentalSensorManufacturer':detail_data[MatchedColumns['environmentalSensorManufacturer']]}):
											error_list.append({'Label':'Environmental Sensor Manufacturer','key':'environmentalSensorManufacturer','message':' '.join(map(str, v.errors['environmentalSensorManufacturer']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorModel']:
										if not v.validate({'environmentalSensorModel':detail_data[MatchedColumns['environmentalSensorModel']]}):
											error_list.append({'Label':'Environmental Sensor Model','key':'environmentalSensorModel','message':' '.join(map(str, v.errors['environmentalSensorModel']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorUnitsReported']:
										if not v.validate({'environmentalSensorUnitsReported':detail_data[MatchedColumns['environmentalSensorUnitsReported']]}):
											error_list.append({'Label':'Environmental Sensor Units Reported','key':'environmentalSensorUnitsReported','message':' '.join(map(str, v.errors['environmentalSensorUnitsReported']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalLowerSensorDetectionLimit']:
										if not v.validate({'environmentalLowerSensorDetectionLimit':detail_data[MatchedColumns['environmentalLowerSensorDetectionLimit']]}):
											error_list.append({'Label':'Environmental Lower Sensor Detection Limit','key':'environmentalLowerSensorDetectionLimit','message':' '.join(map(str, v.errors['environmentalLowerSensorDetectionLimit']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalUpperSensorDetectionLimit']:
										if not v.validate({'environmentalUpperSensorDetectionLimit':detail_data[MatchedColumns['environmentalUpperSensorDetectionLimit']]}):
											error_list.append({'Label':'Environmental Upper Sensor Detection Limit','key':'environmentalUpperSensorDetectionLimit','message':' '.join(map(str, v.errors['environmentalUpperSensorDetectionLimit']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorPrecision']:
										if not v.validate({'environmentalSensorPrecision':detail_data[MatchedColumns['environmentalSensorPrecision']]}):
											error_list.append({'Label':'Environmental Sensor Precision','key':'environmentalSensorPrecision','message':' '.join(map(str, v.errors['environmentalSensorPrecision']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorSamplingFrequency']:
										if not v.validate({'environmentalSensorSamplingFrequency':detail_data[MatchedColumns['environmentalSensorSamplingFrequency']]}):
											error_list.append({'Label':'Environmental Sensor Sampling Erequency','key':'environmentalSensorSamplingFrequency','message':' '.join(map(str, v.errors['environmentalSensorSamplingFrequency']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorDutyCycling']:
										if not v.validate({'environmentalSensorDutyCycling':detail_data[MatchedColumns['environmentalSensorDutyCycling']]}):
											error_list.append({'Label':'Environmental Sensor Duty Cycling','key':'environmentalSensorDutyCycling','message':' '.join(map(str, v.errors['environmentalSensorDutyCycling']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorCalibrationDate']:
										if not v.validate({'environmentalSensorCalibrationDate':detail_data[MatchedColumns['environmentalSensorCalibrationDate']]}):
											error_list.append({'Label':'Environmental Sensor CalibrationDate','key':'environmentalSensorCalibrationDate','message':' '.join(map(str, v.errors['environmentalSensorCalibrationDate']))})
										else:
											pass
								
								elif f == MatchedColumns['environmentalSensorCalibrationDetails']:
										if not v.validate({'environmentalSensorCalibrationDetails':detail_data[MatchedColumns['environmentalSensorCalibrationDetails']]}):
											error_list.append({'Label':'Environmental Sensor Calibration Details','key':'environmentalSensorCalibrationDetails','message':' '.join(map(str, v.errors['environmentalSensorCalibrationDetails']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalSensorType']:
										if not v.validate({'physiologicalSensorType':detail_data[MatchedColumns['physiologicalSensorType']]}):
											error_list.append({'Label':'Physiological Sensor Type','key':'physiologicalSensorType','message':' '.join(map(str, v.errors['physiologicalSensorType']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalSensorManufacturer']:
										if not v.validate({'physiologicalSensorManufacturer':detail_data[MatchedColumns['physiologicalSensorManufacturer']]}):
											error_list.append({'Label':'Physiological Sensor Manufacturer','key':'physiologicalSensorManufacturer','message':' '.join(map(str, v.errors['physiologicalSensorManufacturer']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalSensorModel']:
										if not v.validate({'physiologicalSensorModel':detail_data[MatchedColumns['physiologicalSensorModel']]}):
											error_list.append({'Label':'Physiological Sensor Model','key':'physiologicalSensorModel','message':' '.join(map(str, v.errors['physiologicalSensorModel']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalSensorUnitsReported']:
										if not v.validate({'physiologicalSensorUnitsReported':detail_data[MatchedColumns['physiologicalSensorUnitsReported']]}):
											error_list.append({'Label':'Physiological Sensor Units Reported','key':'physiologicalSensorUnitsReported','message':' '.join(map(str, v.errors['physiologicalSensorUnitsReported']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalLowerSensorDetectionLimit']:
										if not v.validate({'physiologicalLowerSensorDetectionLimit':detail_data[MatchedColumns['physiologicalLowerSensorDetectionLimit']]}):
											error_list.append({'Label':'Physiological Lower Sensor Detection Limit','key':'physiologicalLowerSensorDetectionLimit','message':' '.join(map(str, v.errors['physiologicalLowerSensorDetectionLimit']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalUpperSensorDetectionLimit']:
										if not v.validate({'physiologicalUpperSensorDetectionLimit':detail_data[MatchedColumns['physiologicalUpperSensorDetectionLimit']]}):
											error_list.append({'Label':'Physiological Upper Sensor Detection Limit','key':'physiologicalUpperSensorDetectionLimit','message':' '.join(map(str, v.errors['physiologicalUpperSensorDetectionLimit']))})
										else:
											pass
								
								elif  f ==  MatchedColumns['physiologicalSensorPrecision']:
										if not v.validate({'physiologicalSensorPrecision':detail_data[MatchedColumns['physiologicalSensorPrecision']]}):
											error_list.append({'Label':'Physiological Sensor Precision','key':'physiologicalSensorPrecision','message':' '.join(map(str, v.errors['physiologicalSensorPrecision']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalSensorSamplingFrequency']:
										if not v.validate({'physiologicalSensorSamplingFrequency':detail_data[MatchedColumns['physiologicalSensorSamplingFrequency']]}):
											error_list.append({'Label':'Physiological Sensor Sampling Frequency','key':'physiologicalSensorSamplingFrequency','message':' '.join(map(str, v.errors['physiologicalSensorSamplingFrequency']))})
										else:
											pass     
								
								elif f == MatchedColumns['physiologicalSensorDutyCycling']:
										if not v.validate({'physiologicalSensorDutyCycling':detail_data[MatchedColumns['physiologicalSensorDutyCycling']]}):
											error_list.append({'Label':'Physiological Sensor Duty Cycling','key':'physiologicalSensorDutyCycling','message':' '.join(map(str, v.errors['physiologicalSensorDutyCycling']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalSensorCalibrationDate']:
										if not v.validate({'physiologicalSensorCalibrationDate':detail_data[MatchedColumns['physiologicalSensorCalibrationDate']]}):
											error_list.append({'Label':'Physiological Sensor Calibration Date','key':'physiologicalSensorCalibrationDate','message':' '.join(map(str, v.errors['physiologicalSensorCalibrationDate']))})
										else:
											pass
								
								elif f == MatchedColumns['physiologicalSensorCalibrationDetails']:
										if not v.validate({'physiologicalSensorCalibrationDetails':detail_data[MatchedColumns['physiologicalSensorCalibrationDetails']]}):
											error_list.append({'Label':'Physiological Sensor Calibration Details','key':'physiologicalSensorCalibrationDetails','message':' '.join(map(str, v.errors['physiologicalSensorCalibrationDetails']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometrySensorManufacturer']:
										if not v.validate({'accelerometrySensorManufacturer':detail_data[MatchedColumns['accelerometrySensorManufacturer']]}):
											error_list.append({'Label':'Accelerometry Sensor Manufacturer','key':'accelerometrySensorManufacturer','message':' '.join(map(str, v.errors['accelerometrySensorManufacturer']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometrySensorModel']:
										if not v.validate({'accelerometrySensorModel':detail_data[MatchedColumns['accelerometrySensorModel']]}):
											error_list.append({'Label':'Accelerometry Sensor Model','key':'accelerometrySensorModel','message':' '.join(map(str, v.errors['accelerometrySensorModel']))})
										else:
											pass
								
								elif f == MatchedColumns['axes']:
										if not v.validate({'axes':detail_data[MatchedColumns['axes']]}):
											error_list.append({'Label':'Axes','key':'axes','message':' '.join(map(str, v.errors['axes']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometrySensorUnitsReported']:
										if not v.validate({'accelerometrySensorUnitsReported':detail_data[MatchedColumns['accelerometrySensorUnitsReported']]}):
											error_list.append({'Label':'Accelerometry Sensor Units Reported','key':'accelerometrySensorUnitsReported','message':' '.join(map(str, v.errors['accelerometrySensorUnitsReported']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometryLowerSensorDetectionLimit']:
										if not v.validate({'accelerometryLowerSensorDetectionLimit':detail_data[MatchedColumns['accelerometryLowerSensorDetectionLimit']]}):
											error_list.append({'Label':'Accelerometry Lower Sensor Detection Limit','key':'accelerometryLowerSensorDetectionLimit','message':' '.join(map(str, v.errors['accelerometryLowerSensorDetectionLimit']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometryUpperSensorDetectionLimit']:
										if not v.validate({'accelerometryUpperSensorDetectionLimit':detail_data[MatchedColumns['accelerometryUpperSensorDetectionLimit']]}):
											error_list.append({'Label':'Accelerometry Upper Sensor Detection Limit','key':'accelerometryUpperSensorDetectionLimit','message':' '.join(map(str, v.errors['accelerometryUpperSensorDetectionLimit']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometrySensorPrecision']:
										if not v.validate({'accelerometrySensorPrecision':detail_data[MatchedColumns['accelerometrySensorPrecision']]}):
											error_list.append({'Label':'Accelerometry Sensor Precision','key':'accelerometrySensorPrecision','message':' '.join(map(str, v.errors['accelerometrySensorPrecision']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometrySensorSamplingFrequency']:
										if not v.validate({'accelerometrySensorSamplingFrequency':detail_data[MatchedColumns['accelerometrySensorSamplingFrequency']]}):
											error_list.append({'Label':'Accelerometry Sensor Sampling Frequency','key':'accelerometrySensorSamplingFrequency','message':' '.join(map(str, v.errors['accelerometrySensorSamplingFrequency']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometrySensorDutyCycling']:
										if not v.validate({'accelerometrySensorDutyCycling':detail_data[MatchedColumns['accelerometrySensorDutyCycling']]}):
											error_list.append({'Label':'Accelerometry Sensor Duty Cycling','key':'accelerometrySensorDutyCycling','message':' '.join(map(str, v.errors['accelerometrySensorDutyCycling']))})
										else:
											pass
								
								elif f == MatchedColumns['accelerometrySensorCalibrationDate']:
										if not v.validate({'accelerometrySensorCalibrationDate':detail_data[MatchedColumns['accelerometrySensorCalibrationDate']]}):
											error_list.append({'Label':'Accelerometry Sensor Calibration Date','key':'accelerometrySensorCalibrationDate','message':' '.join(map(str, v.errors['accelerometrySensorCalibrationDate']))})
										else:
											pass
								
								elif  f ==  MatchedColumns['accelerometrySensorCalibrationDetails']:
										if not v.validate({'accelerometrySensorCalibrationDetails':detail_data[MatchedColumns['accelerometrySensorCalibrationDetails']]}):
											error_list.append({'Label':'Accelerometry Sensor Calibration Details','key':'accelerometrySensorCalibrationDetails','message':' '.join(map(str, v.errors['accelerometrySensorCalibrationDetails']))})
										else:
											pass

						row_data_list.append({**detail_data, **{'errors':error_list}})
			except:
				raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched') 
	
		elif request_data['csv_type'] == 'Input Data':
			v=Validator(InputDataSchema)
			row_data_list=[]
			CsvFileData.objects.filter(upload_identifier=request_data['upload_identifier']).filter(csv_type=request_data['csv_type']).update(matchedcolums=request_data['MatchedColumns'])
			CsvFileData.objects.filter(upload_identifier=request_data['upload_identifier']).update(fileuploadstatus_id=get_object_or_404(FileUploadStatus,id=request_data['fileuploadstatus_id']))
			row_count=0
			no_error_row_count=0
			get_file_instance=get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type=request_data['csv_type'])

			try:
				import requests
				r = requests.get(get_file_instance.csv_file.url)
				with open("media/"+str(get_file_instance.csv_file),'wb') as f:
					f.write(r.content)
				with open('media/'+str(get_file_instance.csv_file), 'r', newline='', encoding='ISO-8859-1') as file:
					csvreader = csv.reader(file)
					header = next(csvreader)
					# print(header)
					MatchedColumns=request_data['MatchedColumns']
					if not len(set(list(MatchedColumns.values()))) == len(header):
						raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched')
					for row in csvreader:

						row_count=row_count+1
						error_list=[]
						detail_data=dict(zip(header,row))
						if request_data['csv_type'] == 'Input Data':
							for f in header:
									if f == MatchedColumns['instrumentID']:
										if not v.validate({'instrumentID':detail_data[MatchedColumns['instrumentID']]}):
											error_list.append({'Label':'Instrument ID','key':'instrumentID','message':' '.join(map(str, v.errors['instrumentID']))})
										else:
											pass
									
									elif f == MatchedColumns['deploymentID']:
										deployment_unique_values_list.append(detail_data[MatchedColumns['deploymentID']])
										if not v.validate({'deploymentID':detail_data[MatchedColumns['deploymentID']]}):
											error_list.append({'Label':'Deployment ID','key':'deploymentID','message': ' '.join(map(str, v.errors['deploymentID']))})
										elif InputData.objects.filter(deploymentID=detail_data[MatchedColumns['deploymentID']]).filter(~Q(upload_identifier=request_data['upload_identifier'])).exists():
											error_list.append({'Label':'Deployment ID','key':'deploymentID','message': f"Field '{f}' expected Unique Alphanumeric but '{detail_data[MatchedColumns['deploymentID']]}' already exists"})
										else:
											pass
									
									elif f == MatchedColumns['organismID']:
										organism_unique_values_list.append(detail_data[MatchedColumns['organismID']])
										if not v.validate({'organismID':detail_data[MatchedColumns['organismID']]}):
											error_list.append({'Label':'Organism ID','key':'organismID','message': ' '.join(map(str, v.errors['organismID']))})
										elif InputData.objects.filter(organismID=detail_data[MatchedColumns['organismID']]).filter(~Q(upload_identifier=request_data['upload_identifier'])).exists():
											error_list.append({'Label':'Organism ID','key':'deploymentID','message': f"Field '{f}' expected Unique Alphanumeric but '{detail_data[MatchedColumns['organismID']]}' already exists"})
										else:
											pass
									
									elif f == MatchedColumns['organismIDSource']:
										if not v.validate({'organismIDSource':detail_data[MatchedColumns['organismIDSource']]}):
											error_list.append({'Label':'Organism IDSource','key':'organismIDSource','message': ' '.join(map(str, v.errors['organismIDSource']))})
										else:
											pass
									
									elif f == MatchedColumns['time']:
										if not v.validate({'time':detail_data[MatchedColumns['time']]}):# HH:MM[:ss[.uuuuuu]][TZ]
											error_list.append({'Label':'Time','key':'time','message': ' '.join(map(str, v.errors['time']))})
										else:
											pass
									
									elif f == MatchedColumns['latitude']:
										if not v.validate({'latitude':detail_data[MatchedColumns['latitude']]}):
											error_list.append({'Label':'Latitude','key':'latitude','message': ' '.join(map(str, v.errors['latitude']))})
										else:
											pass
									
									elif f == MatchedColumns['longitude']:
										if not v.validate({'longitude':detail_data[MatchedColumns['longitude']]}):
											error_list.append({'Label':'longitude','key':'longitude','message': ' '.join(map(str, v.errors['longitude']))})
										else:
											pass
									
									elif f == MatchedColumns['argosLC']:
										if not v.validate({'argosLC':detail_data[MatchedColumns['argosLC']]}):
											error_list.append({'Label':'Argos LC','key':'argosLC','message': ' '.join(map(str, v.errors['argosLC']))})
										else:
											pass
									
									elif f == MatchedColumns['argosErrorRadius']:
										if not v.validate({'argosErrorRadius':detail_data[MatchedColumns['argosErrorRadius']]}):
											error_list.append({'Label':'Argos ErrorRadius','key':'argosErrorRadius','message': ' '.join(map(str, v.errors['argosErrorRadius']))})	
										else:
											pass
									
									elif f == MatchedColumns['argosSemiMajor']:
										if not v.validate({'argosSemiMajor':detail_data[MatchedColumns['argosSemiMajor']]}):
											error_list.append({'Label':'Argos SemiMajor','key':'argosSemiMajor','message': ' '.join(map(str, v.errors['argosSemiMajor']))})
										else:
											pass
									
									elif f == MatchedColumns['argosSemiMinor']:
										if not v.validate({'argosSemiMinor':detail_data[MatchedColumns['argosSemiMinor']]}):
											error_list.append({'Label':'Argos SemiMinor','key':'argosSemiMinor','message': ' '.join(map(str, v.errors['argosSemiMinor']))})
										else:
											pass
									
									elif f == MatchedColumns['argosOrientation']:
										if not v.validate({'argosOrientation':detail_data[MatchedColumns['argosOrientation']]}):
											error_list.append({'Label':'Argos Orientation','key':'argosOrientation','message': ' '.join(map(str, v.errors['argosOrientation']))})
										else:
											pass
									
									elif f == MatchedColumns['argosGDOP']:
										if not v.validate({'argosGDOP':detail_data[MatchedColumns['argosGDOP']]}):
											error_list.append({'Label':'Argos GDOP','key':'argosGDOP','message': ' '.join(map(str, v.errors['argosGDOP']))})
										else:
											pass
									
									elif f == MatchedColumns['gpsSatelliteCount']:
										if not v.validate({'gpsSatelliteCount':detail_data[MatchedColumns['gpsSatelliteCount']]}):
											error_list.append({'Label':'Gps Satellite Count','key':'gpsSatelliteCount','message': ' '.join(map(str, v.errors['gpsSatelliteCount']))})
										else:
											pass
									
									elif f == MatchedColumns['residualsGPS(rapid acquisition GPS)']:
										if not v.validate({'residualsGPS(rapid acquisition GPS)':detail_data[MatchedColumns['residualsGPS(rapid acquisition GPS)']]}):
											error_list.append({'Label':'Residuals GPS (Rapid Acquisition GPS','key':'residualsGPS(rapid acquisition GPS)','message': ' '.join(map(str, v.errors['residualsGPS(rapid acquisition GPS)']))})
										else:
											pass
									
									elif f == MatchedColumns['temperatureGLS']:
										if not v.validate({'temperatureGLS':detail_data[MatchedColumns['temperatureGLS']]}):
											error_list.append({'Label':'Temperature GLS','key':'temperatureGLS','message': ' '.join(map(str, v.errors['temperatureGLS']))})
										else:
											pass
									
									elif f == MatchedColumns['depthGLS']:
										if not v.validate({'depthGLS':detail_data[MatchedColumns['depthGLS']]}):
											error_list.append({'Label':'Depth GLS','key':'depthGLS','message': ' '.join(map(str, v.errors['depthGLS']))})
										else:
											pass								
									elif  f ==  MatchedColumns['sensorIType']:
										if not v.validate({'sensorIType':detail_data[MatchedColumns['sensorIType']]}):
											error_list.append({'Label':'Sensor IType','key':'sensorIType','message': ' '.join(map(str, v.errors['sensorIType']))})
										else:
											pass
										
									elif f == MatchedColumns['sensorIMeasurement']: 
										if not v.validate({'sensorIMeasurement':detail_data[MatchedColumns['sensorIMeasurement']]}):
											error_list.append({'Label':'Sensor IMeasurement','key':'sensorIMeasurement','message': ' '.join(map(str, v.errors['sensorIMeasurement']))})
										else:
											pass
							row_data_list.append({**detail_data, **{'errors':error_list}})
			
			except:
				raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched') 

		for data in row_data_list:
			if len(data['errors']) == 0:
				no_error_row_count+=1
		if no_error_row_count == row_count:
			serializer.save()
		file_headers=get_object_or_404(CsvFileHeaders,csv_file_type=request_data['csv_type'])
		fileheaders=eval(file_headers.csv_file_headers)
		# initializing list 
			
		deployment_flag = 0
		organism_flag = 0
		# to check all unique list elements
		for i in range(len(organism_unique_values_list)):
			for i1 in range(len(organism_unique_values_list)):
						if i != i1:
							if organism_unique_values_list[i] == organism_unique_values_list[i1]:
								organism_flag = 1
		for i in range(len(deployment_unique_values_list)):
			for i1 in range(len(deployment_unique_values_list)):
				if i != i1:
					if deployment_unique_values_list[i] == deployment_unique_values_list[i1]:
						deployment_flag = 1
		if(deployment_flag):
				error_list.append({"Deployment_ID":"Deployment ID does not contains all unique values in file."})
		if(organism_flag):
				error_list.append({"Organism_ID":"Organism ID does not contains all unique values in file."})
		return Response({'status':True,'Headers':fileheaders,'Data':row_data_list,'error_summary':error_list},status=status.HTTP_200_OK,)


class ReUploadView(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = ReUploadSerializer
	def patch(self,request):
		serializer = self.serializer_class(data=request.data)
		request_data=request.data
		if request_data['csv_type'] == "Deployment MetaData" or request_data['csv_type'] == 'Device MetaData' or request_data['csv_type'] == 'Input Data':
			file_obj=get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type=request_data['csv_type'])
		else:
			raise serializers.ValidationError({'wrong_csv_type': "wrong_csv_type "},code='wrong_csv_type')
		serializer = ReUploadSerializer(file_obj, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		instance= get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type=request_data['csv_type'])
		# for data in CsvFileData.objects.filter(upload_identifier=data['upload_identifier']):

			# instance=get_object_or_404(CsvFileData,id=data.id)
		import os
		if os.path.exists("media/"+str(instance.csv_file)):
			os.remove("media/"+str(instance.csv_file))
		msg=js['csv_file_uploaded_successfully']
		return Response({'status':True,'message':msg,}, status=status.HTTP_200_OK)


			
class licenseView(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get(self,request):
		get_license=(licenseSerializer((License.objects.all()), many=True)).data
		return Response({'License':get_license}, status=status.HTTP_200_OK)

class MapView(LoggingMixin,APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get(self, request, *args, **kwargs):
		get_map=MapSerializer((InputData.objects.filter(upload_identifier=kwargs['upload_identifier'])),many=True).data
		return Response({'data_coordinates ':get_map}, status=status.HTTP_200_OK)

class PostFilelicenseView(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = PostFilelicenseSerializer
	def post(self,request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({'status':True,'message':'Data uploaded successfully'},status=status.HTTP_200_OK)


#=======================================================Draft APIs Start================================================
class DraftView(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get(self,request):
		get_drafts=(DraftSerializer((CsvFileData.objects.filter(created_by=request.user).filter(csv_type='Input Data').filter(~Q(fileuploadstatus_id=8))), many=True)).data
		return Response({'status':True,'Drafts':get_drafts}, status=status.HTTP_200_OK)

class DraftDetailsView(LoggingMixin,generics.GenericAPIView):
	serializer_class = DraftDetailsSerializer
	permission_classes = (permissions.IsAuthenticated,)
	def post(self,request):
		get_deployment_file_data=None
		get_device_file_instance=None
		get_device_file_data=None
		get_input_file_data=None
		get_input_file_instance=None
		request_data = request.data
		serializer = self.serializer_class(data=request_data)
		serializer.is_valid(raise_exception=True)
		if (request_data['fileuploadstatus_id']) == 1:
			get_deployment_file_instance=None
		elif (request_data['fileuploadstatus_id']) == 2:
			get_deployment_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Deployment MetaData')).matchedcolums
		elif (request_data['fileuploadstatus_id']) == 3:
			get_deployment_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Deployment MetaData')).matchedcolums
			get_deployment_file_data=DeploymentMetadataSerializer(DeploymentMetadata.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
		elif (request_data['fileuploadstatus_id']) == 4:
			get_deployment_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Deployment MetaData')).matchedcolums
			get_deployment_file_data=DeploymentMetadataSerializer(DeploymentMetadata.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
			get_device_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Device MetaData')).matchedcolums
		elif (request_data['fileuploadstatus_id']) == 5:
			get_deployment_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Deployment MetaData')).matchedcolums
			get_deployment_file_data=DeploymentMetadataSerializer(DeploymentMetadata.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
			get_device_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Device MetaData')).matchedcolums
			get_device_file_data=DeviceMetadataSerializer(DeviceMetaData.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
		elif (request_data['fileuploadstatus_id']) == 6:
			get_deployment_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Deployment MetaData')).matchedcolums
			get_deployment_file_data=DeploymentMetadataSerializer(DeploymentMetadata.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
			get_device_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Device MetaData')).matchedcolums
			get_device_file_data=DeviceMetadataSerializer(DeviceMetaData.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
			get_input_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Input Data')).matchedcolums
		elif (request_data['fileuploadstatus_id']) == 7:
			get_deployment_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Deployment MetaData')).matchedcolums
			get_deployment_file_data=DeploymentMetadataSerializer(DeploymentMetadata.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
			get_device_file_instance=get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Device MetaData').matchedcolums
			get_device_file_data=DeviceMetadataSerializer(DeviceMetaData.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
			get_input_file_instance=(get_object_or_404(CsvFileData,upload_identifier=request_data['upload_identifier'],csv_type='Input Data')).matchedcolums
			get_input_file_data=InputdataSerializer(InputData.objects.filter(upload_identifier=request_data['upload_identifier']),many=True).data
		return Response( {'status':True,'DeploymentMetaData_matchedcolums':(get_deployment_file_instance),'DeploymentMetaData_FileData':get_deployment_file_data,
		'DeviceMetaData_matchedcolums': get_device_file_instance,'DeviceMetaData_FileData':get_device_file_data,
		'InputData_matchedcolums':get_input_file_instance,'InputData_FileData':get_input_file_data},status=status.HTTP_200_OK)



class DraftDiscardView(LoggingMixin,generics.GenericAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	# serializer_class = DraftDiscardSerializer
	def delete(self,request,upload_identifier):
		if CsvFileData.objects.filter(created_by=request.user).filter(upload_identifier=upload_identifier).exists():
			(CsvFileData.objects.filter(created_by=request.user).filter(upload_identifier=upload_identifier)).delete()
			if DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).exists():
				(DeploymentMetadata.objects.filter(upload_identifier=upload_identifier)).delete()
			if DeviceMetaData.objects.filter(upload_identifier=upload_identifier).exists():
				(DeviceMetaData.objects.filter(upload_identifier=upload_identifier)).delete()
			if InputData.objects.filter(upload_identifier=upload_identifier).exists():
				(InputData.objects.filter(upload_identifier=upload_identifier)).delete()
			return Response({'status':True,'msg':'Succesfully Deleted'}, status=status.HTTP_200_OK)
		else:
			return Response({'status':False,'msg':'upload_identifier does not exists'}, status=status.HTTP_200_OK)
#========================================================================================================================