#!/usr/bin/python3
import os
import configparser
import subprocess
from datetime import datetime

#A functon that prints and logs to file
def log(log_type, line):
    envvars = check_envvars()
    
    if envvars: 
        createLogFile = os.environ['CREATE_LOG_FILE']
        logfile = os.environ['LOGFILE']
        timeformat = os.environ['LOGTIMEFORMAT']
    else: 
        config = configparser.ConfigParser()
        config.read("./port_update.conf")
       
        createLogFile = config["logging"]["createLogFile"]
        timeformat = config["logging"]["logTimeFormat"]
        logfile = config["logging"]["logfile"]
    
    if createLogFile == "yes": 
        
        currtime = datetime.now().strftime(timeformat)
        with open(logfile, 'a', newline='') as f:
            f.write(f"{currtime} - {log_type.upper()} - {line}\n")
        
        print(f"{log_type.upper()} - {line}")

#a function that checks if enviroment variables are set
def check_envvars(): 
    variables = ["PATH_GLUETUN", "PATH_QBITTORRENT", "QBT_CONTAINER_ID", "CREATE_LOG_FILE", "LOGFILE", "LOGTIMEFORMAT"]
    try:

        for var in variables: 
            if not os.environ[var]:
                return False
        return True
    except:
        return False


#A function that checks values in config file
def check_config():
    #checking if path to gluetun and qbittorrent config is set in enviroment variable
    envvars = check_envvars()
    if envvars:
        result = file_exist(os.environ['PATH_GLUETUN'])
        result = file_exist(os.environ['PATH_QBITTORRENT'])
    #if not, read from config file and check 
    else: 
        config = configparser.ConfigParser()
        config.read("./port_update.conf")
        qbt_path = config["paths"]["qbittorrent"]
        gluetun_path = config["paths"]["gluetun"]
           
        result = file_exist(gluetun_path)
        result = file_exist(qbt_path)   

    return result

#a function that checks if file paths exist
def file_exist(filepath):
    log("info", f"Verifying the presence of {filepath}")
    if os.path.isfile(filepath): 
        log("info", f"Found {filepath}")
        return True
    else: 
        log("error", f"Did not find {filepath}")
        return False
    
#The function that updates the port. It reads both config files and compares value and updates.    
def update_port():
    #chech if enviroment variables are set
    envvars = check_envvars()
    if envvars: 
        gluetun_path = os.environ['PATH_GLUETUN']
        qbt_path = os.environ['PATH_QBITTORRENT']
        container_id = os.environ['QBT_CONTAINER_ID']
    else: 
        #if not, read from config file and check 
        config = configparser.ConfigParser()
        config.read("./port_update.conf")
        qbt_path = config["paths"]["qbittorrent"]
        gluetun_path = config["paths"]["gluetun"]
        container_id = config["docker"]["container_id"]
    
    log("info", f"Fetching port from {gluetun_path}")
    with open(gluetun_path, 'r') as file:
        port = str(file.readline().strip())

    log("info", f"Forward port is {port}")   

    log("info", f"Reading qBittorrent config file: {qbt_path}")
    with open(qbt_path, 'r') as file:
        lines = file.readlines()
    
    in_bittorrent_section = False
    updated_lines = []
    found_qbt_port = False
    update = False 
    for line in lines:
        # Check if we've entered or left the [BitTorrent] section
        if line.strip() == '[BitTorrent]':
            in_bittorrent_section = True
        elif line.startswith('[') and in_bittorrent_section:
            # If we encounter another section while in the [, we've left the [BitTorrent] section
            in_bittorrent_section = False
        
        # If we're in the [BitTorrent] section and find the Session\Port line, update it
        if in_bittorrent_section and 'Session\\Port=' in line:
            log("info", line.strip())
            old_port = line.split('=')[1].strip()
            found_qbt_port = True
            if old_port != port:
                update = True
                updated_line = 'Session\\Port=' + port + '\n'
                updated_lines.append(updated_line)
                log("info", f"Forward port has changed! Updating qBittorrent.conf") 
            else:
                log("info", f"Forward port is unchanged! No changes made to qBittorrent.conf")    
        else:
            updated_lines.append(line)
    
    # Write the modified contents back to the file
    if update == True: 
        docker_qbittorrent("stop", container_id)
               
        with open(qbt_path, 'w') as file:
            file.writelines(updated_lines)

        log("info", f"Session\\Port updated with value {port}") 
        docker_qbittorrent("start", container_id)

    if found_qbt_port == False: 
        log("error", f"Could not find Session\\Port in qBittorrent.conf")   

def docker_qbittorrent(action, container_id):
    command = ["docker", action, container_id]
    # Run the command
    log("info", f"Executing: docker {action} {container_id}") 
    result = subprocess.run(command, capture_output=True, text=True)

    # Check the result
    if result.returncode == 0:
        log("info", f"Container {action} successful")
        log("info", f"Execution output: {result.stdout.strip()}")
    else:
        log("error", f"Could not {action} container")
        log("error", f"Execution output: {result.stderr.strip()}")


def main():
    
    # Get the absolute path to the directory containing the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Change the current working directory to the script directory
    os.chdir(script_dir)
    
    log("info", f"qBittorrent Port Update started...")  
    if not check_config():
        SystemExit()
    else: 
        update_port()
        log("info", f"qBittorrent Port Update completed")  

if __name__ == "__main__":
    main()
