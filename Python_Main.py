import sys
import subprocess
from time import sleep

Sensor_1 = "B0:B4:48:D2:F4:04"
Sensor_2 = "B0:B4:48:C9:EA:83"
Sensor_3 = "B0:B4:48:D2:2C:82"
Sensor_4 = "A0:E6:F8:C1:C7:87"
Sensor_5 = "A0:E6:F8:AF:32:86"
Sensor_6 = "A0:E6:F8:AE:0F:85"
Sensor_7 = "A0:E6:F8:C2:63:05"
Sensor_8 = "24:71:89:07:86:06"
Sensor_9 = "B0:B4:48:C9:DD:83"

Pible_1 = "A0:E6:F8:CE:D9:87"
Pible_2 = "A0:E6:F8:CE:E0:87"
Pible_3 = "A0:E6:F8:CE:E8:03"

Pible_1_v2 = "A0:E6:F8:BE:F1:06"

Sensor_Dict = {
'FFM' : "A0:E6:F8:BF:2E:87",
'FF1' : "A0:E6:F8:BF:8E:84",
'FF2' : "A0:E6:F8:BF:8F:80",
'FF3' : "A0:E6:F8:BE:D3:80",
'FF4' : "A0:E6:F8:BF:0F:05",
'FF5' : "A0:E6:F8:BE:F3:06",
'FF6' : "A0:E6:F8:BF:7B:04",
'FF7' : "A0:E6:F8:BF:09:01",
'FF8' : "A0:E6:F8:BE:E4:85",
'FF9' : "A0:E6:F8:BE:FF:81",
'FF10' : "A0:E6:F8:BE:F2:03",
'FF11' : "A0:E6:F8:BE:D4:86",

'FFS1': "A0:E6:F8:BE:D8:82",
}

ID_List =[]
Name_List = []
File_List = []
f = open("ID.txt", "r")
content = f.read()
splitted = content.split(',')
Sens_Splitted = splitted[0].split('-') #[Sensor_5, Sensor_1]
File_Splitted = splitted[1].split('-') #[Sensor_5, Sensor_1]
if len(Sens_Splitted) == len(File_Splitted):
	print "File Ok"
else:
	print "Error: Check ID File"
	quit()

for i in range(len(Sens_Splitted)):
	ID_List.append(Sensor_Dict[Sens_Splitted[i]])
	Name_List.append(str(Sens_Splitted[i])) #["Sensor_5", "Sensor_1"]
	File_List.append(str(File_Splitted[i])) #["2142_Middle_Battery.txt", "2142_Middle_Pible.txt"]

finder_time = 3 # time needed to avoid that multiple process are called and not completly killed. Put 3 for one sensor and 1 for several sensors
write_completed = 5 #after you write a data you avoid to call the sensor again. Put 1 for several sensors and 5 for 1 sensor
tryals = 5 #number of trials it looks for a specific device. Each try is 0.5s. Put 10 for 1 sensor and 5 for multiple sensors

def kill_search():
	subprocess.Popen("killall Find_New_BLE_Device.sh 2?/dev/null, shell=True")

def killer():
	subprocess.Popen("killall Detector.sh 2>/dev/null", shell=True)
	subprocess.Popen("killall gatttool 2>/dev/null" , shell=True)

def check():
	for ii in range(0,tryals):
		with open('wait.txt', 'r') as f:
			first_line = f.readline()
		f.close()
		first = first_line[:1]
		if first == '2': # if it reads 2 that means that Detector.sh has already written everything
			#print "Sleep 1"
			sleep(write_completed)
			return
        	if first == '1': #if it reads 1 it we five him other 10 extra seconds to finish to write the data
        		for i in range(0,20):
        			#wait = 0
                		#f = open('wait.txt','w')
        			#f.write('0')
        			#f.close()
		        	with open('wait.txt', 'r') as f:
					first_line = f.readline()
					f.close()
					first = first_line[:1]
					if first == '2':
						sleep(write_completed)
						#print  "Sleep 2"
						return
				sleep(0.5)
		sleep(0.5)

print "Let us Start!!"
while(1):
	for x in range(0,len(Sens_Splitted)):
		
		subprocess.Popen("bash Find_New_BLE_Device.sh > dev_found.txt", shell=True)
		sleep(2)
		with open("dev_found.txt", 'r') as f:
			data = f.read()
		for i in range(len(data)):
			print(data[i])
		
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
		sleep(finder_time)

print "It's Over"

#sudo hciconfig hci0 reset

#B0:B4:48:C9:EA:83
#gatttool -b $Sensor --char-write-req -a 0x0024 -n 00

#subprocess.Popen("gatttool -b B0:B4:48:C9:EA:83 --char-write-req -a 0x0024 -n 00")
