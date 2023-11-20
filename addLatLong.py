#!/usr/bin/python3

# addLatLong.py <input_file> <output_file>

# addLatLong.py takes an input file containing a list of broadcaster call-signs
# and retrieves the geolocation in the from of Lat-Long coordinates and
# write the output to a new file similarly made of lines. It effectively adds
# lat-long to each line and writes the result to a new file.

# Includes or imports
import os
import sys
import subprocess
import re
import time

# Initial Defines
web_prefix = 'https://radio-locator.com'
http_cmd = '/usr/bin/curl'
regex_cmd = '/usr/bin/grep'
source_list = sys.argv[1]
dest_list = sys.argv[2]
file_ext = '.html'
RL_regex = '\-\d\d\.\d\d+'
lat_regex = '(?P<Lat>\d\d\.\d\d\d\d\d\d)'
long_regex = '(?P<Long>\-\d\d\.\d\d\d\d\d\d)'
hint_field = 3
rate_limit = 60
backoff_limit = 86400

# Function Definitions
def argCheck():
    if len(sys.argv) == 3:
        return True
    return False

def srcDstCheck(source=source_list, dest=dest_list):
    if os.path.isfile(source) and os.path.isfile(dest):
        if os.access(source, os.R_OK) and os.access(dest, os.W_OK):
            return True
    return False

def lastLineChk(file=dest_list):
    wc_args = ['wc', '-l', file]
    wc_proc = subprocess.run(wc_args, stdout=subprocess.PIPE, universal_newlines=True)
    if wc_proc.returncode == 0:
        wc_out_list = wc_proc.stdout.splitlines()
        if len(wc_out_list) > 0:
            wc_out_line = wc_out_list[0].split()
            if len(wc_out_line) > 0:
                num_lines = int(wc_out_line[0])
            else:
                print('ERROR: Partial dest file not readable.')
                return None
        else:
            print('ERROR: Partial dest file has no lines.')
            return None
    else:
        print('ERROR: \'wc\' failed to execute.')
        return None
    
    tail_args = ['tail', '+' + str(num_lines), file]
    tail_proc = subprocess.run(tail_args, stdout=subprocess.PIPE, universal_newlines=True)
    if tail_proc.returncode == 0:
        tail_out_list = tail_proc.stdout.splitlines()
        if len(tail_out_list) > 0:
            tail_out_line = tail_out_list[0].split(',')
            if len(tail_out_line) > hint_field:
                return tail_out_line[hint_field]
            else:
                print('ERROR: Incomplete line.')
                return None
        else:
            print('ERROR: No last line.')
            return None
    else:
        print('ERROR: Tail did not execute succussfully.')
        return None

# Retrieve Radio-Locator page
# Creates a temporary file named <callsign>.html to be parsed later by HTML parser
# Returns True on success, False on failure
# WARNING: This function does not clean up the file created. Please delete file afterwards.
def retrieveWebPage(dir_suffix, callsign):
    '''curl -o <filename> <url>'''
    print('Entering \'retrieveWebPage()\' ...: ' + dir_suffix + '; ' + callsign)
    file = callsign + file_ext
    # Perform file collision check
    # if os.path.isfile(file):
        # print('ERROR: File \"' + file + '\" already exists.')
        # return False
    # Perform HTTP operation
    arg_list = [http_cmd, '-o', file, web_prefix + dir_suffix]
    http_proc = subprocess.run(arg_list, stderr=subprocess.PIPE, universal_newlines=True)
    # Check that the retrieval completed successfully
    if http_proc.returncode == 0:
        http_out_list = http_proc.stderr.splitlines()
        http_out_line = http_out_list[len(http_out_list)-1].split()
        if (int(http_out_line[0]) == 100 and int(http_out_line[1]) > 10000):
            if (os.path.isfile(file) and os.access(file, os.R_OK)):
                return True
            else:
                print('ERROR: rwp(): isfile() = ' + os.path.isfile(file))
                print('ERROR: rwp(): access() = ' + os.access(file, os.R_OK))
        else:
            print('ERROR: rwp(): http_out_line_0 = ' + str(http_out_line[0]))
            print('ERROR: rwp(): http_out_line_1 = ' + str(http_out_line[1]))
    return False

