import sys
import subprocess
from time import sleep
import json
import os
import time
import datetime
from subprocess import PIPE

path = '/home/pi/BLE_GIT/Base_Station/'
ID_List = []
Name_List = []
File_List = []

Name_spl = []
File_spl = []

with open("../ID/ID.txt", "r") as f:
    for line in f:
        splitted = line.split(',')
        print(splitted)
        Name_spl.append(splitted[0]) 
        File_spl.append(splitted[1]) 
#print(Name_spl, File_spl)

if len(Name_spl) == len(File_spl):
    print("File Ok Ok")
else:
    print("Error: Check ID File")
    quit()

dict_dev = {}

with open('pible_dev_list.txt', 'r') as inf:
    for data in inf:
        line = data.strip().split(' ')
        dict_dev[line[0]] = line[1]

for i in range(len(File_spl)):
    checker = 1
    for key, val in dict_dev.items():
        if Name_spl[i] == val:
            ID_List.append(key)
            checker = 0
            break
    if checker == 1:
        print('Huston we have a problem, sensor not found! Try updating device List!')
        quit()
    Name_List.append(str(Name_spl[i])) #["Sensor_5", "Sensor_1"]
    File_List.append('../Data/' + str(File_spl[i])) #["2142_Middle_Battery.txt", "2142_Middle_Pible.txt"]

#print(ID_List)
#print(Name_List)
#print(File_List)
#quit()

#finder_time = 3 # time needed to avoid that multiple process are called and not completly killed. Put 3 for one sensor and 1 for several sensors
write_completed = 1 #after you write a data you avoid to call the sensor again. 
tryals = 5 #number of trials it looks for a specific device. Each try is 0.5s. 

def kill_search():
	subprocess.Popen("killall Find_New_BLE_Device.sh 2>/dev/null", shell=True)

def killer():
	subprocess.Popen("killall Detector.sh 2>/dev/null", shell=True)
	subprocess.Popen("killall gatttool 2>/dev/null" , shell=True)

def check():
    for ii in range(0,tryals):
        with open('wait.txt', 'r') as f:
            first_line = f.readline()
        first = first_line[:1]
        #print(first)
        if first == '2': # if it reads 2 that means that Detector.sh has already written everything
	    #print "Sleep 1"
            sleep(write_completed)
            return
        if first == '1': #if it reads 1 it we five him other 10 extra seconds to finish to write the data
            for i in range(0,10):
                #print('here')
                with open('wait.txt', 'r') as f:
                    first_line = f.readline()
			
                first = first_line[:1]
                if first == '2':
                    sleep(write_completed)
                    return
                sleep(0.5)
        sleep(0.5)

def get_raw_data(ID):
    with open('wait.txt', 'w') as f:
        f.write('0')
        sleep(0.1)
                    
    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break

    with open('ID.txt', 'r') as f:
        Action = '-1'
        for line in f:
            line = line.strip()
            splt = line.split(',')
            if Name == splt[0]:
                #print(splt[0], splt[2])
                Action = splt[2]
                break
        
        if Action == '-1':
            print("Pay Attention: Name and Action not found")
            Action = '0'

    #print("bash get_data_from_device.sh "+Name+" "+ID+" "+File+" "+Action) 
    subprocess.Popen("bash get_data_from_device.sh "+Name+" "+ID+" "+File+" "+Action+" &", shell=True)
   
    #subprocess.Popen('bash get_data_from_device.sh ' +Name+' '+ID+' '+File+' '+Action+' &', shell=True)
    #print('checking')
    check()
    #print('checking over')
    killer()
    sleep(0.5)
                    
def get_action_name(ID):
    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break

    with open('../ID/ID.txt', 'r') as f:
        Action = '-1'
        for line in f:
            line = line.strip()
            splt = line.split(',')
            if Name == splt[0]:
                #print(splt[0], splt[2])
                Action = splt[2]
                break
    return (Action, Name, File)
     

print("Let us Start!!")

#Reset BLE drivers
#subprocess.Popen("sudo hciconfig hci0 reset &", shell=True)
#print(json.dumps(dict_dev, indent=1, sort_keys=True))

avoid = []  # in this list there are all the devices that have been read and that needs to be left alone for a bit to avoid to get the data read twice.
countarell = 0

