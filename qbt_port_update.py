#!./venv/bin/python3
import sys
import os
import configparser
import docker
import requests
from datetime import datetime

#A function that checks execution arguments and exits
def checkargs():
    script_name = "qBittorrent Port Update"
    version = "2.1.5"
    if len(sys.argv) !=1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print(f"Usage: {sys.argv[0]} [OPTION]")
            print("Fetches the forwarded port from a running Gluetun container and")
            print("dynamically updates the qBittorrent container's configuration to use this port.")
            print("")
            print("-v, --version   Display version information")
            print("-h, --help      Display this help text")
            print("")
            exit()

        if  sys.argv[1] == "--version" or sys.argv[1] == "-v":
            print(f"{script_name}")
            print(f"v.{version}")
            print("")
            exit()

        print(f"Usage: {sys.argv[0]} [OPTION]")
        print("Fetches the forwarded port from a running Gluetun container and")
        print("dynamically updates the qBittorrent container's configuration to use this port.")
        print("")
        exit()
    

#A function that tries to read port_update.conf from the scripts execution folder or /config
def readConfigFile():
    config = configparser.ConfigParser(interpolation=None)
    
    #config file in scripts execution folder will be prioritized
    if os.path.isfile("./port_update.conf"):
        config.read("./port_update.conf")
        return config
    
    #check if there is a config file in /config (docker containers configuration folder) 
    if os.path.isfile("/config/port_update.conf"):
        config.read("/config/port_update.conf")
        return config
    
    return False
   

#A functon that prints and logs to file
def log(log_type, line):
    envvars = check_envvars()
    if envvars: 
        createLogFile = os.environ['CREATE_LOG_FILE']
        logfile = os.environ['LOGFILE']
        timeformat = os.environ['LOGTIMEFORMAT']
    else: 
        config = readConfigFile()

        createLogFile = config["logging"]["createLogFile"]
        timeformat = config["logging"]["logTimeFormat"]
        logfile = config["logging"]["logfile"]
    
    currtime = datetime.now().strftime(timeformat)
    print(f"{currtime} - {log_type.upper()} - {line}")
    
    if createLogFile == "yes": 
        with open(logfile, 'a', newline='') as f:
            f.write(f"{currtime} - {log_type.upper()} - {line}\n")


# A function that checks if environment variables are set for either option 1 or option 2
def check_envvars():
    # Dictionary of environment variables for each option
    envvars_dict = {
        1: [
            "PATH_GLUETUN", 
            "PATH_QBITTORRENT", 
            "QBT_CONTAINER_ID", 
            "CREATE_LOG_FILE", 
            "LOGFILE", 
            "LOGTIMEFORMAT"
        ],
        2: [
            "GLUETUN_IP",
            "GLUETUN_PORT",
            "GLUETUN_USER",
            "GLUETUN_PASS",
            "PATH_QBITTORRENT",
            "QBT_CONTAINER_ID",
            "CREATE_LOG_FILE",
            "LOGFILE",
            "LOGTIMEFORMAT"
        ]
    }
    
    # Check each option
    for envvars in envvars_dict.values():
        # Use all() to check if all the environment variables for the current option are set
        if all(os.environ.get(var) for var in envvars):
            return True  
    
    # If neither option has all variables set, return False
    return False


#A function that checks values in the config file
def check_config():
    #Try to read config file
    config = readConfigFile()
    if config: 
        sections = ['paths', 'docker', 'gluetun', 'logging']
        gluetun_options = ['gluetun_ip', 'gluetun_port', 'gluetun_user', 'gluetun_pass']
        logging_options = ['createlogfile', 'logfile', 'logtimeformat']
        paths_options = ['gluetub', 'qbittorrent']
        docker_options = ['container_id']
        
        for section in sections: 
            #has_section = config.has_section(section)
            match section: 
                case "paths":
                    for option in paths_options: 
                        has_option = config.has_option(section, option)
                        if not has_option: 
                            if option == "gluetun": 
                                has_option = config.has_option("gluetun", "gluetun_ip")
                                if not has_option: 
                                    return False
                                has_option = config.has_option("gluetun", "gluetun_port")
                                if not has_option: 
                                    return False
                                has_option = config.has_option("gluetun", "gluetun_user")
                                if not has_option: 
                                    return False
                                has_option = config.has_option("gluetun", "gluetun_pass")
                                if not has_option: 
                                    return False
                            if option == "qbittorrent":
                                return False
                
                case "docker": 
                    for option in docker_options: 
                        has_option = config.has_option(section, option)
                        if not has_option:
                            return False

                case "gluetun": 
                    for option in gluetun_options: 
                        has_option = config.has_option(section, option)
                        if not has_option: 
                            has_option = config.has_option("paths", "gluetun")
                            if not has_option: 
                                return False

                case "logging": 
                    for option in logging_options: 
                        has_option = config.has_option(section, option)
                        if not has_option:
                            return False
        
        #Config file looks good
        return True
    else: 
        #unable to read config file
        return False


#a function that checks if file paths exist
def file_exist(filepath):
    log("info", f"Verifying the presence of {filepath}")
    if os.path.isfile(filepath): 
        log("info", f"Found {filepath}")
        return True
    else: 
        log("error", f"Did not find {filepath}")
        return False


