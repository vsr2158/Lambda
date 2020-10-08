import json
import csv
import boto3
import datetime as datetime
bucket_name = "137965528627-ec2-rightsizing"

def s3_load (filename,key):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(filename, bucket_name, key+"/"+filename)
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False

def csv_write (list_instance_dict, current_date):
    csv_columns = ['InstanceId', 'TimeStamp_UTC', 'CPU_Average_Percentage_24Hr','CPU_Maximum_Percentage_24Hr' ]
    try:
        filename = 'ec2-cpu' + "-" + current_date + '.csv'
        with open (filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for item in list_instance_dict:
                print('####################', item)
                writer.writerow(item)
            csvfile.close()
    except IOError:
        print("I/O error writing csv")
    return filename
def json_write (list_instance_dict_json, current_date):
    try:
        filename = 'ec2-cpu' + "-" + current_date + '.json'
        with open (filename, 'w') as jsonfile:
            jsonfile.write(list_instance_dict_json)
            jsonfile.close()
    except IOError:
        print("I/O error writing json")
    return filename
# Get list of regions
ec2_client = boto3.client("ec2")
regions = [region['RegionName']
           for region in ec2_client.describe_regions()['Regions']]
print ("######### List of all regions to be iterated:")
print(regions)
current_utc_time = datetime.datetime.utcnow()
current_date = current_utc_time.isoformat()
past_utc_time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
print("######### Metric Start Time:", past_utc_time)
print("######### Metric End Time:",current_utc_time)
##
#regions = ["us-west-2"]
##
datapoints_all = {}
list_instance_dict = []
for region in regions:
    cloudwatch = boto3.resource('cloudwatch', region)
    metric = cloudwatch.Metric('AWS/EC2', 'CPUUtilization')
    print("######### Going to check region:", region)
    ec2 = boto3.resource('ec2', region_name=region)
    test_instance_ids = []
    other_instance_ids = []
    all_instance_ids = []
    # Get list of Ec2 instances
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name',
                  'Values': ['running']}])
    print(type(instances))
    datapoints_all_json = {}
    for instance in instances:
        print (instance.id)
        metric_response_av_cpu = metric.get_statistics(
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance.id
                },
            ],
            StartTime= past_utc_time,
            EndTime= current_utc_time,
            Period=86400,
            Statistics=[
                'Average',
            ]
        )
        metric_response_mx_cpu = metric.get_statistics(
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance.id
                },
            ],
            StartTime=past_utc_time,
            EndTime=current_utc_time,
            Period=86400,
            Statistics=[
                'Maximum',
            ]
        )
## Lets format the data and store it in a dictionary called instance_dict
        instance_datapoints_av_cpu = metric_response_av_cpu.get("Datapoints")
        instance_datapoints_mx_cpu = metric_response_mx_cpu.get("Datapoints")
        instance_datapoints_av_cpu = instance_datapoints_av_cpu[0]
        instance_datapoints_mx_cpu = instance_datapoints_mx_cpu[0]
        instance_dict = {"InstanceId": instance.id}
        instance_dict["TimeStamp_UTC"] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        instance_dict["CPU_Average_Percentage_24Hr"] = round(instance_datapoints_av_cpu.get("Average"), 2)
        instance_dict["CPU_Maximum_Percentage_24Hr"] = round(instance_datapoints_mx_cpu.get("Maximum"), 2)
        print('#### Printing instance_dict', instance_dict)
        ## we have to append this dictionary to a list called list_instance_dict
        list_instance_dict.append(instance_dict)
## lets print out list_instance_dict to see if all data is present
print('#### Printing list_instance_dict' ,list_instance_dict)
#lets convert the dict to json
list_instance_dict_json = json.dumps(list_instance_dict)
csv_filename = csv_write(list_instance_dict, current_date)
json_filename = json_write(list_instance_dict_json, current_date)
print (csv_filename)
print(json_filename)
s3_load(csv_filename, 'csv')
s3_load(json_filename, 'json')

