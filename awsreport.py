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

def main():
    # Create the workbook
    workbook = xlsxwriter.Workbook('awsreport.xlsx')

    # define a cell format
    bold = workbook.add_format({'bold': True})

    class myVPC:
        """
        VPC class - represents Name, State, VPCID, and cidr block 
        """        

        num_of_vpcs = 0
        
        def __init__(self, vpcname, vpcstate, vpcid, cidr):
            self.vpcname = vpcname
            self.vpcstate = vpcstate
            self.vpcid = vpcid
            self.cidr = cidr
        
            myVPC.num_of_vpcs += 1
    
    class EC2:
        """ 
        EC2 class - Name, Instance id, type, AZ, State, IP, launch time
        """
        num_of_ec2s = 0

        def __init__(self, ec2name, instanceId, instanceType, az, state, privateIP, OS, projectCode, vpcid):
            self.ec2name = ec2name
            self.instanceId = instanceId
            self.instanceType = instanceType
            self.az = az
            self.state = state
            self.privateIP = privateIP
            self.OS = OS
            self.projectCode = projectCode
            self.vpcid = vpcid

            EC2.num_of_ec2s += 1

            
    vpc_client = boto3.resource('ec2')
    vpc_ids = vpc_client.vpcs.all()
   
    vpcList = [] 
    for i in vpc_ids:
        v = vpc_client.Vpc(i.id)
        #print v.vpc_id
        #print v.state
        #print v.cidr_block
        vpcid = v.vpc_id
        vpcstate = v.state
        cidr = v.cidr_block
        for t in v.tags:
            if t['Key'] == 'Name':
                #print t['Value']     
                vpcname = t['Value']
        vpctemp = myVPC(vpcname, vpcstate, vpcid, cidr) 
        vpcList.append(vpctemp)
   

    # Load EC2 list
    # 
#    ec2List = []
#    ec2 = boto3.resource('ec2')
#    inst  = ec2.instances.all()
#    for i in inst:
#        for t in i.tags:
#            if t['Key'] == 'Name':
#                print "Name is %s" % (t['Value'])
#            if t['Key'] == 'project':
#                print "Project is %s" % t['Value']
#        print i.id
#        print i.instance_type
#        print i.state['Name'] 
#        print i.private_ip_address
#        print i.launch_time
#        if i.platform == 'Windows':
#            print "OS is Windows"
#        else:
#            print "OS is Linux"

    # Load EC2 
    ec2List = []
    client = boto3.client('ec2')
    response = client.describe_instances()

    for r in response['Reservations']:
        for i in r['Instances']:
            state = i['State']['Name']
            vpcid = i['VpcId']
            privateIP = i['PrivateIpAddress']
            instanceId = i['InstanceId']
            az = i['Placement']['AvailabilityZone']
            instanceType = i['InstanceType']
            for t in i['Tags']:
                if t['Key'] == 'Name':
                    ec2name = t['Value']

                if t['Key'] == 'project':
                    projectCode = t['Value']
                else:
                    projectCode = 'None'
           
            inst = boto3.resource('ec2')
            s = inst.Instance(id=instanceId)
            if s.platform  == 'Windows':
                OS = 'Windows'
            else:
                OS = 'Linux'

            #instanceId = i['InstanceId']
            #ec2state = i['State']['Name']
            #privateIp = i['PrivateIpAddress']
            #az = i['Placement']['AvailabilityZone']
            #instanceType = i['InstanceType']
            ec2temp = EC2(ec2name,instanceId,instanceType,az,state,privateIP,OS,projectCode,vpcid) 
            ec2List.append(ec2temp)

    for i in ec2List:
        print i.ec2name
        print i.instanceId
        print i.state
        print i.privateIP
        print i.OS
        print i.projectCode
        print i.vpcid

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

    loadVPCs()
    
    workbook.close()

if __name__ == "__main__":
    main()
