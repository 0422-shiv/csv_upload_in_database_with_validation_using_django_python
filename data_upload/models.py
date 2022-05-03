from utils.models import BaseModel
from django.db import models
from accounts.models import Institutions

class License(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    explanation=models.TextField()

    def __str__(self):
        return str(self.name)


class FileUploadStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status=models.IntegerField(null=True,blank=True)
    def __str__(self):
        return str(self.status)

class CsvFileHeaders(models.Model):
    id = models.AutoField(primary_key=True)
    csv_file_type=models.CharField(max_length=20)
    csv_file_headers=models.TextField()
    def __str__(self):
        return str(self.csv_file_type)



class CoAuthors(BaseModel):
    id = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=75)
    author_email = models.EmailField(max_length=255, db_index=True)
    institution_id = models.ForeignKey(Institutions, on_delete=models.PROTECT, db_column='institution_id')
    upload_identifier = models.CharField(max_length=20,default=None,null=True,blank=True)
    def __str__(self):
        return str(self.author_name)
    

class CsvFileData(BaseModel):
    id = models.AutoField(primary_key=True)
    assign_name = models.CharField(max_length=20)
    csv_type = models.CharField(max_length=20,default=None)
    upload_identifier = models.CharField(max_length=20,default=None,null=True,blank=True)
    csv_file=models.FileField(upload_to="csv_files", max_length=254)
    matchedcolums=models.JSONField(null=True,blank=True)
    licence_type_id=models.ForeignKey(License, on_delete=models.PROTECT,null=True,blank=True,related_name='licence_type')
    fileuploadstatus_id = models.ForeignKey(FileUploadStatus, on_delete=models.PROTECT, db_column='File Upload Status', default=None,null=True,blank=True,related_name='FileUploadStatus')

    def __str__(self):
        return str(self.csv_file)


