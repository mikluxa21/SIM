from numpy.random import random
from smartcard.util import toHexString, toBytes
from smartcard.ATR import ATR
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver

from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker
from smartcard.sw.SWExceptions import SWException, WarningProcessingException

import time
import random

# https://www.programmersought.com/article/83975420589/
"""EF-ICCID （2FE2): ICC Identification, the identity ID of the SIM card EF-LP（6F05): Language Preference, 
language preference EF-IMSI（6F07): International Mobile Subscriber Identity, the authentication ID for accessing the 
operator's network EF-KC（6F20): Ciphering Key kc, the encryption key for network registration EF-SST（6F3 8): SIM 
Service Table, a list of services provided by operators, such as ADN, FDN, SMS, etc. EF-ACM（6F39) : Accumulated Call 
Meter - total number of units for both the current call and the preceding calls EF-GID1（6F3E) : Group Identifier 
Level 1 - identifiers for particular SIM-ME associations EF-GID2（6F3F) : Group Identifier Level 2 EF-SPN（6F46): 
Service Provider Name, operator name EF-MSISDN（6F40): Mobile Station International ISDN number (O)EF-CBMI : Cell 
Broadcast Message Identifier Selection - Message format accepted by MS EF-BCCH（6F74) : Broadcast Control Channels 
EF-ACC（6F78) : Access Control Class - The access control class is a parameter to control the RACH utilisation. 
EF-FPMLN（6F7B) : Forbidden PMLNs EF-LOCI（6F7E): Location Infomation, location information Temporary Mobile Subscriber 
Identity (TMSI) Location Area Information (LAI) TMSI TIME Location update status EF-AD（6FAD) : Administrative Data - 
This EF contains information concerning the mode of operation according to the type of SIM, such as normal (to be 
used by PLMN subscribers for GSM operations), type approval (to allow specific use of the ME during type approval 
procedures of e.g. the radio equipment), cell testing (to allow testing of a cell before commercial use of this 
cell), manufacturer specific (to allow the ME manufacturer to perform specific proprietary auto-test in its ME during 
e.g. maintenance phases). EF-Phase（6FAE) : Phase Identification (O)EF-ADN（6F3A) : Abbreviative Dialing Number (
O)EF-FDN（6F3B) : Fixed Dialing Number (O)SF-SMS（6F3C) : Short Message (O)EF-CCP（6F3D) : Capability Configuration 
Parameters - parameters of required network and bearer capabilities and ME configurations associated with a call 
established using an abbreviated dialling number, a fixed dialling number, MSISDN or a last number dialled. (
O)EF-LND（6F44) : Last number dialled"""

GET_RESPONSE = [00, 0XC0, 00, 00]
SELECT = [0x00, 0xA4, 0x08, 0x04, 0x02]
SELECT2 = [0x00, 0xA4, 0x04, 0x05, 0x10]
SELECT3 = [0x00, 0xA4, 0x00, 0x04, 0x02]
STATUS = [0xA0, 0xF2, 0x00, 0x00, 0x22]
RUN_ALG = [0x00, 0x88, 0x00, 0x81, 0x22]
READREC = [0x00, 0xB2, 0x01, 0x04]
READ_BIN = [0x00, 0xB0, 0x00, 0x00]

#RAND = [0x01, 0x02, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02]
def randhex():
    res = []
    for i in range(32):
        res.append(int("0x" + str(random.choice("0123456789ABCDEF")) + str(random.choice("0123456789ABCDEF")), 0))
    return res
RAND = randhex()

MF = [0x3F, 0x00]
MF2 = [0x2F, 0x00]
AB = [0x6F, 0x3A]
SMS = [0x6F, 0x3C]
ICCID = [0x2F, 0xE2]
COMMAND = [0x00, 0x00, 0x00, 0x00, 0x00]
EMPTY_PARMS = [0x00, 0x00, 0x00]
GSM_CLA = [0xA0]

