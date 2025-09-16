#!python

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, subprocess
import  struct, io, traceback, hashlib, traceback, argparse
import  codecs, re

base = os.path.dirname(os.path.realpath(__file__))

__doc__ = \
'''
The testcase file is python code, defining an array of tests.
Python comments are OK. Syntax errors are reported.
File Format:
[
  [ ContextStr, SendStr, ExpectStr, FindStr ], # optional comment
]
Where the items are:
   Context_String,     Send_String,   Expect_String,   Find/Compare
   -----------------   ------------   --------------   ------------
   info for the user   what to send   what to expect   True if Find
                                                       False if Match
Example test case file:
[
    [ "Echo Command", "", "", True],         # NOOP
    [ "Test ls", "ls", "Make", True],        # Do we have a Make file
    [ "DF command", "df", "blocks", True ],  # Any 'blocks' string in the
    [ "Exact", "ls -d /.", ".", False ], # Any 'blocks' string in the
]
FindStr field accepts:
        True,       False,      "regex"       "mregex"
        ----        ---------   ----------    -----------
        Find str    Match str   Find regex    Match regex'''

VERSION = "1.2.3"
def_testfile = "testcase.txt"

def pp(strx):
    return "'" + str(strx) + "'"

# ------------------------------------------------------------------------
# Print( an exception as the system would print it)

def print_exception(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print("Could not print trace stack. ", sys.exc_info())
    print( cumm)

def strdiff(expectx, actualx):

    ''' Rudimentary info on string differences '''

    print("strdiff()", str(expectx), str(actualx))

    strx = ""
    for cnt, bb in enumerate(expectx):
        #print("cnt", cnt, bb)
        if bb != actualx[cnt]:
            strx = "At pos: %d  [%s]" % (cnt,
                            str(expectx[cnt:cnt+5]))
            break
    return strx

def xdiff(actualx, expectx, findflag):

    ''' Compare values, display string in Color
        Sensitive to find flag.
    '''

    if type(findflag) == type(""):
        if "mregex" in findflag :
            #print("Match regex", str(expectx), str(actualx))
            rex = re.compile(str(expectx))
            if rex.match(str(actualx)):
                return "\033[32;1mOK\033[0m"
            else:
                return"\033[31;1mERR\033[0m"
        elif "regex"  in findflag:
            #print("Find regex", str(expectx), str(actualx))
            rex = re.compile(str(expectx))
            if rex.search(str(actualx)):
                return "\033[32;1mOK\033[0m"
            else:
                return"\033[31;1mERR\033[0m"
        else:
            print("Warn: Invalid find flag string", findflag)
    elif findflag:
        #print("Find", str(expectx), str(actualx))
        if str(expectx) in str(actualx):
            return "\033[32;1mOK\033[0m"
        else:
            return"\033[31;1mERR\033[0m"
    else:
        if expectx == actualx:
            return "\033[32;1mOK\033[0m"
        else:
            return"\033[31;1mERR\033[0m"

def obtain_response(cmd):

    ''' Get output from command, if any '''

    comm = [0,]
    exec = cmd.split()
    if args.debuglev > 0:
        print("exec:", exec)

    if exec:
        try:
            ret = subprocess.Popen(exec, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            comm = ret.communicate()
            if args.outp:
                print(codecs.decode(comm[0]).replace("\\n", "\n"))
                sys.stdout.flush()
        except:
            print("Cannot communicate with:", exec, file=sys.stderr)
            #print(sys.exc_info())
            print_exception("exec")

    return comm[0]

def fill(strx, wantlen):
    return  strx + " " * (wantlen - len(strx))

def send_expect(context, sendx, expectx, findflag):

    ''' Evaluate one SEND -- EXPECT sequence '''

    ret = obtain_response(sendx)
    if args.debuglev > 1:
        print("\033[32;1mGot: ", ret, "\033[0m")

    err = xdiff(ret, expectx, findflag)

    # If no context, we do not want any printing
    if context:
        print(fill(context, args.fill), "\t", err)

    if args.verbose > 1:
        # On error tell us the expected result
        if ret != expectx:
            print("\033[34;1mGot:\033[0m\n", ret)

    if args.verbose > 2:
        if ret != expectx:
            print("\033[34;1mExpected:\033[0m\n", expectx)

    if args.verbose > 3:
        print("\033[34;1mSend\033[0m:", pp(sendx))
        #if ret != expectx:
        #    print("\033[34;1mDiff:\033[0m\n",
        #        strdiff(ret, expectx))

    return err

def mainloop():

    #global args

    if args.test_cases:
        for fff in args.test_cases:
            lineno = 0
            try:
                with open(fff) as fp:
                    testx = fp.read()
                    if args.show_case:
                        print("testx:", testx)
                try:
                    test_case_code = eval(testx)
                except:
                    #print("Error in", fff, sys.exc_info(), file=sys.stderr)
                    print_exception("Eval code error in '%s' '%s'\n" % \
                                                    (fff, sys.exc_info()[0]) )
                    args.errcnt += 1
                    continue
            except:
                print("Cannot open file", "'" + fff  + "'", file=sys.stderr)
                args.errcnt += 100
                #sys.exit()
                continue
            #print("testx", testx)

            for aa in test_case_code:
                err = send_expect(aa[0], aa[1], aa[2], aa[3])
                #print("err", err)
                if "ERR" in err:
                    args.errcnt += 1

pdesc = 'Test with send/expect by executing sub commands from test case scripts.'
pform = "For info on TestCase File Format use -A option.\n" + \
        "The file 'testcase.txt' is executed by default."

def mainfunct():

    global args

    parser = argparse.ArgumentParser( description=pdesc, epilog=pform)

    parser.add_argument("-V", '--version', dest='version',
                        default=0,  action='store_true',
                        help='Show version number')
    parser.add_argument("-o", '--outp', dest='outp',
                        default=0,  action='store_true',
                        help='Show communication with program')
    parser.add_argument("-A", '--info', dest='info',
                        default=0,  action='store_true',
                        help='Show testcase file format info')
    parser.add_argument("-v", '--verbose', dest='verbose',
                        default=0,  action='count',
                        help='increase verbocity (Default: none)')
    parser.add_argument("-d", '--debug', dest='debuglev',
                        default=0,  action='store', type=int,
                        help='Debug value (0-9). Show working info. Default: 0')
    parser.add_argument("-l", '--fill', dest='fill', type=int,
                        default=16,  action='store',
                        help='Fill info string to lenght. Default: 16')
    parser.add_argument("test_cases", nargs= "*",
                        help = "Test case file names to execute")
    parser.add_argument("-s", "--show_case", default=0,  action='store_true',
                        help = "Show test case file(s).")

    args = parser.parse_args()
    #print(args)

    if args.version:
        print("Version: %s" % VERSION)
        sys.exit(0)

    if args.info:
        print(__doc__)
        sys.exit(0)

    if not args.test_cases:
        #print("Must specify at least one test case file.")
        #sys.exit(1)
        if args.verbose > 0:
            print("Using default file:", def_testfile)
        args.test_cases.append(def_testfile)

    args.errcnt = 0
    mainloop()

if __name__ == "__main__":
    mainfunct()
    sys.exit(args.errcnt)

# EOF
