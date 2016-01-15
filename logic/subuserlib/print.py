#external imports
import sys
#internal imports
#import ...

def printWithoutCrashing(message):
  """
  Print to stdout any unicode string and don't crash even if the terminal has a weird encoding.
  """
  if not sys.stdout.encoding == "UTF-8": #TODO, utf-16 should also be supported.
    try:
      preppedMessage = message + u"\n"
      preppedMessage = preppedMessage.encode("utf8", 'surrogateescape')
      sys.stdout.buffer.write(preppedMessage) #Force utf-8, most terminals can handle it anyways
      sys.stdout.flush()
    except AttributeError:
      message = message.encode("ascii", 'replace')
      message = message.decode("ascii")
      print(message)
  else:
    print(message)
