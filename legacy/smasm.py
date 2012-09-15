#!/usr/bin/python3
import sys

VERSION = '1.2b'
INPUT_EXT = ['.sm','.sm2']
DATA_EXT = '_dat'
I_MIN = 31
I_MAX = -32
J_MIN = -4096
J_MAX = 4095

global f, fin, iout, dout
lnum = 0
opnum = 0
inum = 0
addrPos = 0
header = ''
fullOut = False
strict = False
multiOut = False
labels = {}
ops = { 'and':  {'op': '0000','type': 'arithmetic','argc': 3,'fnct': '000'},
        'or':   {'op': '0000','type': 'arithmetic','argc': 3,'fnct': '010'},
        'nor':  {'op': '0000','type': 'arithmetic','argc': 3,'fnct': '001'},
        'add':  {'op': '0000','type': 'arithmetic','argc': 3,'fnct': '100'},
        'sub':  {'op': '0000','type': 'arithmetic','argc': 3,'fnct': '101'},
        'slt':  {'op': '0000','type': 'arithmetic','argc': 3,'fnct': '111'},
        'andi': {'op': '0010','type': 'immArithmetic','argc': 3},
        'ori':  {'op': '0011','type': 'immArithmetic','argc': 3},
        'addi': {'op': '0100','type': 'immArithmetic','argc': 3},
        'slti': {'op': '0101','type': 'immArithmetic','argc': 3},
        'lw':   {'op': '0110','type': 'memory','argc': 3},
        'sw':   {'op': '0111','type': 'memory','argc': 3},
        'beq':  {'op': '1001','type': 'branchIf','argc': 3},
        'bne':  {'op': '1010','type': 'branchIf','argc': 3},
        'jr':   {'op': '1011','type': 'jr','argc': 1},
        'j':    {'op': '1100','type': 'jump','argc': 1},
        'jal':  {'op': '1101','type': 'jump','argc': 1},
        'lui':  {'op': '1111','type': 'jump','argc': 1}  }

def main():
    global f, fin, iout, dout, lnum, opnum, inum, addrPos, header, fullOut, strict, multiOut, labels    
    #check args
    if len(sys.argv) == 1 or len(sys.argv) > 6:
        shutd(1)
    for i in range(1,len(sys.argv)):
        if sys.argv[i][0] == '-':
            opt = sys.argv[i][1:].lower()
            if opt == 'help' or opt == '-help' or opt == 'h':
                print(GEN_HELP)
                shutd(99)
            elif opt == 'version' or opt == '-version':
                print('SMIPS Assembler version {0}\n'.format(VERSION))
                shutd(99)
            elif opt == 'f':
                fullOut = True
            elif opt == 's':
                strict = True
            elif opt == 'm':
                multiOut = True
            else:
                shutd(1)
        else:
            if (sys.argv[i][-3:] == INPUT_EXT[0] or sys.argv[i][-4:] == INPUT_EXT[1]):
                    try:
                        f = open(sys.argv[i], 'r')
                    except IOError:
                        shutd(2)
                    if sys.argv[i][-4:] == INPUT_EXT[1]:
                        multiOut = True
            else:
                shutd(3)
    #process data
    fin = [(x+'\n')[:x.find('#')].strip() for x in f.read().split('\n')]
    header = fin[0].lower()
    for j in range(len(fin)):
        fin[j] = preProcess(fin[j])
    lnum = 0
    inum = opnum
    header = fin[0].lower()
    if  header == '.data':
        if (multiOut):
            dout=[]
        else:
            try:
                dout = open(sys.argv[i][:-3]+DATA_EXT,'w')
            except IOError:
                shutd(4)
            print('v2.0 raw',file=dout)
        for data in fin[lnum:]:
            lnum += 1
            if data.strip() == '.data':
                continue
            elif data.strip() == '.text':
                header = '.text'
                break           
            elif data == '':
                continue           
            listDat = [x.strip() for x in data.split(',')]
            for item in listDat:
                if multiOut:
                    dout.append(toHex(toBin(toInt(item),16,1)))
                else:
                    print(toHex(toBin(toInt(item),16,1)),end=' ',file=dout)
    if header != '.text':
        shutd(5)
    #process text
    try:
        if sys.argv[i][-3:] == INPUT_EXT[0]:
            iout = open(sys.argv[i][:-3], 'w')
        else:
            iout = open(sys.argv[i][:-4], 'w')
    except IOError:
        shutd(4)
    print('v2.0 raw',file=iout)
    opnum = 0
    for inst in fin[lnum:]:
        lnum += 1
        if inst.strip() == '.text':
            continue
        elif inst == '':
            continue
        op = inst.partition(' ')[0].strip()
        args = [x.strip() for x in inst.partition(' ')[2].split(',')]
        if op == 'mv':
            op = 'add'
            args = args + ['$0']
        elif op == 'end':
            op = 'j'
            args = ['-1']
        if len(args) != ops[op]['argc']:
            shutd(6)
        print(toHex(encode(op,args)),end=' ',file=iout)
    if multiOut:
        for i in range(len(dout)):
            print(dout[i],end=' ',file=iout)
    shutd(0)

        