def check_gluetun_port(gluetun_path, gluetun_ip, gluetun_port, gluetun_user, gluetun_pass):
    if gluetun_path:
        log("info", f"Fetching port from {gluetun_path}")
        try: 

            with open(gluetun_path, 'r') as file:
                port = str(file.readline().strip())
        
        except Exception as e:
            log("error", f"Unable to fetch port from {gluetun_path}: {str(e)}")
            exit()

        return port

    else: 
        
        log("info", f"Fetching forwarded port from Gluetun Control Server on IP: {gluetun_ip}:{gluetun_port}")
        
        try: 
            response = requests.get(f'http://{gluetun_ip}:{gluetun_port}/v1/portforward', auth=(gluetun_user, gluetun_pass))
       
        except Exception as e:
            log("error", f"Unable to fetch forwarded port from Gluetun Control Server: {str(e)}")
            exit()

        if response.status_code == 200:
            data = response.json()
            port = data['port']
            return port

        if response.status_code == 401:
            log("error", f"Unable to fetch forwarded port from Gluetun Control Server: 401 Unauthorized")
            exit()
        
        if response.status_code == 403:
            log("error", f"Unable to fetch forwarded port from Gluetun Control Server: 403 Forbidden")
            exit()
        else:
            return False
 

#The function that updates the port. It reads both config files and compares value and updates.    
def update_port():
    #chech if enviroment variables are set
    envvars = check_envvars()
    if envvars: 
        qbt_path = os.environ['PATH_QBITTORRENT']
        container_id = os.environ['QBT_CONTAINER_ID']
        try: 
            gluetun_ip = os.environ['GLUETUN_IP']
            gluetun_port = os.environ['GLUETUN_PORT']
            gluetun_user = os.environ['GLUETUN_USER']
            gluetun_pass = os.environ['GLUETUN_PASS']
        except: 
            gluetun_path = os.environ['PATH_GLUETUN']
            gluetun_ip = False 

        try: 
            gluetun_path = os.environ['PATH_GLUETUN']
        except: 
            gluetun_ip = os.environ['GLUETUN_IP']
            gluetun_port = os.environ['GLUETUN_PORT']
            gluetun_user = os.environ['GLUETUN_USER']
            gluetun_pass = os.environ['GLUETUN_PASS']
            gluetun_path = False 
    else: 
        #if not, read from config file and check 
        config = readConfigFile()
        
        qbt_path = config["paths"]["qbittorrent"]
        
        #checking if path to gluetune forwarded port is set, if not fetch ip and port
        try: 
            gluetun_ip = config["gluetun"]["gluetun_ip"]
            gluetun_port = config["gluetun"]["gluetun_port"]
            gluetun_user = config["gluetun"]["gluetun_user"]
            gluetun_pass = config["gluetun"]["gluetun_pass"]
        except: 
            gluetun_path = config["paths"]["gluetun"]
            gluetun_ip = False

        try:                                  
            container_id = config["docker"]["container_id"]
        except: 
            log("ERROR", f"Unable to container_id from port_update.conf")
            exit()
    

    if gluetun_ip:
        port = check_gluetun_port("", gluetun_ip, gluetun_port, gluetun_user, gluetun_pass)
        if not port:
            log("ERROR", f"Unable to fetch port from Gluetun Control Server")
            exit()
            #port = check_gluetun_port(gluetun_path, "", "")
    else: 
        port = check_gluetun_port(gluetun_path, "", "", "", "")
        
    if not port: 
        log("ERROR", f"Unable to fetch forwarded port from Gluetun")
        exit()

    else: 
        log("info", f"Forwarded port is {port}")   

    "making the port into a string" 
    port = str(port) 

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
                updated_line = f"Session\\Port={port}\n"
                updated_lines.append(updated_line)
                log("info", f"Forwarded port has changed! Updating qBittorrent.conf") 
            else:
                log("info", f"Forwarded port is unchanged! No changes made to qBittorrent.conf")    
        else:
            updated_lines.append(line)
    
    # Write the modified contents back to the file
    if update == True: 
        docker_qbittorrent("stop", container_id)
        try:        
            with open(qbt_path, 'w') as file:
                file.writelines(updated_lines)

            log("info", f"Session\\Port updated with value {port}") 
        
        except Exception as e:
            log("error", f"Error writing to qBittorrent.conf: {str(e)}")
            exit()
            
        
        docker_qbittorrent("start", container_id) 
        

    if found_qbt_port == False: 
        log("error", f"Could not find Session\\Port in qBittorrent.conf")   
        exit()

#a function that stops, starts or restarts a docker containers
def docker_qbittorrent(action, container_id):
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')

    try:
        # Restart the container
        container = client.containers.get(container_id)
        match action: 
            case "stop":
                log("info", f"Stopping container {container_id}") 
                container.stop()
                log("info", f"Container successfully stopped!")
            case "start":
                log("info", f"Starting container {container_id}") 
                container.start()
                log("info", f"Container successfully started!")
            case "restart":
                log("info", f"Restarting container {container_id}") 
                container.restart()
                log("info", f"Container successfully restarted!")
        
        
    except docker.errors.NotFound:
        log("error", f"Container {container_id} not found")
        exit()    
    
    except Exception as e:
        if action == "stop": 
            log("error", f"Error stopping container {container_id}: {str(e)}")
        else: 
            log("error", f"Error {action}ing container {container_id}: {str(e)}")

        exit()    


def main():

    #check arguments, print helptext and exit if invalid
    checkargs()

    # Get the absolute path to the directory containing the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Change the current working directory to the script directory
    os.chdir(script_dir)
    
    if not check_config() and not check_envvars():
            print("Unable to read qBittorrent Port Update configuration!")
            print("Configuration can be set in port_update.conf or as enviroment variables.") 
            print("See https://github.com/royborgen/qbt_port_update for more information.")  
            SystemExit()
    else: 
        log("info", f"qBittorrent Port Update started...")  
        update_port()
        log("info", f"qBittorrent Port Update completed")  

if __name__ == "__main__":
    main()
