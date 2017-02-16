#!/usr/bin/env python

""" 
awsreport.py, Berhe Gebretensai
This script queries your aws account and collects information
on VPCs and EC2 instances and generates an excel spreadshet 
with the collected information.
"""

import boto3    
import xlsxwriter
import collections

# set myTag to what ever tag you want reported
# i.e myTag = 'department', default is project
# also set the title of the tag
myTag = 'project'
myTagTitle = 'Project Tag'

def main():
    # Create the workbook
    workbook = xlsxwriter.Workbook('awsreport.xlsx', {'remove_timezone': True})

    # define a cell format
    bold = workbook.add_format({'bold': True})
    redBG = workbook.add_format({'bold': True, 'font_color': 'red'})

    class myVPC:
        """
        VPC class - represents Name, State, VPCID, and cidr block 
        """        

        num_of_vpcs = 0
        my_vpc_dict = {}

        def __init__(self, vpcname, vpcstate, vpcid, cidr):
            self.vpcname = vpcname
            self.vpcstate = vpcstate
            self.vpcid = vpcid
            self.cidr = cidr
        
            myVPC.num_of_vpcs += 1

            #if self.vpcid in myVPC.my_vpc_dict.keys():
            if myVPC.my_vpc_dict.has_key(self.vpcid):
                pass
            else:
                myVPC.my_vpc_dict[self.vpcid] = self.vpcname
    
    class EC2:
        """ 
        EC2 class - Name, Instance id, type, AZ, State, IP, launch time
        """
        num_of_ec2s = 0

        def __init__(self, ec2name, instanceId, instanceType, az, state, privateIP, launchTime, OS, projectCode, vpcid):
            self.ec2name = ec2name
            self.instanceId = instanceId
            self.instanceType = instanceType
            self.az = az
            self.state = state
            self.privateIP = privateIP
            self.launchTime = launchTime
            self.OS = OS
            self.projectCode = projectCode
            self.vpcid = vpcid

            EC2.num_of_ec2s += 1

    vpc_client = boto3.resource('ec2')
    vpc_ids = vpc_client.vpcs.all()
   
    vpcList = [] 
    for i in vpc_ids:
        v = vpc_client.Vpc(i.id)
        vpcid = v.vpc_id
        vpcstate = v.state
        cidr = v.cidr_block
        for t in v.tags:
            if t['Key'] == 'Name':
                vpcname = t['Value']
        vpctemp = myVPC(vpcname, vpcstate, vpcid, cidr) 
        vpcList.append(vpctemp)
   
    # Load EC2 
    ec2List = []
    client = boto3.client('ec2')
    response = client.describe_instances()

    for r in response['Reservations']:
        for i in r['Instances']:
            state = i['State']['Name']
            vpcid = i['VpcId']
            privateIP = i['PrivateIpAddress']
            launchTime = i['LaunchTime']
            instanceId = i['InstanceId']
            az = i['Placement']['AvailabilityZone']
            instanceType = i['InstanceType']
            for t in i['Tags']:
                if t['Key'] == 'Name':
                    ec2name = t['Value']

                if t['Key'] == myTag:
                    projectCode = t['Value']
                else:
                    projectCode = 'None'
           
            inst = boto3.resource('ec2')
            s = inst.Instance(id=instanceId)
            if s.platform  == 'Windows':
                OS = 'Windows'
            else:
                OS = 'Linux'

            ec2temp = EC2(ec2name,instanceId,instanceType,az,state,privateIP,launchTime,OS,projectCode,vpcid) 
            ec2List.append(ec2temp)

    def loadVPCs(): 
        # create VPC worksheet
        # worksheet fields: VPC Name | VPC State | VPC ID | VPC CIDR 
        vpcworksheet = workbook.add_worksheet("VPC Information")
        
        # set columns width for vpcworksheet
        vpcworksheet.set_column('A:D', 20)

        # populate header cells
        vpcworksheet.write('A1', 'VPC Name', bold)
        vpcworksheet.write('B1', 'VPC State', bold)
        vpcworksheet.write('C1', 'VPC ID', bold)
        vpcworksheet.write('D1', 'VPC CDIR', bold)

        row = 2
        for i in vpcList:
            # loop through list and populate the worksheet starting from row 2
            vpcworksheet.write('A'+str(row), i.vpcname)
            vpcworksheet.write('B'+str(row), i.vpcstate)
            vpcworksheet.write('C'+str(row), i.vpcid)
            vpcworksheet.write('D'+str(row), i.cidr)
            row += 1
 
    def loadEC2s():

        for vID,vName in myVPC.my_vpc_dict.iteritems():
            ec2worksheet = workbook.add_worksheet(vName) 
            #if firstrun == 'true':
            ec2worksheet.set_column('A:J', 20)
            # add time format
            ec2worksheet.set_column('A:J', 20)

            ec2worksheet.write('A1', 'EC2 Name', bold)
            ec2worksheet.write('B1', 'Instance ID', bold)
            ec2worksheet.write('C1', 'Instance Type', bold)
            ec2worksheet.write('D1', 'Availability Zone', bold)
            ec2worksheet.write('E1', 'State', bold)
            ec2worksheet.write('F1', 'Private IP', bold)
            ec2worksheet.write('G1', 'Launch Time', bold)
            ec2worksheet.write('H1', 'Operating System', bold)
            ec2worksheet.write('I1', myTagTitle, bold)
            ec2worksheet.write('J1', 'VPC ID', bold)

            currentID = vID
            row = 2
            for i in ec2List:
                if i.vpcid == currentID:
                    ec2worksheet.write('A'+str(row), i.ec2name)
                    ec2worksheet.write('B'+str(row), i.instanceId)
                    ec2worksheet.write('C'+str(row), i.instanceType)
                    ec2worksheet.write('D'+str(row), i.az) 
                    ec2worksheet.write('E'+str(row), i.state) 
                    ec2worksheet.write('F'+str(row), i.privateIP) 
                    ec2worksheet.write('G'+str(row), i.launchTime) 
                    ec2worksheet.write('H'+str(row), i.OS) 
                    if i.projectCode == 'None':
                        ec2worksheet.write('I'+str(row), "MISSING", redBG) 
                    else:
                        ec2worksheet.write('I'+str(row), i.projectCode) 
                    ec2worksheet.write('J'+str(row), i.vpcid) 
                    row += 1 

    loadVPCs()
    loadEC2s()
    
    workbook.close()

if __name__ == "__main__":
    main()