def preProcess(line):
    '''Takes line from file and returns line without labels or comments'''
    global lnum, opnum, addrPos, header, fullOut, labels
    if fullOut:
        print('{0}:'.format(lnum).rjust(4)+' {0}'.format(line))
    lnum += 1
    if line == '.text':
        header = '.text'
        return header
    rest = line[line.find(':') + 1:].lower().strip()
    if header == '.text' and len(rest) > 0:
        opnum += 1
    if line.find(':') > -1:
        name = line[:line.find(':')].lower()
        if (strict and name in labels):
            shutd(100)
        if header == '.data':
            labels[name] = addrPos
            addrPos += 1
        else:
            labels[name] = opnum
    return rest


def encode(op, args):
    '''Encodes instruction'''
    global lnum, opnum, inum, labels
    try:
        inst = ops[op]['op']
    except KeyError:
        shutd(200)
    opnum += 1
    if ops[op]['type'] == 'arithmetic':
        rd = parseReg(args[0])
        if (rd == 0 and strict):
            shutd(201)
        rs = parseReg(args[1])
        rt = parseReg(args[2])
        inst += toBin(rs, 3) + toBin(rt, 3) + toBin(rd, 3) + ops[op]['fnct']
    elif ops[op]['type'] == 'immArithmetic':
        rt = parseReg(args[0])
        if (rt == 0 and strict):
            shutd(201)
        rs = parseReg(args[1])
        inst += toBin(rs, 3) + toBin(rt, 3) + toBin(toInt(args[2]), 6, 1)
    elif ops[op]['type'] == 'memory':
        rt = parseReg(args[0])
        if (rt == 0 and op == 'lw' and strict):
            shutd(201)
        rs = parseReg(args[1])
        if args[2] in labels:
            if multiOut:
                imm = (inum + int(labels[args[2]]))
            else:
                imm = (int(labels[args[2]]))
        else:
            imm = toInt(args[2])
        inst += toBin(rs, 3) + toBin(rt, 3) + toBin(imm, 6, 1)
    elif ops[op]['type'] == 'branchIf':
        rs = parseReg(args[0])
        rt = parseReg(args[1])
        if args[2] in labels:
            imm = (int(labels[args[2]]) - (opnum))
        else:
            imm = toInt(args[2])
        inst += toBin(rs, 3) + toBin(rt, 3) + toBin(imm, 6, 1)
    elif ops[op]['type'] == 'jr':
        inst += toBin(parseReg(args[0]), 3) + '000000000'
    elif ops[op]['type'] == 'jump':
        if args[0] in labels:
            imm = (int(labels[args[0]]) - (opnum))
        else:
            imm = toInt(args[0])
        inst += toBin(imm, 12, 1)
    else:
        shutd(98)
    return inst


def parseReg(reg):
    '''Takes a raw register string, returns the integer value'''
    if (len(reg) == 2 and reg.startswith('$') and int(reg[1]) >= 0 and int(reg[1]) < 8):
        return int(reg[1])
    else:
        shutd(300)
    

def toBin(num, size, usign=0):
    '''Takes bin, int, or hex number, returns two-compliment binary of length size'''
    binNum = ''
    neg = False
    if num < 0 and usign:
        num = -num - 1
        neg = True
    while num > 0:
        binDig = num % 2
        binNum = str(binDig) + binNum
        num = num // 2
    if ((len(binNum) == size and not neg and usign) or (len(binNum) > size)) and strict:
        shutd(400)
    binNum = binNum.zfill(size)
    if neg:
        binNum = ''.join(['0' if x == '1' else '1' for x in binNum])
    return binNum
    

def toInt(num):
    '''Takes string and returns integer'''
    i = 0
    if num[0] == '-':
        i = 1
    if num[i:i+2] == '0b':
        return int(num, 2)
    elif num[i:i+2] == '0o':
        return int(num, 8)
    elif num[i:i+2] == '0x':
        return int(num, 16)
    else:
        try:
            return int(num)
        except ValueError:
            shutd(500)

    
def toHex(bNum):
    '''Takes two-compliment binary string and returns hex'''
    hexNum = ''
    while len(bNum) > 0:
        hexNum = str(hex(int(bNum[-4:],2))[2:]) + hexNum
        bNum = bNum[:-4]
    return hexNum


