
#TODO: Some NAME and MEMO fields hame "&amp;" strings in there to represent &
#      Replace with a single &

def parseTransactionsFromFile(path):
    """
    Parse the transactions out of a QFX file.

    File format:

    ...
    ...
    VERSION:102
    ...
    ...
    <STMTTRN>
    <TRNTYPE>DEBIT
    <DTPOSTED>20120710120000[0:GMT]
    <TRNAMT>-142.00
    <FITID>201207100
    <NAME>THE HAY MERCHANT HOUSTON
    <MEMO>07/09THE HAY M
    </STMTTRN>
    ...
    ...
    """

    stmttrn = None
    ret = []
    for line in open(path, "r"):
        line = line.strip()

        if line.startswith("VERSION:"):
            version = int(line[8:])
            if version != 102:
                raise Exception("invalid file version %d" % version)

        elif stmttrn is not None:
            if line == "</STMTTRN>":
                ret.append(stmttrn)
                stmttrn = None
            else:
                gidx = line.index(">")
                stmttrn[line[1:gidx]] = line[gidx + 1:]

        elif line == "<STMTTRN>":
            stmttrn = {}

        else:
            # not in a statement transaction, ignore the line
            pass

    return ret


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        transactions = parseTransactionsFromFile(sys.argv[1])
        for t in transactions:
            print t
        print ""
        print "%d transactions" % len(transactions)
