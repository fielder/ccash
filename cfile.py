import re

import centry


def loadFromFile(path):
    fp = open(path, "r")
    if fp.readline().strip() != "CCASH":
        raise Exception("\"%s\" is not a valid file" % path)

    types = {}
    entries = []

    for line in fp:
        line = line.strip()

        if not line:
            continue

        if line.upper().startswith("TYPE"):
            m = re.compile("{([^}]+)}(.*)").match(line[4:].strip())
            types[m.group(1).strip()] = m.group(2).strip()

        elif line.upper().startswith("ENTRY"):
            entries.append(centry.CEntry(line[5:].strip()))

        else:
            raise Exception("invalid line")

    fp.close()

    return (types, entries)


def writeToFile(path, types, entries):
    fp = open(path, "w")

    fp.write("CCASH\n")

    for type_name, type_regex in types.iteritems():
        if type_regex:
            fp.write("TYPE {%s} %s\n" % (type_name, type_regex))
        else:
            fp.write("TYPE {%s}\n" % type_name)

    for e in entries:
        fp.write("ENTRY %s\n" % str(e))

    fp.close()
