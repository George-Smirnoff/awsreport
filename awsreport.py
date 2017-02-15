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
            print i.vpcname
            print i.vpcstate
            print i.vpcid
            print i.cidr
            row += 1

    loadVPCs()
    
    workbook.close()

if __name__ == "__main__":
    main()
