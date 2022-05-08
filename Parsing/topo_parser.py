# -*- coding: utf-8 -*-

import os,sys
import argparse
import time
import re
import threading

class Devices:
    '''
    Master class to hold all devices 
    '''
    def __init__(self, file_path):
        self.file_path = file_path
        self.devices_list = []  # a list of objects to hold all the devices  
        self.report = []  # the final report will be writen to file using self.report 
    
    def write_to_file(self,file_name):
        # writing report to file
        print("Saving data to file")
        with open(file_name,'w') as fr:
            for line in self.report:
                fr.write(line)  
    
    def add_device(self,sysimgguid,switchguid=None,port_id=None):
        '''
        Add new device (switch/host) to the devices_list
        In order to support both Host and Switch configuration
        Both option were taken in considuration
        A pair of sysimgguid/switchguid or a sysimgguid/port_id can be created
        '''
        device = Device(sysimgguid,switchguid,port_id)
        self.devices_list.append(device)
    
    def add_inner_device(self,device_name,device_kind,port_num):
        '''
        Add inner devices to an exsisting device
        This will hold the list for all devices under a specific device
        The use of devices list[-1] will take care of the "counting and management"
        of each main device for it's devices link 
        '''
        inner_device = Inner_device(device_name,device_kind,port_num)
        self.devices_list[-1].inner_device_list.append(inner_device)
    
    def parse_data(self):
        '''
        Reading each line to extract the data All parsing is done line by line, 
        and the devices are collected as they appear by their chronological order.
        '''
        try:
            with open(self.file_path, 'r',encoding ="utf-8") as fo:
                # Skip the first 4 rows with no data
                for i in range(4):
                    next(fo)
                # Start parsing and analysis the file line by line
                for line in fo:
                    # the found var will be use to stop checking the conditions in case
                    # it was already submitted to a proper var by the if's statements
                    found = False
                    test_line = line.split('\n')
                    test_line = test_line[0]
                    # first catch the device main characters:
                    # sysimgguid/switchguid/caguid
                    device_name = test_line.split('=')
                    if device_name[0] == 'sysimgguid' and not found:
                        sysimgguid = device_name[1]
                        found =True
                    # The 'switchguid' indicate on a Switch device
                    elif device_name[0] == 'switchguid' and not found:
                        switchguid = device_name[1]
                        self.add_device(sysimgguid=sysimgguid,switchguid=switchguid)
                        found =True
                    # We will skip this line, it's not adding valuable information
                    elif re.match('Switch',test_line) and not found:
                        found = True
                    # the 'caguid' indicate on a Host device 
                    elif device_name[0] == 'caguid' and not found:
                        port_id  = device_name[1]
                        self.add_device(sysimgguid=sysimgguid,port_id=port_id)
                        found = True
                    # We will skip this line, it's not adding valuable information
                    elif re.match('Ca',test_line) and not found:
                        found = True
                    # This line will catch all the inner devices within a certain device.
                    # It's valid both to Host and Switch configuration
                    elif re.search('#',line) and not found:
                        ans = line.split('#')[0]           #'[1]\t"S-b8599f0300fc6de4"[3]\t\t'
                        ans1 = ans.split('\t')             # ['[1]', '"S-b8599f0300fc6de4"[3]', '', '']
                        ans2 = re.findall(r'\w+', ans1[1]) #['S', 'b8599f0300fc6de4', '3']
                        device_kind = ans2[0] 
                        device_name = ans2[0] + '-' + ans2[1] 
                        port_num = ans2[2] 
                        # Add the device to the devices_list of devices obj
                        self.add_inner_device(device_name,device_kind,port_num)
                        found =True
                        
        except:
            print(f"An error occurred while trying to upload the file {self.file_path}\n" 
                  f"The file {self.file_path} is not exist or corrupted")
        # After parsing is done, the data for the report file is colected
        self.report += f"Parser analysis report on {self.file_path.split('.')[0]} topology\n"
        self.report += "#"*60 + "\n"
        # For each device we will collect the inforamtio on the main device
        # and for the devices linked to it.
        for device in self.devices_list:
            self.report += device.print_device() + "\n"
        self.report += "#"*14 + "        End of File        " + "#"*14 + "\n"
    
