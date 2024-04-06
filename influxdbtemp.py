import influxdb_client, os, time, glob 
from influxdb_client import InfluxDBClient, Point, WritePrecision 
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN") 
org = "" #Your Org
url = "" #Server url

print(token)

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

# These tow lines mount the device:
os.system('modprobe w1-gpio') 
os.system('modprobe w1-therm')

def read_temp_raw(device_file): 
	f = open(device_file, 'r') 
	lines = f.readlines() 
	f.close() 
	while len(lines) == 0:
		f = open(device_file, 'r') 
		lines = f.readlines() 
		f.close()
	return lines

def read_temp(device): 
    base_dir = '/sys/bus/w1/devices/' 
    device_folder = glob.glob(base_dir + device)[0] 
    device_file = device_folder + '/w1_slave' 
    lines = read_temp_raw(device_file)

    # Analyze if the last 3 characters are 'YES'.
    while lines[0].strip()[-3:] != 'YES': 
        time.sleep(0.2) 
        lines = read_temp_raw()
    # Find the index of 't=' in a string.
    equals_pos = lines[1].find('t=') 
    if equals_pos != -1:
        # Read the temperature .
        temp_string = lines[1][equals_pos+2:] 
        temp_c = float(temp_string) / 1000.0 
        temp_f = temp_c * 9.0 / 5.0 + 32.0 
        return temp_c, temp_f

bucket="temps" 
write_api = client.write_api(write_options=SYNCHRONOUS)

while True: 
    #print('inner C=%3.3f F=%3.3f'% read_temp('temp-one-name')) 
    #print('outer C=%3.3f F=%3.3f'% read_temp('temp-two-name')) 
    time.sleep(1)

    temp_inside = read_temp('temp-one-name') 
    temp_outside = read_temp('temp-two-name')

    outside = ( Point("temp_outside") .tag("tagname1", "tagvalue1") 
         .field("field1", temp_outside[1])
    )

    inside = ( Point("temp_inside") .tag("tagname1", "tagvalue1") 
         .field("field1", temp_inside[1])
    )

    write_api.write(bucket=bucket, org="HOME PROJECTS", record=outside) 
    write_api.write(bucket=bucket, org="HOME PROJECTS", record=inside)

    time.sleep(10) 
    #print("good")

