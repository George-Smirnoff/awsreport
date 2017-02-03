#!/usr/bin/python

import boto3    
ec2client = boto3.client('ec2')
response = ec2client.describe_instances()

InstanceIdsArray = []
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        #print(instance["InstanceId"])
        InstanceIdsArray.append(instance["InstanceId"])

ec2 = boto3.resource('ec2')
for i in InstanceIdsArray:
    currentInst = ec2.Instance(i) 
    print currentInst 
    list=currentInst.tags
    print list
    if list is None:
        #print("none")
        continue
    mylist = [] 
    for i in list:
        print i['Key'],"=",i['Value']
        tagValue = i['Key'] + " = " + i['Value']
        mylist.append(tagValue)
        #if i['Key'] == 'project':
         #   print i['Key'],"=",i['Value']
    print mylist


#print dict


#print dict['Name']
     #print(i.tags["Key"])
 #   ec2instance = ec2.Instance(i)
 #   print(ec2instance)
    #instancename = ''
    #for tags in i.tags:
    #    if tags["Key"] == 'Name':
    #        #instancename = tags["Value"]
    #        print("hello")
