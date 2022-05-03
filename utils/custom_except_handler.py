from rest_framework.views import exception_handler
from django.http import Http404
from utils.response_utils import UWAErrorResponse, UWAResponse
from uwa.settings import js


def custom_exception_handler(exc, context=None):
	response = exception_handler(exc, context)
	fields=None   
	message=None
	print('exc:===',type(exc))
	print('exc:===',(exc))
	if str(type(exc)) == "<class 'django.http.response.Http404'>":
		return UWAErrorResponse(status=response.status_code, error_message=str(exc), resp_data=fields)
	elif str(type(exc)) == "<class 'binascii.Error'>":
		return UWAErrorResponse( error_message=str(exc), resp_data='csv_file')
	elif str(type(exc)) == "<class 'pandas.errors.ParserError'>":
		return UWAErrorResponse( error_message=str(exc), resp_data='csv_file')
	elif str(type(exc)) == "<class 'KeyError'>":
		return UWAErrorResponse( error_message='Key error '+ str(exc), resp_data='csv_file')	

	required=[]
	unique=[]
	does_not_exist=[]
	invalid_email=[]
	password_len=[]
	blank=[]
	error_message=exc.get_codes()
	print('error_message========',(error_message),type((error_message)))
	if isinstance(error_message, dict):
		print("in")
		for k, v in error_message.items():
			print(v,k)
			if v == ["required"]:
				required.append(''.join([str(elem) for elem in k]))
			elif v == ['unique']:
				unique.append(''.join([str(elem) for elem in k]))
			elif v ==  ['does_not_exist'] :
				does_not_exist.append(''.join([str(elem) for elem in k]))
			elif v ==  ['invalid'] and 'email' == k:
				invalid_email.append(''.join([str(elem) for elem in k]))
			elif v == ['file_extension'] and 'error' == k :
				message=(exc.detail)
				message=message['error']
				message=' '.join([str(elem) for elem in message])
				# message=str(message)[2:-2]
				fields='file field'
			elif v == ['invalid'] and 'error' == k :
				message=(exc.detail)
				message=message['error']
				message=' '.join([str(elem) for elem in message])
				message=str(message)[2:-2]
				fields='Password'
			elif v ==  ['invalid_choice'] and 'country' == k:
				message=js['country_validation']
				fields='country'
			elif v ==  ['invalid'] and 'password' == k:
				message=js['password_mismatch']
				fields='Password','Confirm_Password'
			elif  (k ==  'password' or k == 'Confirm_Password') and ['min_length'] == v:
				password_len.append(''.join([str(elem) for elem in k]))
			elif k == 'detail' and v =='token_not_valid':
					message=js['token_not_valid']
			elif v == ['invalid_image'] and k == 'profile_image':
						message=js['vaild_profile_img']
						fields='profile_image'
			elif v == ['empty'] and k == 'profile_image':
				message=js['vaild_profile_img']
				fields='profile_image'
			elif v == ['blank'] and k == 'password':
				blank.append(''.join([str(elem) for elem in k]))
			elif v == ['blank'] and k == 'email' :
				blank.append(''.join([str(elem) for elem in k]))
			elif v == ['invalid'] and k == 'is_terms_conditions':
				message=js['invalid_terms_conditions']
				fields='is_terms_conditions'
			elif v == ['blank'] and k == 'refresh_token':
				message=js['blank_refresh_token']
				fields='refresh_token'

			elif v == ['not a csv file'] and k == 'csv_file':
				message=js['Unsupported file extension. File should be CSV']
				fields='csv file'
			# elif v == ['file_size'] and k == 'csv_file':
			# 	message=js['File should be not more than 5MB']
			# 	fields='csv file'
			elif v == ['upload_identifier'] and k == 'upload_identifier':
				message=js['upload_identifier_does_not_exist']
				fields='upload_identifier'
			elif v == 'upload_identifier' and k == 'upload_identifier':
				message=js['upload_identifier_does_not_exist']
				fields='upload_identifier'
			elif v == ['csv_type'] and k == 'csv_type':
				message=js['Csv_type_does_not_exist']
				fields='csv type'
			elif v == 'csv_type' and k == 'csv_type':
				message=js['Csv_type_does_not_exist']
				fields='csv type'
			elif v == 'column_mismatched' and k == 'column_mismatched':
				message='columns mismatched'
				fields='csv file columns'
			
			elif v == ['licence_type_id'] and k == 'licence_type_id':
				message='licence id does not exist'
				fields='licence_type_id'
			
			elif v == 'blank_files_array' and k == 'blank_files_array':
				message=js['blank_files_array']
				fields='files'
			# elif k=='files' and v == [{'assign_name': ['required']}, {} ,{}]:
			# 	message='assign name field is required'
			# 	fields='assign_name'
			# elif k=='files' and v == [{'assign_name': ['required']}, {} ]:
			# 	message='assign name field is required'
			# 	fields='assign_name'
			# elif k=='files' and v == [{'assign_name': ['required']} ]:
			# 	message='assign name field is required'
			# 	fields='assign_name'
			elif k=='files' :
				# print(v)
				for data in v:
					
					for key in data.keys():
						print(key)
						if key == 'assign_name':
							if data['assign_name'] == ['required']:
								message=js['required_field']
								fields='assign_name  in files'
							elif data['assign_name'] == ['blank']:
								message=js['required_field']
								fields='assign_name in files'
						elif key == 'csv_type':
							if data['csv_type'] == ['required']:
								message=js['required_field']
								fields='csv_type in files'
							elif data['csv_type'] == ['blank']:
								message=js['required_field']
								fields='csv_type in files'
						elif key == 'csv_file':
							if data['csv_file'] == ['required']:
								message=js['csv_file_not_submit']
								fields='csv_file in files'
							elif data['csv_file'] == ['blank']:
								message=js['csv_file_not_submit']
								fields='csv_file in files'
							elif data['csv_file'] == ['not_csv_file']:
								message=js['not_csv_file']
								fields='csv_file in files'
							elif data['csv_file'] == ['more_than_five_mb']:
								message=js['more_than_five_mb']
								fields='csv_file in files'
							elif data['csv_file'] == ['more_than_fifteen_mb']:
								message=js['more_than_fifteen_mb']
								fields='csv_file in files'


						elif key == 'created_by':
							if data['created_by'] == ['does_not_exist']:
								message=js['wrong_created_by']
								fields='created_by in files'
						elif key == 'fileuploadstatus_id':
							if data['fileuploadstatus_id'] == ['does_not_exist']:
								message=js['wrong_fileuploadstatus_id']
								fields='fileuploadstatus_id in files'
						elif key == 'wrong_csv_type':
							if data['wrong_csv_type'] == ['wrong_csv_type']:
								message=js['wrong_csv_type']
								fields='csv_type in files'
						# elif key == 'not_csv_file':


						# else:
						# 	message=exc.detail
						# 	fields='files'

				
			elif k=='authors':
				print(v)
				for data in v:
					for key in data.keys():
						if key == 'institution_id':
							if data['institution_id'] == ['does_not_exist']:
								message="Invalid pk \"0\" - object does not exist."
								fields='institution_id in authors'
							elif data['institution_id'] == ['required']:
								message="This field is required."
								fields='institution_id in authors'
						elif key == 'created_by':
							if data['created_by'] == ['does_not_exist']:
								message="Invalid pk \"0\" - object does not exist."
								fields='created_by in authors'
							elif data['created_by'] == ['required']:
								message="This field is required."
								fields='created_by in authors'
						elif key == 'author_email':
							if data['author_email'] == ['required']:
								message="This field is required."
								fields='author_email in authors'
						elif key == 'author_name':
							if data['author_name'] == ['required']:
								message="This field is required."
								fields='author_name in authors'

						else:
							message=exc.detail
							fields='authors'
			elif v == ['MatchedColumns'] and k == 'MatchedColumns':
					message="This field is required."
					fields='MatchedColumns'
			elif v == ['csv_file_validation_error'] and k == 'csv_file_validation_message':
					message=exc.detail
					fields='MatchedColumns'

			elif v == 'wrong_csv_type' and k == 'wrong_csv_type':
					message=js['wrong_csv_type']
					fields='csv_type'

	elif isinstance(error_message, str):
		exc=str(exc)
		if 'parse_error' == error_message:
			message=js['other_error']
			
		elif exc == 'Email is not verified':
			message=js['email_not_verified']
			fields='email'
		elif exc == "Invalid credentials, try again":
			message=js['invalid_email_or_pass']
			fields='email or password'
		elif error_message == 'unsupported_media_type':
			message=js['vaild_profile_img']
			
		elif error_message == 'invalid_reset_link' :
			message=js['invalid_reset_link']
			
		elif 'authentication_failed' == error_message:
			message='authentication_failed'
			
		elif 'not_authenticated' == error_message:
			message=js['not_authenticated']


		else:
			message=error_message
	elif error_message == ['logout_bad_token']:
			message=js['logout_bad_token']
			fields='refresh_token'
	elif error_message == ['less_columns']:
			message=js['less_columns']
			fields=None
			
	else:
		message=error_message
	if required :
		fields=' ,'.join(map(str, required))
		message=js['user_required_fields']
		return UWAErrorResponse(status=response.status_code, error_message=message, resp_data=fields)
	elif invalid_email:
		fields=' ,'.join(map(str, invalid_email))
		message=js['invalid_email']
		return UWAErrorResponse(status=response.status_code, error_message=message, resp_data=fields)
	elif unique :
		fields=None
		message=js['user_already_exists']
		return UWAErrorResponse(status=response.status_code, error_message=message, resp_data=fields)
	elif does_not_exist:
		fields=' ,'.join(map(str, does_not_exist))
		message=js['institution_id']
		return UWAErrorResponse(status=response.status_code, error_message=message, resp_data=fields)

	elif blank:
		message=js['blank']
		fields=' ,'.join(map(str, blank))
	elif password_len:
		message=js['password_length']
		fields=' ,'.join(map(str, password_len))

	if response is not None:
		if response.status_code != 200 or response.status_code != 201 or \
				isinstance(exc, (UWAErrorResponse, UWAResponse)) is False:
			return UWAErrorResponse(status=response.status_code, error_message=message, resp_data=fields)
		 
	return response
