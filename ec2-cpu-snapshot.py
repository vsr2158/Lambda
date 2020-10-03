import json
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
regions = ["us-west-2"]
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
        datapoints_av_cpu = metric_response_av_cpu.get("Datapoints")
        datapoints_mx_cpu = metric_response_mx_cpu.get("Datapoints")
        datapoints_av_cpu = datapoints_av_cpu[0]
        datapoints_mx_cpu = datapoints_mx_cpu[0]
        datapoints_all = {**datapoints_av_cpu, **datapoints_mx_cpu}
        print(datapoints_all)
        #print (datapoints_mx_cpu)
        #metric_response_mx_cpu['InstanceId'] = instance.id
        #print (metric_response_composite)
        #print ((metric_response_av_cpu))
        #print ((metric_response_mx_cpu))
        jout = (json.dumps(datapoints_all, default=str))
        #jout["instance.id"] = instance.id
        print(jout)
        all_instance_ids.append(instance.id)
        other_instance_ids = set(all_instance_ids) - (set(test_instance_ids))
    print('All Instances in region:', region, all_instance_ids)