PREFIX_MASTER_FILE = [0x3F]
PREFIX_DEDICATED_FILE = [0x7F]
PREFIX_ELEMENTARY_FILE_UNDER_MF = [0x2F]
PREFIX_ELEMENTARY_FILE_UNDER_DF = [0x6F]

DF_GSM = PREFIX_DEDICATED_FILE + [0x20]


def get_nth_byte(response, n):
    if len(response) > n:
        nth_byte = response[n]
        return nth_byte
    else:
        return None


def find_byte(response, target_byte):
    target_byte = 160
    try:
        index = response.index(target_byte)
    except ValueError:
        return None
    if index + 15 <= len(response):
        following_bytes = response[index :index + 16]
        return following_bytes
    else:
        return None


def make_list(n):
    if hasattr(n, '__iter__'):
        return n
    else:
        return [n]


def main():
    global READREC
    global READ_BIN
    print('Insert a card within 10 seconds')

    # request any card type
    cardtype = AnyCardType()
    cardrequest = CardRequest(timeout=10, cardType=cardtype)
    cardservice = cardrequest.waitforcard()

    # use ISO7816-4 and ISO7816-8 error checking strategy
    # first check iso7816_8 errors, then iso7816_4 errors
    errorchain = []
    errorchain = [ErrorCheckingChain(errorchain, ISO7816_9ErrorChecker())]
    errorchain = [ErrorCheckingChain(errorchain, ISO7816_8ErrorChecker())]
    errorchain = [ErrorCheckingChain(errorchain, ISO7816_4ErrorChecker())]
    cardservice.connection.setErrorCheckingChain(errorchain)

    # filter Warning Processing Exceptions (sw1 = 0x62 or 0x63)
    cardservice.connection.addSWExceptionToFilter(WarningProcessingException)

    # attach the console tracer
    observer = ConsoleCardConnectionObserver()
    cardservice.connection.addObserver(observer)

    # connect to the card and perform a few transmits
    cardservice.connection.connect()

    atr = ATR(cardservice.connection.getATR())
    """
    print(atr)
    print('historical bytes: ', toHexString(atr.getHistoricalBytes()))
    # print('checksum: ', "0x%X" % atr.getChecksum())
    # print('checksum OK: ', atr.checksumOK)
    print('T0  supported: ', atr.isT0Supported())
    print('T1  supported: ', atr.isT1Supported())
    print('T15 supported: ', atr.isT15Supported())"""

    try:
        apdu = SELECT + MF2
        response, sw1, sw2 = cardservice.connection.transmit(apdu)
        if sw1 == 0x61:
            apdu = GET_RESPONSE + [sw2]
            response, sw1, sw2 = cardservice.connection.transmit(apdu)
            NTH_RESP = bytes([response[7]])
            READREC += NTH_RESP
            cardservice.connection.transmit(READREC)
            response, sw1, sw2 = cardservice.connection.transmit(READREC)
            NTH_BYTES = find_byte(response, [160])
            if NTH_BYTES:

                apdu = SELECT2 + NTH_BYTES
                response, sw1, sw2 = cardservice.connection.transmit(apdu)
            apdu = GET_RESPONSE + [sw2]
            response, sw1, sw2 = cardservice.connection.transmit(apdu)
            apdu = SELECT3 + [0x6F, 0x07]
            response, sw1, sw2 = cardservice.connection.transmit(apdu)
            apdu = GET_RESPONSE + [sw2]
            response, sw1, sw2 = cardservice.connection.transmit(apdu)
            NTH_RESP = bytes([response[7]])
            READ_BIN += NTH_RESP
            apdu = READ_BIN
            response, sw1, sw2 = cardservice.connection.transmit(apdu)
            apdu = RUN_ALG + [0x10] + RAND[:16] + [0x10] + RAND[0:]
            response, sw1, sw2 = cardservice.connection.transmit(apdu)
    except SWException as e:
        print(str(e))
    return RAND



    cardservice.connection.disconnect()

if __name__ == "__main__":
    main()