class DeploymentMetadata(models.Model):
    id = models.AutoField(primary_key=True)
    upload_identifier = models.CharField(max_length=20,default=None,null=True,blank=True)
    deployment_id =models.CharField(max_length=15,unique=True)# ID  of DeploymentDataCalibration Table
    instrumentID  = models.CharField(max_length=50,default=None)
    ptt=models.BigIntegerField(default=None) #Platform Transmitter Terminal for Argos transmission,e.g. “178937”
    transmission_settings =models.IntegerField(default=None,null=True,blank=True)#Step duration and location uplink limit (can add rows if needed)     String with duration in hours, followed by number of messages e.g. “24 hours, 200 messages”
    transmission_mode = models.IntegerField(default=None,null=True,blank=True)#User-defined conditions for entering and exiting power-saving mode (i.e. slower sampling rate) and transmission control, if applicable. Time settings in minutes e.g. “Haul-Out state entered after 10 consecutive dry minutes (40 seconds/minute), exited if wet for 30 seconds/minute” OR “disabled”
    duty_cycle = models.CharField(max_length=100,default=None,null=True,blank=True)#Detailed instrument settings defined in a file (e.g. Wildlife Computers Report, htm file/URL, or screenshot of tag settings), e.g. "PTT active 12 hours, followed by 6 hours sleep-mode"
    instrument_settings  = models.CharField(max_length=254,null=True,blank=True)#Attach a file with detailed instrument settings (eg. Wildlife Computers Report .htm file or screenshot of tag settings).
    #Movement metadata
    deployment_datetime  = models.DateTimeField(default=None,null=True,blank=True)#Timestamp the instrument was deployed on the organism.
    deployment_latitude  = models.DecimalField(max_digits=22, decimal_places=16,default=None)#Latitude in decimal degrees of instrument deployment.Decimal degrees north, -90.0000 to 90.0000
    deployment_longitude = models.DecimalField(max_digits=22, decimal_places=16,default=None)#Longitude in decimal degrees of instrument deployment.Decimal degrees east, -180.0000 to 180.0000
    deployment_end_type = models .CharField(max_length=30,default=None,null=True,blank=True)#Classification of instrument deployment end, i.e. what ended the collection of usable data, which may or may not be tag removal.(e.g. removal, equipment failure, fall off)
    detachment_datetime = models.DateTimeField(default=None,null=True,blank=True)#Timestamp the instrument was recovered or otherwise detached from the organism (if known).
    detachment_details = models.CharField(max_length=100,default=None,null=True,blank=True)#Brief description of recovery/detachment if known (e.g., caught in fisheries, recaptured animal, predetermined detachment)
    detachment_latitude  = models.DecimalField(max_digits=22, decimal_places=16,default=None,null=True,blank=True)#Latitude in decimal degrees of instrument recovery/detachment from organism (if known).
    detachment_longitude = models.DecimalField(max_digits=22, decimal_places=16,default=None,null=True,blank=True)#Longitude in decimal degrees of instrument recovery/detachment from organism (if known).
    track_start_time = models.DateTimeField(default=None,null=True,blank=True)#Timestamp at which organism track starts if different from deployment time.
    track_start_latitude = models.DecimalField(max_digits=22, decimal_places=16,default=None)#Latitude at which track of organism begins (may or may not be different from deployment latitude)
    track_start_longitude = models.DecimalField(max_digits=22, decimal_places=16,default=None)#Longitude at which track of organism begins (may or may not be different from deployment longitude).
    track_end_time = models.DateTimeField(default=None,null=True,blank=True)#Timestamp at which track of organism ends.
    track_end_latitude = models.DecimalField(max_digits=22, decimal_places=16,default=None)#Latitude at which organism track ends.
    track_end_longitude = models.DecimalField(max_digits=22, decimal_places=16,default=None)#    Longitude at which organism track ends.
    sun_elevation_angle = models.FloatField(default=None)#Angle of the sun to determine twilight derived at the beginning of deployment.
    argos_filter_method =models.CharField(max_length=50,default=None)#Filter method implemented by CLS/Argos to generate location.
    #Organism metadata
    organismid = models.CharField(max_length=30,default=None)#identifier for an individual, link data from different deployments or instruments on the same animal.
    scientific_name = models.CharField(max_length=100,default=None)#Binomial species name of organism carrying instrument.
    scientific_name_source =models.TextField(default=None,null=True,blank=True)#URN denoting the authority from which the species identification is defined
    common_name = models.TextField(default=None)#One or more common name(s) of organism carrying instrument.
    organism_sex =models.CharField(max_length=1,default=None)#Sex of organism carrying instrument.
    organism_weight_at_deployment = models.FloatField(default=None,null=True,blank=True)#Weight of organism carrying instrument measured at tag deployment.
    organism_weight_remeasurement = models.FloatField(default=None,null=True,blank=True)#Weight of organism carrying instrument at another time (specified in "Organism weight re-measurement time") than deployment
    organism_weight_remeasurement_time  =models.DateTimeField(default=None,null=True,blank=True)#imestamp when the additional measurement of organism weight was taken.
    organism_size =models.FloatField(default=None,null=True,blank=True)#Size of organism carrying instrument (can be repeated for up to three measurements).
    organism_size_measurement_type =models.CharField(max_length=20,default=None,null=True,blank=True)#Type of method used for size measurement reported.
    organism_size_measurement_description = models.CharField(max_length=150,default=None,null=True,blank=True)#Description of method used for size measurement reported.
    organism_size_measurement_time = models.DateTimeField(default=None,null=True,blank=True)#Timestamp when the organism size measurement was taken.
    organism_age_reproductive_class = models.CharField(max_length=20,default=None,null=True,blank=True)#Age class of organism carrying instrument at the time the instrument was attached.
    trapping_method_details  = models.CharField(max_length=100,default=None,null=True,blank=True)#Method used to trap the organism for instrumentation, or to deploy the instrument without trapping.
    attachment_method = models.CharField(max_length=20,default=None)#Method with which instrument was attached.
    #Environmental data calibration
    environmental_calibrations_done = models.URLField(max_length=200,default=None,null=True,blank=True)#Provide link to calibration file.
    environmental_qc_done = models.BooleanField(default=False)#Whether quality control was performed.(Y/N) 
    environmental_qc_problems_found = models.BooleanField(default=False)#Whether data quality problem(s) were detected.(Y/N)
    environmental_qc_notes = models.TextField(default=None)#Description of QC done, e.g. “temperatures outside of xx range removed”, number of cases flagged.
    #Physiological data calibration
    physiological_calibrations_done = models.URLField(max_length=200,default=None,null=True,blank=True)#Provide link to calibration file.
    physiological_qc_done = models.BooleanField(default=False)#Whether quality control was performed.(Y/N) 
    physiological_qc_problems_found = models.BooleanField(default=False)#Whether data quality problem(s) were detected.(Y/N)
    physiological_qc_notes = models.TextField(default=None)#Description of QC done, e.g. “temperatures outside of xx range removed”, number of cases flagged.
    #Accelerometry data calibration
    accelerometry_position_of_accelerometer_on_organism = models.CharField(max_length=50,default=None,null=True,blank=True)#Where the accelerometer was placed on the organism, e.g. “head”
    accelerometry_orientation_of_accelerometer_on_organism =models.CharField(max_length=50,default=None,null=True,blank=True)#The orientation of the accelerometer on the organism, if applicable, e.g. “facing towards front of head”
    accelerometry_calibrations_done = models.URLField(max_length=200,default=None,null=True,blank=True)#Provide link to calibration file.
    accelerometry_qc_done = models.BooleanField(default=False,null=True,blank=True)#Whether quality control was performed.(Y/N) 
    accelerometry_qc_problems_found = models.BooleanField(default=False,null=True,blank=True)#Whether data quality problem(s) were detected.(Y/N)
    accelerometry_qc_notes = models.TextField(default=None,null=True,blank=True)#Description of QC done, e.g. “temperatures outside of xx range removed”, number of cases flagged.
    #Other data
    owner_name = models.CharField(max_length=50)
    owner_email_contact=models.EmailField(max_length=254)
    owner_institutional_contact=models.BigIntegerField()
    owner_phone_contact=models.BigIntegerField()
    license=models.CharField(max_length=150)
    other_relevent_identifier=models.CharField(max_length=100,null=True,blank=True,default=None)
    other_datatypes_associated_with_deployment=models.CharField(max_length=100,null=True,default=None,blank=True)
    references=models.URLField(max_length=200,null=True,blank=True,default=None)
    citation=models.TextField(null=True,blank=True,default=None)




