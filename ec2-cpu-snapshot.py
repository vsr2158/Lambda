import sys
import botocore
import boto3
import datetime as datetime
# Get list of regions
ec2_client = boto3.client("ec2")
regions = [region['RegionName']
           for region in ec2_client.describe_regions()['Regions']]
print ("######### List of all regions to be iterated:")
print(regions)
current_utc_time = datetime.datetime.utcnow()
past_utc_time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
print("######### Metric Start Time:", past_utc_time)
print("######### Metric End Time:",current_utc_time)
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

    for instance in instances:
        print (instance.id)
        metric_response = metric.get_statistics(
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
        print (metric_response)
        all_instance_ids.append(instance.id)
        other_instance_ids = set(all_instance_ids) - (set(test_instance_ids))
    print('All Instances in region:', region, all_instance_ids)