def shutd(code):
    '''Exits program with correct message and cleanup'''
    global f, iout, dout, lnum
    if code == 0:
        print('\nAssembled {0} lines successfully'.format(lnum))
    elif code == 1:
        print('Usage: {0} [options] sourceCode[{1},{2}]'.format(sys.argv[0],INPUT_EXT[0], INPUT_EXT[1]))
    elif code == 2:
        print('ERR: Source code not found')
    elif code == 3:
        print('ERR: Source code file extension not recognized')
    elif code == 4:
        print('ERR: Failed to create output file(s)')
    elif code == 5:
        print('ERR: Source code missing .text section')
    elif code == 6:
        print('ERR:{0}: Invalid sytax, try --help for guide'.format(lnum))
    elif code == 99:
    	pass 
    elif code == 100:
        print('ERR:{0}: Label is already in use'.format(lnum))
    elif code == 200:
        print('ERR:{0}: Unknown op'.format(lnum))
    elif code == 201:
        print('ERR:{0}: $0 is read only'.format(lnum))
    elif code == 300:
        print('ERR:{0}: Invalid register (must be of form $#)'.format(lnum))
    elif code == 400:
        print('ERR:{0}: Overflow detected'.format(lnum))
    elif code == 500:
        print('ERR:{0}: Integer conversion failed'.format(lnum))
    else: #Code 98 is reserved for unspecified error
        print('ERR: Unspecified error')
        
    try:
        f.close()
    except (IOError, NameError):
        pass
    try:
        iout.close()
    except (IOError, NameError):
        pass
    try:
        dout.close()
    except (IOError, NameError, AttributeError):
        pass
    exit(code)


GEN_HELP = '''
    SMIPS Assembler, version {0}
    Brett Cooley, Aaron Dufour, 2011

    GENERAL HELP
        smasm.py is an assembler which will convert assembly instructions into
        proper machine code for the SMIPS ISA. These instructions, along with
        any data, should be placed in one file that is passed as an argument.
        Within this file, data can be specified by word, with every word
        separated by either a comma or a newline.  Instructions must be placed
        one per line. Both lines of data and instructions can be labeled, and
        those labels can be used in place of jump or memory immediates. All
        indentation within a file is ignored, however there must be a space
        between a instruction's op and its first argument. For more information
        see SYNTAX GUIDE and TIPS.
        
    DATAPATH COMPATIBILITY
        In order to maintain compatibility with the single-cycle datapath,
        files with a '.sm' extension will be handled as single-cycle source
        files.  To assemble a file for the multi-cycle datapath, the '.sm2'
        extension will be used.  Alternatively, setting the -m flag will force
        the multi-cycle format, regardless of file extension.
        
    ARGUMENT FLAGS
        -f, -F                 Prints input file by line to stdout
        -s, -S                 Impose strict assembler rules.  Will not
                                 assemble files if overflow is detected, labels
                                 are reused, or if there are attempts to modify
                                 $0
        -m, -M                 Forces the assembler to assemble to the multi-
                                 cycle format, ignorning file extension
        
    SYNTAX GUIDE
        R-Type
         and                   and $rd, $rs, $rt
         or                    or $rd, $rs, $rt
         nor                   nor $rd, $rs, $rt
         add                   add $rd, $rs, $rt
         sub                   sub $rd, $rs, $rt
         slt                   slt $rd, $rs, $rt
        
        I-Type                 I-Type immediate range is [31,-32] 
         andi                  andi $rt, $rs, imm
         ori                   ori $rt, $rs, imm
         addi                  addi $rt, $rs, imm
         slti                  slti $rt, $rs, imm
         lw                    lw $rt, $rs, imm
                                 $rt - Location to load word to
                                 $rs - Address offset
                                 imm - Address in memory to load from
         sw                    sw $rt, $rs, imm (Mirrors above concept)
         beq                   beq $rs, $rt, imm
         bne                   bne $rs, $rt, imm
         jr                    jr $rs
         
        J-Type                 J-Type immediate range is [4095,-4096]
         j                     j imm
         jal                   jal imm
         lui                   lui imm
         
        Pseudo Ops
         mv                    mv $rt, $rs #Equivalent to add $rt, $rs, $0
         end                   end #Equivalent to j -1
         
    TIPS
        - All files must start with either '.data' or '.text'. Regardless of 
           how a file starts, before instructions are written, '.text' must be
           present.
        - Similarly, all files must have a '.sm' or '.sm2' extension to them.
           This does not imply any structure, it's for easy output naming
           conventions.  '.sm' is used for source code to be run on the single-
           cycle datapath, and '.sm2' is used for the multi-cycle datapath.
        - The recommended way to invoke smasm is './smasm.py -w source.sm',
           to make this default, simply type 'alias asm="./smasm.py -w"',
           replacing 'asm' with whatever you want to invoke the assembler by.
        - Some error messages print out the line number right after 'ERR:'.
         
    KNOWN BUGS
        No bugs are currently known, but to report any you find, please email
        brcooley [AT] cs.wm.edu.  The inclusion of the error message you
        received would be greatly appreciated.
'''.format(VERSION, sys.argv[0])

main()