class DeviceMetaData(models.Model):
    id = models.AutoField(primary_key=True)
    upload_identifier = models.CharField(max_length=20,default=None,null=True,blank=True)
    instrument_id  = models.CharField(max_length=50,default=None)
    instrument_type  = models.CharField(max_length=50,default=None)#Type of instrument deployed (e.g. archival, Argos, GSM, radio telemetry, rapid-acquisition GPS, acoustic tag, acoustic receiver)
    instrument_model_number   = models.CharField(max_length=20,default=None)#Name of specific instrument model deployed, e.g. “Mk10”
    instrument_manufacturer  = models.CharField(max_length=50,default=None)#Manufacturer of the instrument (e.g. Wildlife Computers, SMRU, Lotek, Little Leonardo)
    instrument_serial_number  = models.CharField(max_length=20,default=None)#Serial number of instrument deployed, e.g. “09A0178”
    horizontal_sensor_tracking_device = models.CharField(max_length=35,default=None)  #Type of tracking technology used (e.g. Argos, fast-acquisition GPS, GLS, acoustic)
    horizontal_sensor_uplink_Interval = models.IntegerField(default=None)  #Interval of time between two consecutive message dispatches,e.g '12'
    horizontal_sensor_uplink_interval_units = models.BigIntegerField(default=None)  #Unit of uplink interval reported in Seconds
    vertical_sensor_units_reported  = models.CharField(max_length=20,default=None)#Unit of altitude/depth reported,e.g. “meters”
    vertical_sensor_resolution = models.DecimalField(max_digits=20, decimal_places=3,default=None)#Resolution of altitude/depth measurements in same unit specified for vertical sensor, e.g. “0.1”
    vertical_lower_sensor_detection_limit = models.IntegerField(default=None)    #Lower detection limit for sensor in same unit specified for sensor,e.g. “5”
    vertical_upper_sensor_detection_limit = models.IntegerField(default=None) #  Upper detection limit for sensor in same unit specified for sensor, e.g. “2500”
    vertical_sensor_precision = models.DecimalField(max_digits=20, decimal_places=3,default=None)#Sensor precision in same unit specified for sensor,e.g. “+/- 0.01”
    vertical_sensor_sampling_frequency = models.IntegerField(default=None) #How often the sensor records a measurement in Hz
    vertical_sensor_duty_cycling = models.CharField(max_length=100,default=None) #Description of any duty cycling assigned to sensor,e.g. "records data only on deepest dive in 6 hr period"
    vertical_sensor_calibration_date = models.DateTimeField(default=None)#Date when sensor calibration was done. ISO-8601 Datetime in UTC, yyyy-MM-ddT HH:mm:ss.SSSZ, e.g. “2020-03-29T 17:56:10.000Z”
    vertical_sensor_calibration_details = models.URLField(max_length=200,default=None)#Full definition of the calibration done through addition of a link to where the data and/or methods are described (e.g. peer-reviewed publication).
    environmental_sensor_type = models.CharField(max_length=40,default=None)#Type of sensor in instrument (e.g. heart oxygen probe, blood oxygen probe).
    environmental_sensor_manufacturer =models.CharField(max_length=50,default=None)#Name of the manufacturer of the sensor (may or may not be the same as the instrument manufacturer).
    environmental_sensor_model =models.CharField(max_length=50,default=None)#Name of specific sensor model.
    environmental_sensor_units_reported  = models.CharField(max_length=20,default=None)#Unit of altitude/depth reported,e.g. “meters”
    environmental_lower_sensor_detection_limit = models.IntegerField(default=None)    #Lower detection limit for sensor in same unit specified for sensor,e.g. “5”
    environmental_upper_sensor_detection_limit = models.IntegerField(default=None) #  Upper detection limit for sensor in same unit specified for sensor, e.g. “2500”
    environmental_sensor_precision = models.DecimalField(max_digits=20, decimal_places=3,default=None)#Sensor precision in same unit specified for sensor,e.g. “+/- 0.01”
    environmental_sensor_sampling_frequency = models.IntegerField(default=None) #How often the sensor records a measurement in Hz
    environmental_sensor_duty_cycling = models.CharField(max_length=100,default=None) #Description of any duty cycling assigned to sensor,e.g. "records data only on deepest dive in 6 hr period"
    environmental_sensor_calibration_date = models.DateTimeField(default=None)#Date when sensor calibration was done. ISO-8601 Datetime in UTC, yyyy-MM-ddT HH:mm:ss.SSSZ, e.g. “2020-03-29T 17:56:10.000Z”
    environmental_sensor_calibration_details = models.URLField(max_length=200,default=None)#Full definition of the calibration done through addition of a link to where the data and/or methods are described (e.g. peer-reviewed publication).
    physiological_sensor_type = models.CharField(max_length=40,default=None)#Type of sensor in instrument (e.g. heart oxygen probe, blood oxygen probe).
    physiological_sensor_manufacturer =models.CharField(max_length=50,default=None)#Name of the manufacturer of the sensor (may or may not be the same as the instrument manufacturer).
    physiological_sensor_model =models.CharField(max_length=50,default=None)#Name of specific sensor model.
    physiological_sensor_units_reported  = models.CharField(max_length=20,default=None)#Unit of altitude/depth reported,e.g. “meters”
    physiological_lower_sensor_detection_limit = models.IntegerField(default=None)    #Lower detection limit for sensor in same unit specified for sensor,e.g. “5”
    physiological_upper_sensor_detection_limit = models.IntegerField(default=None) #  Upper detection limit for sensor in same unit specified for sensor, e.g. “2500”
    physiological_sensor_precision = models.DecimalField(max_digits=20, decimal_places=3,default=None)#Sensor precision in same unit specified for sensor,e.g. “+/- 0.01”
    physiological_sensor_sampling_frequency = models.IntegerField(default=None) #How often the sensor records a measurement in Hz
    physiological_sensor_duty_cycling = models.CharField(max_length=100,default=None) #Description of any duty cycling assigned to sensor,e.g. "records data only on deepest dive in 6 hr period"
    physiological_sensor_calibration_date = models.DateTimeField(default=None)#Date when sensor calibration was done. ISO-8601 Datetime in UTC, yyyy-MM-ddT HH:mm:ss.SSSZ, e.g. “2020-03-29T 17:56:10.000Z”
    physiological_sensor_calibration_details = models.URLField(max_length=200,default=None)#Full definition of the calibration done through addition of a link to where the data and/or methods are described (e.g. peer-reviewed publication).
    physiological_sensor_model=models.CharField(max_length=50,default=None)
    accelerometry_sensor_manufacturer =models.CharField(max_length=50,default=None,null=True,blank=True)#Name of the manufacturer of the sensor (may or may not be the same as the instrument manufacturer).
    accelerometry_sensor_model =models.CharField(max_length=50,default=None,null=True,blank=True)#Name of specific sensor model.
    accelerometry_sensor_axes=models.CharField(max_length=50,default=None)#Axes in which acceleration is logged.Categorical (combinations of x, y, and z)
    accelerometry_sensor_units_reported  = models.CharField(max_length=20,default=None)#Unit of altitude/depth reported,e.g. “meters”
    accelerometry_lower_sensor_detection_limit = models.IntegerField(default=None)    #Lower detection limit for sensor in same unit specified for sensor,e.g. “5”
    accelerometry_upper_sensor_detection_limit = models.IntegerField(default=None) #  Upper detection limit for sensor in same unit specified for sensor, e.g. “2500”
    accelerometry_sensor_precision = models.DecimalField(max_digits=20, decimal_places=3,default=None)#Sensor precision in same unit specified for sensor,e.g. “+/- 0.01”
    accelerometry_sensor_sampling_frequency = models.IntegerField(default=None) #How often the sensor records a measurement in Hz
    accelerometry_sensor_duty_cycling = models.CharField(max_length=100,default=None) #Description of any duty cycling assigned to sensor,e.g. "records data only on deepest dive in 6 hr period"
    accelerometry_sensor_calibration_date = models.DateTimeField(default=None)#Date when sensor calibration was done. ISO-8601 Datetime in UTC, yyyy-MM-ddT HH:mm:ss.SSSZ, e.g. “2020-03-29T 17:56:10.000Z”
    accelerometry_sensor_calibration_details = models.URLField(max_length=200,default=None)#Full definition of the calibration done through addition of a link to where the data and/or methods are described (e.g. peer-reviewed publication)


