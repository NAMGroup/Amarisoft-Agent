import json
import subprocess
# from common import agent_logging
import time
# global variable containing callbacks
callbacks = {}

# API for registering callbacks
def register_callback(event, callback):
    if event not in callbacks:
        callbacks[event] = callback
        print("in here")
    else:
        print("Already reguistered")

# a function that is called when some event is triggered on an object
def process_event(event,debug_mode,params):
    if  event in callbacks:
        # this object/event pair has a callback, call it
        callback = callbacks[event]
        print("Callback registered-->", callback)
        print(debug_mode)
        callback(debug_mode,params)
    else:
        print("No callback registered")
        return False


def _execCMD(action_command,debug_mode=False):
    process=None
    #process = subprocess.Popen(['echo', self.action_command], 
#    process = subprocess.Popen(["echo \"", action_command,"\" >>./test.txt"],
    print(type(action_command))
    print(action_command)
    if debug_mode:
        process = subprocess.Popen(["echo \""+ str(action_command)+"\" >>../test.txt"],
        # process = subprocess.Popen([action_command],
                            #we need shell= true to pass the command as string and not as list
                            shell=True, 
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    else:
        # process = subprocess.Popen(["echo \""+ str(action_command)+"\" >>../test.txt"],
        process = subprocess.Popen([action_command],
                    #we need shell= true to pass the command as string and not as list
                    shell=True, 
                    stdout=subprocess.PIPE,
                    universal_newlines=True)

    while True:
        output = process.stdout.readline()
        print(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            print('RETURN CODE', return_code)
            # Process has finished, read rest of the output 
            for output in process.stdout.readlines():
                print(output.strip())
            break

def touch(debug_mode,params):
    time_now = time.strftime("%Y%m%d-%H%M%S")
    fileName="./shared/"+'_'.join(["test",time_now]);
    if params is not None:
        if "filename" in params:
            fileName=params["filename"]
    cmd2send="touch "+fileName
    _execCMD(cmd2send)    
    # _execCMD("echo touch > ./docker_command.txt ")    
    # _execCMD("ls -la")    


def echo(debug_mode,params):
    time_now = time.strftime("%Y%m%d-%H%M%S")
    fileName="./shared/default.echo"
    msg=time_now
    if params is not None:
        if "filename" in params:
            fileName=params["filename"]
        if "message" in params:
            print("here")
            msg=msg +":"+params["message"]
    cmd2send="echo TEST:11111"+msg + " >> ./" + fileName
    print(msg)
    _execCMD(cmd2send)    
    # _execCMD("echo 'papajohn' >>./test.txt ; echo $(date -u) >>./test.txt ")    

def write_conf_file(params):
    #clear file contents
    with open("./shared/myconf.cfg", 'a+') as conf:
        conf.truncate(0)

    #start wirtitng file
    for param in params:
        if param in params:
            with open("./shared/myconf.cfg", mode="a") as conf:
                if param in ["PRMT_AMF_ADDR","PRMT_GTP_ADDR" , "PRMT_PLMN" , "PRMT_MOD_UL" , "PRMT_MOD_DL"]:
                    conf.write("#define  {} \"{}\"\n".format(param,params[param]))
                else:
                    conf.write("#define  {} {}\n".format(param,params[param]))

        else:
            print("Yeah  this param is not available... ",param)

def stop(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl stop lte"
    
    _execCMD(cmd2send)    
 

def start(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl start lte"
    if params is not None:
        write_conf_file(params)
    _execCMD(cmd2send)    


def restart(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl restart lte"
    if params is not None:
       write_conf_file(params)
    _execCMD(cmd2send)    


    
