from urllib import urlencode
import httplib2


# full GET URL example:
# https://g1m.me/send_sms?messageText=hello&deviceAddress=919880700000&password=847yhhgfj
# should return "OK"

GATEWAY_URL = "https://g1m.me/send_sms"
# GATEWAY_URL = "http://127.0.0.1:30824/send_sms"

OVI_NUM_FROM = "919900095039"

def send_sms(deviceAddress, messageText, _from):
    """ Send an SMS to the given deviceAddress phone.
    Considering we send only messages to India, we add the India prefix here.
    
    deviceAddress: cellphone number in India only
    messageText: content of SMS
    _from: cellphone number for the 'from' phone
    """
    # Fix the number if necessary
    if len(deviceAddress)==10:
        deviceAddress = "91"+deviceAddress # India country code
    elif deviceAddress[0:4]=="0091":
        deviceAddress = deviceAddress[2:]

    data = {'deviceAddress':deviceAddress,
            'messageText':  messageText,
            'fromAddress':  _from and _from or OVI_NUM_FROM,
            'password':     "847yhhgfj",
            }
    http = httplib2.Http()
    resp, content = http.request(GATEWAY_URL + "?" + urlencode(data), "GET")
    if content and content[0:2]=="OK":
        return True
    return False
    

if __name__=="__main__":
    TEST_NUM = "919880703078" #91-98807-03078 Verisign guy
    # TEST_NUM = "919586550654" # NEIL
    TEST_NUM = "919880700000" # FAKE

    send_sms(TEST_NUM,"Test from Agathe/Nokia. Thanks!!", OVI_NUM_FROM)
    
    