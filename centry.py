import re

#FIXME: We use { and } as delimiters when converting an entry to a string,
#       but don't worry about escaping. This breaks the reverse conversion.


class CEntry(object):
    def __init__(self, from_string=""):
        self.type = ""
        self.uid = ""
        self.date = ""
        self.amount = 0.0
        self.description = ""

        if from_string:
            self.takeFromString(from_string)

    def __str__(self):
        return "%s %s %s {%s} %s" % (self.uid, self.date,
                                     self.amount, self.type,
                                     self.description)

    def takeFromString(self, s):
        m = re.compile("([^ ]+) ([^ ]+) ([^ ]+) {([^}]*)} (.*)").match(s)

        self.uid = m.group(1)
        self.date = m.group(2)
        self.amount = float(m.group(3))
        self.type = m.group(4)
        self.description = m.group(5)


def CEntryFromQFX(qfx_stmttrn):
    c = CEntry()

    # unique identifier
    c.uid = qfx_stmttrn["FITID"]

    # date
    y = qfx_stmttrn["DTPOSTED"][0:4]
    m = qfx_stmttrn["DTPOSTED"][4:6]
    d = qfx_stmttrn["DTPOSTED"][6:8]
    if "MEMO" in qfx_stmttrn:
        # Some entries have a MEMO that begin with a month and date
        # telling more accurately when the transaction occurred. Use
        # that month/day if avaialable.
        match = re.compile("(\\d)/(\\d)").match(qfx_stmttrn["MEMO"])
        if match:
            m = match.group(1)
            d = match.group(2)
    c.date = "%s/%s/%s" % (m, d, y)

    # amount
    c.amount = float(qfx_stmttrn["TRNAMT"])

    # description
    if "MEMO" in qfx_stmttrn:
        c.description = "%s (%s)" % (qfx_stmttrn["NAME"], qfx_stmttrn["MEMO"])
    else:
        c.description = qfx_stmttrn["NAME"]

    return c