class InputData(models.Model):
    upload_identifier = models.CharField(max_length=20,default=None,null=True,blank=True)
    instrumentID  = models.CharField(max_length=50,default=None,null=True,blank=True)
    deploymentID  = models.CharField(max_length=15,unique=True,null=True,blank=True)#Unique identifier for single deployment of device.
    organismID  = models.CharField(max_length=15,unique=True,null=True,blank=True)#Unique identifier for an individual, links data from different deployments or instruments on the same animal.
    organismIDSource = models.TextField(default=None , null = True,blank = True)#URN denoting the globally unique identifier as assigned by the repository publishing the dataset.
    time =models.DateTimeField(default=None , null = True,blank = True)#Timestamp of data point.
    latitude = models.DecimalField(max_digits=22, decimal_places=16,default=None , null = True,blank = True)#  Latitude of data point.
    longitude = models.DecimalField(max_digits=22, decimal_places=16,default=None, null = True,blank = True)#     Longitude of data point.
    argosLC = models.CharField(max_length=20,default=None , null = True,blank = True)#Argos quality class for positions retrieved from ARGOS.
    argosErrorRadius = models.FloatField(default=None, null = True,blank = True )#Argos quality class for positions retrieved from ARGOS. 
    argosSemiMajor = models.FloatField(default=None , null = True,blank = True)#Length of semi-major axis of error ellipse provided by CLS/Argos. Defaults to NA if Least-Squares Data.
    argosSemiMinor = models.FloatField(default=None , null = True,blank = True)#Length of semi-minor axis of error ellipse provided by CLS/Argos. Defaults to NA if Least-Squares Data.
    argosOrientation = models.FloatField(default=None , null = True,blank = True)#Orientation of error ellipse provided by CLS/Argos.
    argosGDOP = models.FloatField(default=None , null = True,blank = True)#Geometric Dilution of Precision provided by CLS/Argos.
    gpsSatelliteCount = models.IntegerField(default=None , null = True,blank = True)#The number of satellites used to estimate location (rapid acquisition GPS).
    residualsGPS  = models.FloatField(default=None, null = True,blank = True)#Measure of how well the solution provided for the location estimate matched the observed data.
    temperatureGLS = models.FloatField(default=None , null = True,blank = True)#In situ temperature measured by instrument (can be used to correct geolocation positions). Associated with depth in "Depth GLS e.g, 45.5 °C
    depthGLS  = models.FloatField(default=None , null = True,blank = True)#Depth of the in situ temperature measurements taken and recorded in "Temperature GLS" field.
    sensorIMeasurement = models.CharField(max_length=100,default=None , null = True,blank = True)#Measurement taken by SensorI at this time and location. Can be repeated for any number of sensors (N), as specified in Device template (e.g. SensorI, SensorII,...SensorN). Units of measurement and other relevant metadata documented in Device metadata table.
    sensor_type = models.CharField(max_length=40,default=None, null = True,blank = True)


