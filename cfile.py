import re

import centry


def loadFromFile(path):
    fp = open(path, "r")
    if fp.readline().strip() != "CCASH":
        raise Exception("\"%s\" is not a valid file" % path)

    types = []
    entries = []
    autotypes = {}

    for line in fp:
        line = line.strip()

        if not line:
            continue

        if line.upper().startswith("TYPE"):
            types.append(line[4:].strip())

        elif line.upper().startswith("ENTRY"):
            entries.append(centry.CEntry(line[5:].strip()))

        elif line.upper().startswith("AUTOTYPE"):
            m = re.compile("{([^}]+)} (.+)").match(line[8:].strip())
            autotypes[m.group(2).strip()] = m.group(1)

        else:
            raise Exception("invalid line")

    fp.close()

    return (types, entries, autotypes)


def writeToFile(path, types, entries, autotypes):
    fp = open(path, "w")

    fp.write("CCASH\n")

    for t in types:
        fp.write("TYPE %s\n" % str(t))

    for e in entries:
        fp.write("ENTRY %s\n" % str(e))

    for regex, type_ in autotypes.iteritems():
        fp.write("AUTOTYPE {%s} %s\n" % (type_, regex))

    fp.close()