while(True):
    #print('here')	
    Name = ''
    File = ''
    #print("scanning")
    try:
    	os.remove('dev_found.txt')
    except:
        pass
    #subprocess.Popen("bash Find_New_BLE_Device.sh > dev_found.txt", shell=True)
    subprocess.Popen('sudo blescan -t 3 > dev_found.txt', shell=True)
    sleep(3.5)
    found = []
    if os.stat('dev_found.txt').st_size < 2:
        print('empty')
        sleep(5)
        print('No devices found, something wrong? Resetting')
        subprocess.Popen('sudo hciconfig hci0 reset', shell=True)
        sleep(5)
    else:
        with open("dev_found.txt", 'r') as f:
            for line in f:
                line = line.strip()
                #print(len(line))
                splitted = line.split(' ')
                try:
                    ID = splitted[2][5:22]
                except:
                    ID = 'Not_found'
                if ID in ID_List and ID not in avoid and ID not in found:
                        #print('trovato')
                        found.append(ID)
                        Action, Name, File = get_action_name(ID)
                        log_temp = File.split('/')
                        log = log_temp[-1]
                        #File = 'blupytest.txt'
                        #print(Action)
                        #print('sensortag -T -H -B ' + ID + ' -n 1 > ' + Name + ' &')
                        t = time.strftime('%m/%d/%y %H:%M:%S')
                        #with open(File, 'a') as f:
                        #    f.write('\n' + str(t) + '|' + Name + '|||')

                        #print(str(t) + '|' + Name + '|||')
                        #print('here')
                        #if Action == '3':
                            #print('hereh1')
                            #subprocess.Popen('sensortag -Na ' + log + ' -B ' + ID + ' -n 1 | tee -a ' + File + ' &', shell=True)
                        #subprocess.Popen('sensortag -Na ' + log + ' -B ' + ID + ' -n 1 | tee -a ' + File + ' &', shell=True)
                        #print(Name,ID,File,Action,log)
                        subprocess.Popen("bash Detector.sh " + Name + " " + ID + " " + File + " " + Action + " " + log + " 2>error.txt &", shell=True)


    #print("found", found)
    if len(avoid) > 0:
        #print('remove avoiding last ID')
        for ID in ID_List:
            if ID in avoid: 
                avoid.remove(ID)
                #print('removing ', ID)

    if len(found) > 0:   # There are some device that needs to be downloaded
        for ID in found:
            avoid.append(ID)
            avoid.append(ID)
            avoid.append(ID)
            #avoid.append(ID)
            #print('avoiding ', ID)
        
       
    #if len(found) > 0:
    #    #for i in range(len(ID_List)):
    #    avoid.append(found[-1])
    #    avoid.append(found[-1])
        #print('avoiding last ID')
    try:
    	with open('error.txt','r') as f:
            for line in f:
	        #print(line)
                contain = line.strip().split(' ')
                if (len(line.strip()) > 0) and '(38)' not in contain and '(107)' not in contain and '(111)' not in contain and 'unlikely' not in contain and 'Traceback' not in contain:
                    print(line)
                    print('something wrong, resetting')
                    sleep(5)
                    os.remove('error.txt')
                    subprocess.Popen('sudo hciconfig hci0 reset', shell=True)
                    sleep(5)
                    break
    except:
        continue

    sleep(1)

    proc = subprocess.Popen("cat /var/log/auth.log | grep 'Accepted password' > Accepted_file.txt", stdout=subprocess.PIPE, shell=True)
    #proc = Popen("ls Q_Tables", stdout=PIPE, shell=True)
    (out, err) = proc.communicate()
	
    #subprocess.Popen('tail -1 Accepted_file.txt > Accepted_file.txt', shell=True)
    for line in reversed(open('Accepted_file.txt').readlines()):
        #line line.rstrip())
        spl = line.rstrip().split(' ')
    print(spl)
    clock = spl[2].split(':')

    now = datetime.datetime.now()
    print(clock[0])
    last_time = datetime.datetime(int(now.year), str(spl[0]), int(spl[1]), int(clock[0]), int(clock[1]), int(clock[2]))
    print(last_time)
    
    ''' 	    
		
    ID = ID_List[x]
    Name = str(Name_List[x])
    File = str(File_List[x])
    wait = 0
    		f = open('wait.txt','w')
		f.write('0')
		f.close()
		if x == 0:
			with open('action.txt','r') as f:
				first_line = f.readline()
		else:
			with open('action_2.txt','r') as f:
				first_line = f.readline()

		Action = first_line[:1]
		#Checker.main(Name,ID,File)
		subprocess.Popen("bash Detector.sh "+Name+" "+ID+" "+File+" "+Action+" &", shell=True)
		#process = subprocess.Popen(["PID=$!","echo $PID"],stdout=subprocess.PIPE, shell=True) #I removed this
		#sleep(finder_time)
		check()
		killer()
    '''

print("It's Over")

#sudo hciconfig hci0 reset

#B0:B4:48:C9:EA:83
#gatttool -b $Sensor --char-write-req -a 0x0024 -n 00

#subprocess.Popen("gatttool -b B0:B4:48:C9:EA:83 --char-write-req -a 0x0024 -n 00")
