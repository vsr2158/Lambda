import json
import boto3
import datetime as datetime
bucket_name = "137965528627-ec2-rightsizing"
def s3_load_data (item, current_date):
    objname = 'ec2-cpu'+ "-" + current_date
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, objname)
    print("####### Going to upload data to bucket:", bucket_name )
    print("####### Going to upload following data to the bucket:", item)
    obj.put(Body=json.dumps(item))
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
#regions = ["us-west-2"]
datapoints_all = []
#regions = ['us-west-2']
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
        instance_datapoints_av_cpu = metric_response_av_cpu.get("Datapoints")
        instance_datapoints_mx_cpu = metric_response_mx_cpu.get("Datapoints")
        instance_datapoints_av_cpu = instance_datapoints_av_cpu[0]
        instance_datapoints_mx_cpu = instance_datapoints_mx_cpu[0]
        instance_datapoints_all = {**instance_datapoints_av_cpu, **instance_datapoints_mx_cpu}
        instance_datapoints_all['InstanceId'] = instance.id
        print(instance_datapoints_all)
        all_instance_ids.append(instance.id)
        other_instance_ids = set(all_instance_ids) - (set(test_instance_ids))
        datapoints_all.append(instance_datapoints_all)
    print('All Instances in region:', region, all_instance_ids)
print('Printing all datapoints: ', datapoints_all)
datapoints_all_json = (json.dumps(datapoints_all,default=str))
print('Printing all datapoints JSON: ', datapoints_all_json)
s3_load_data(datapoints_all_json, current_date)