class Device(Devices):
    '''
    This class is for creating the main devices (Host/Switch) 
    Each device will keep track on its linked devices as well
    located under inner_device_list list.
    '''
    def __init__(self,sysimgguid, switchguid=None, port_id=None):
        self.sysimgguid = sysimgguid
        self.switchguid = switchguid
        self.port_id = port_id
        self.inner_device_list = []
            
    def print_device(self):
        '''
        The data for each device is collected for the report file
        There is a slight difference between Host and Switch config
        So there is no need for seperate functions for each one of them
        '''
        report = ""
        report = "Connection:\n"
        if self.switchguid:
            report += "Switch:\n"
        else:
            report += "Host:\n"
        report += f"sysimgguid: {self.sysimgguid}\n"
        if self.switchguid:
            report += f"switchguid= {self.switchguid}\n"
        else:
            report += f"port_id= {self.port_id}\n"
        # Once the data for main device is collected, we will look into it's linked devices.
        for inner_device in self.inner_device_list:
            report += inner_device.get_device() +"\n"
        return report
        
class Inner_device():
    '''
    This class is used to create the inner devices 
    Beacuse they have differennt representation, we didnt 
    use the Device class.
    '''
    def __init__(self,device_name,device_kind,device_port):
        self.device_name = device_name
        self.device_port = device_port
        self.device_kind = device_kind
        self.get_device_kind()
        
    def get_device_kind(self):
        " Seperate the two kinds"
        if self.device_kind == 'H':
            self.device_kind = 'Host'
        else:
            self.device_kind = 'Switch'
    
    def get_device(self):
        # create the report line for each inner device
        report = f"--- {self.device_kind} device {self.device_name} connected on port {self.device_port}"
        return report  

def print_data(file_name):
    # After the data was created and writen into a file
    # We can extract it and read it 
    print("#"*60 + "\n")
    try:
        with open(file_name,'r') as fo:
            for line in fo:
                print(line)    
                time.sleep(0.1)
    except:
        print(f'File {file_name} is missing invalid or curropted')
        print("File should be in the format: <source_file>_parser_output.log")

def run_program(file_name):
    #file_name = args.Parse[0]
    # Parse the file
    print("#"*60)
    print("#"*15 + "       Programm started       " + "#"*15)
    print("#"*15 + "       Starting Analysis      " + "#"*15)
    print("#"*5 +"  Infiniband Fabric Topology Connections Parser   " + "#"*5)
    print("#"*60)
    print(f'- Connections list creation for file: {file_name}')
    start_time = time.perf_counter()
    # create the object to hold all devices
    devices = Devices(file_name)
    # Run the parse function
    devices.parse_data()
    output_file_name = file_name.split('.')[0] + '_parser_output.log' 
    # write data to file
    devices.write_to_file(output_file_name)
    end_time = time.perf_counter()
    print("- Program Ended")
    print(f"- For results please see file: {output_file_name}")
    print(f"\nruntime: {round(end_time - start_time,2)}")    
    
if __name__ == "__main__": 
    '''
    Three optional commands:
    1. python topo_parser –help
    print usage
    2. python topo_parser –f topofile.topo
    parse topofile.topo
    3. python topo_parser –print
    print parsed topology
    '''
    # Creating args
    parser = argparse.ArgumentParser(prog='parser',
                                     description="Parse Infiniband Topolgy File.",
                                     allow_abbrev=False)
    parser.add_argument("-print",
                        '--PRINT',
                        action='store_true',
                        help="Print the output parsed log file")
    parser.add_argument("-f",
                        '--Parse',
                        type=str,
                        nargs=1,
                        action='store',
                        help="Parse the given source file")
    args = parser.parse_args()
    threads = []
    
    # Parse file option was chosen  
    if args.Parse:
        t1 = threading.Thread(target=run_program, args=[args.Parse[0]])
        t1.start()
        threads.append(t1)
    # Print option was chosen
    elif args.PRINT:
        # print the reasults
        file_name = 'ibnetdiscover_r-dmz-ufm134_parser_output.log'        
        t2 = threading.Thread(target=print_data, args=[file_name])
        t2.start()
        t2.threads.append(t2)
    
    # An error was occoured
    else:
        raise SystemExit(f"Usage: {args[0]} (-f | -print | -help)")

    for thread in threads:
        thread.join()
