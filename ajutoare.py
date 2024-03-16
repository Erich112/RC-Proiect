import binascii
import random

# DISCLAIMER: ACESTE FUNCTII AU FOST GANDITE PT O SINGURA INTREBARE SI UN SINGUR RASPUNS
# de facut pt mai multe intrebari si mai multe raspunsuri
addr = "1.2.3.4"


def DNSAnswer(Ctype='A', data=addr):
    Answer = ""
    Name = ""
    if Ctype == 'A':
        address = "target.local"
        Type = 1
    elif Ctype == 'PTR1':
        address = "_device-info._udp.local"
        Type = 12
    elif Ctype == 'PTR2':
        Type = 12
        address = "_services._dns-sd._udp.local"
    elif Ctype == 'TXT':
        Type = 16
        address = "FRTZPC._device-info._udp.local"

    RData = data

    addr_parts = address.split(".")
    for part in addr_parts:
        addr_len = "{:02x}".format(len(part))
        addr_part = binascii.hexlify(part.encode())
        Name += addr_len
        Name += addr_part.decode()
    Class = 1
    Name += "00"
    Answer += Name
    Answer += "{:04x}".format(Type)
    Answer += "{:04x}".format(Class)
    TTL = 60
    RDLength = len(RData)
    Answer += "{:04x}".format(TTL)
    addr_len = "{:04x}".format(RDLength)
    addr_part = binascii.hexlify(RData.encode())
    Answer += addr_len
    Answer += addr_part.decode()



def DNSpack(hasAnswers=0, resource=None, addr=None):
    # Building Header
    ID = random.randint(0, 65535)
    print(ID)
    QR = 1
    OPCODE = 0
    AA = 0
    TC = 0
    RD = 1
    RA = 0
    Z = 0
    RCODE = 0

    flags = str(QR)
    flags += str(OPCODE).zfill(4)
    flags += str(AA) + str(TC) + str(RD) + str(RA)
    flags += str(Z).zfill(3)
    flags += str(RCODE).zfill(4)
    flags = "{:04x}".format(int(flags, 2))

    QDCOUNT = not hasAnswers
    if hasAnswers == 0:
        ANCOUNT = 0
    else:
        ANCOUNT = 5

    NSCOUNT = 0
    ARCOUNT = 0

    Header = ""
    Header += "{:04x}".format(ID)
    Header += flags
    Header += "{:04x}".format(QDCOUNT)
    Header += "{:04x}".format(ANCOUNT)
    Header += "{:04x}".format(NSCOUNT)
    Header += "{:04x}".format(ARCOUNT)

    print(Header)
    if hasAnswers == 0:
        address = "_services._dns-sd._udp.local"
        # Building Questions
        Question = ""
        QName = ""
        QType = 1  # A
        QClass = 1  # IN

        addr_parts = address.split(".")
        for part in addr_parts:
            addr_len = "{:02x}".format(len(part))
            addr_part = binascii.hexlify(part.encode())
            QName += addr_len
            QName += addr_part.decode()

        QName += "00"

        Question += QName
        Question += "{:04x}".format(QType)
        Question += "{:04x}".format(QClass)
        print(Question)

        final = bytes(Header + Question)
        return final

    if hasAnswers > 0:
        # Building Answers
        Answer = ""
        Answer += DNSAnswer("PTR1", "FRTZPC._device-info._udp.local")
        Answer += DNSAnswer("PTR2", "FRTZPC._device-info._udp.local")
        Answer += DNSAnswer("TXT", resource)
        Answer += DNSAnswer("A", addr)

        print(Answer)

        final = bytes(Header + Answer)
        return final


def unpackDNS(data):
    ID = data[0:4]
    flags = data[4:8]
    QDCOUNT = data[8:12]
    ANCOUNT = data[12:16]
    NSCOUNT = data[16:20]
    ARCOUNT = data[20:24]
    flags = "{:b}".format(int(flags, 16)).zfill(16)
    QR = flags[0:1]
    OPCODE = flags[1:5]
    AA = flags[5:6]
    TC = flags[6:7]
    RD = flags[7:8]
    RA = flags[8:9]
    Z = flags[9:12]
    RCODE = flags[12:16]

    if QDCOUNT == 1:
        bitLung = data[24:26]
        print(bitLung)
        inceputadr = 26
        QNAME = ""
        while bitLung != b'00':
            lung = int(bitLung)
            print(lung)
            sfadr = inceputadr + (lung * 2)
            partAdr = binascii.unhexlify(data[inceputadr:sfadr]).decode()
            QNAME = QNAME + partAdr + "."
            print(partAdr)
            inceputadr = sfadr + 2
            bitLung = data[sfadr:inceputadr]
        QNAME = QNAME[:-1]
        print(QNAME)
        QTYPE = data[inceputadr:inceputadr + 4]
        print(QTYPE)
        QCLASS = data[inceputadr + 4:inceputadr + 8]
        print(QCLASS)

    if int(ANCOUNT) > 0:
        bitLung = data[24:26]
        print(bitLung)
        inceputadr = 26
        NAME = ""
        nrAns = ANCOUNT
        while int(nrAns) < 0:
            print("raspuns " + nrAns)
            while bitLung != b'00':
                lung = int(bitLung)
                sfadr = inceputadr + (lung * 2)
                partAdr = binascii.unhexlify(data[inceputadr:sfadr]).decode()
                NAME = NAME + partAdr + "."
                inceputadr = sfadr + 2
                bitLung = data[sfadr:inceputadr]
            NAME = NAME[:-1]
            print(NAME)
            TYPE = data[inceputadr:inceputadr + 4]
            print(TYPE)
            CLASS = data[inceputadr + 4:inceputadr + 8]
            print(CLASS)
            nrAns = nrAns - 1
            bitLung = data[inceputadr + 8:inceputadr + 10]
            TTL = data[inceputadr + 10: inceputadr + 14]
            RDLength = int(data[inceputadr+14:inceputadr+18],16)
            RDATA = binascii.unhexlify(data[inceputadr+18:inceputadr+(2*RDLength)]).decode()
            print(TTL)
            print(RDLength)
            print(RDATA)
            inceputadr = inceputadr+(2*RDLength)
            bitLung = data[inceputadr+(2*RDLength):inceputadr+(2*RDLength)+2]