# Parse HTML file from Radio-Locator for latitude and longitude
# Requires HTML file already be downloaded and located in the working directory
# Returns or otherwise provides Latitude and Longitude in decimal form 
def parseRLFile(filename):
    # Check that passed-in file exists and is readable
    if (os.path.isfile(filename) and os.access(filename, os.R_OK)):
        # NO! RL_file = open(filename, 'r')
        # Prepare shell-out args
        arg_list = [regex_cmd, '-E', RL_regex, filename]
        # Shell-out to run process
        regex_proc = subprocess.run(arg_list, stdout=subprocess.PIPE, universal_newlines=True)
        # Check return code
        if regex_proc.returncode == 0:
        # Split lines of stdout
            regex_out_list = regex_proc.stdout.splitlines()
        # Check number of lines
            if len(regex_out_list) > 0:
                # Pick a line (ie: the first) and save to regex input
                regex_out_line = regex_out_list[0]
                # Run regex against input line
                lat_match = re.search(lat_regex, regex_out_line)
                long_match = re.search(long_regex, regex_out_line)
                # If regex is successful, read matches to lat and long vars
                if lat_match and long_match:
                    lat_num = lat_match.group(0)
                    long_num = long_match.group(0)
                    # Return composite string
                    return lat_num + ',' + long_num
                else:
                    print('regex matches failed!!')
            else:
                print('No lines match regex!!')
        else:
            print('grep returned non-zero!!')
            print('grep args: ')
            for line in regex_proc.args:
                print(line)
            # print('grep stderr: ' + str(regex_proc.returncode))
    else:
        print('Whoa! Something\'s wrong! Check Radio-Locator input file.')
        return False

# Parse HTML file from Radio-Locator for latitude and longitude
# Requires HTML file already be downloaded and located in the working directory
# Returns or otherwise provides Latitude and Longitude in decimal form 
def parseRLFile2(htmlfile):
    # Check that passed-in file exists and is readable
    if (os.path.isfile(htmlfile) and os.access(htmlfile, os.R_OK)):
        RL_file = open(htmlfile, 'r')
        for RL_line in RL_file:
            RL_match = re.search(RL_regex, RL_line)
            if RL_match:
                lat_match = re.search(lat_regex, RL_line)
                long_match = re.search(long_regex, RL_line)
                # If regex is successful, read matches to lat and long vars
                if lat_match and long_match:
                    lat_num = lat_match.group(0)
                    long_num = long_match.group(0)
                    # CLose file and return composite string
                    RL_file.close()
                    return lat_num + ',' + long_num
                else:
                    print('ERROR: regex matches failed!!')
            else:
                continue
        print('ERROR: No lines match regex!!')
    else:
        print('ERROR: No html file (' + htmlfile + ') available to parse.')
    RL_file.close()
    return None

########################
# BEGIN MAIN EXECUTION #
########################
# Check source list file exists and is readable
if not os.path.isfile(source_list) and os.access(source_list, os.R_OK):
    print('ERROR: Source list file not ready.')
    exit()

# Check if dest list file exists or not
if os.path.isfile(dest_list) and os.access(dest_list, os.W_OK):
    last_line_flag = False
else:
    last_line_flag = True

try:

# Open output file
    if last_line_flag == False:
        last_line = lastLineChk(dest_list)
        if last_line == None:
            print('ERROR: Failed to find last line in dest list file.')
            exit()
    output_file = open(dest_list, 'a')

# Open input file
    if (os.path.isfile(source_list) and os.access(source_list, os.R_OK)):
        input_file = open(source_list, 'r')
    else:
        print('Whoa! Something\'s wrong! Check input file.')

# ** Primary Loop **
    line_count = 0

    # Read a line from the input file
    for input_line in input_file:
        line_count = line_count + 1

        # Parse call-sign and URL
        web_dir = input_line.replace('\n', '')
        dir_items = web_dir.split('/')
        callsign = dir_items[2].replace('\n', '')
        # callsign2 = line_list[1].replace('\n', '')
        
        # Check if current source line matches dest last line
        # If not, skip ahead to next source line
        if not last_line_flag:
            if web_dir == last_line:
                last_line_flag = True
                continue
            else:
                continue

        # Retrieve article from wikipedia
        while not retrieveWebPage(web_dir, callsign):
            print('ERROR: Failed to retrieve web article: ' + web_prefix + web_dir)
            print('Perhaps hit limit from server. Backing off for ' + str(backoff_limit) + ' seconds.')
            time.sleep(backoff_limit)

        # Extract Geo-coordinates from wikipedia article file
        lat_long_out = parseRLFile2(callsign + file_ext)
        if not lat_long_out == None:
            lat_long_array = lat_long_out.split(',')
            lat_num = lat_long_array[0]
            long_num = lat_long_array[1]
            # Perhaps some decimal sanity checking here

            # Write line to output file
            output_file.write(lat_num + ',' + long_num + ',' + callsign + ',' + web_dir + '\n')
        else:
            print('ERROR: \'parseRLFile2()\' returned None.')

        # Clean-up after each iteration
        if not (os.path.isfile(callsign + file_ext) and os.access(callsign + file_ext, os.W_OK)):
            print('ERROR: Unable to delete HTML file: ' + callsign + file_ext)
            exit()
        os.remove(callsign + file_ext)

        # Sleep to avoid abusing the Radio-Locator server
        print('Note: waiting ' + str(rate_limit) + ' seconds before attempting next item.')
        time.sleep(rate_limit)

# ** End of Loop **

# Close output and input files
    print('Total source file line count: ' + str(line_count))
    input_file.close()
    output_file.close()

except OSError:
    print('Derp!! Caught an exception. ABORT!!')
    exit()

# Cool, we don't abort execution early.
print("Yay, we ran out of code. Success!!")