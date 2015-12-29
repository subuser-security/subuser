#external imports
import sys
#internal imports
#import ...

def printWithoutCrashing(message):
  """
  Print to stdout any unicode string and don't crash even if the terminal has a weird encoding.
  """
  if not sys.stdout.encoding == "UTF-8": #TODO, utf-16 should also be supported.
    message += u"\n"
    message = message.encode("utf8", 'surrogateescape')
    sys.stdout.buffer.write(message) #Force utf-8, most terminals can handle it anyways
    sys.stdout.flush()
  else:
    print(message)
