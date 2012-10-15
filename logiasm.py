#!/usr/bin/python3
import sys
import logging
import argparse
import textwrap
import contextlib

VERSION = '1.3b'

# OLD
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
####

@contextlib.contextmanager
def safe_open(filename, mode='r'):
	'''Just like open, but makes top-level code using with more readible, passing the error directly from the with statement.'''
	try:
		f = open(filename, mode)
	except EnvironmentError as err:
		_log = logging.getLogger('asm_log')
		_log.error("Couldn't open source file {}".format(filename)) #, exc_info=err)
		sys.exit()
	else:
		try:
			yield f
		finally:
			f.close()


def main():
	global fin, iout, dout, lnum, opnum, inum, addrPos, header, fullOut, strict, multiOut, labels

	# Parse arguments
	parser = argparse.ArgumentParser(description=DESC,
									 epilog=EPILOG,
									 formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('--version', action='version',
		version='{} version {}'.format(sys.argv[0], VERSION))
	parser.add_argument('-d','--debug', type=int, choices=range(3), default=0, metavar='LVL',
		help='sets debug logging level (default=0)')
	parser.add_argument('-i','--isa',
		help='uses the specified ISA during assembly. Otherwise, the file directive is read or the default ISA is used')
	parser.add_argument('-v','--verbosity', action='store_true',
		help='toggles on verbose output')
	parser.add_argument('-w','--warnings', type=int, choices=range(3), default=1, metavar='LVL',
		help='how to treat warnings.  Can be 0 (ignore), 1 (as warnings), or 2 (as errors)')
	parser.add_argument('filename',
		help='File to assemble')

	args = parser.parse_args()

	# Set up logging. We use one logger for problems in the assembler itself (asm_log)
	# and another for problems in source code being assembled (src_log)
	asm_log = logging.getLogger('asm_log')
	src_log = logging.getLogger('src_log')

	asm_faults = logging.StreamHandler(sys.stderr)
	asm_faults.setLevel(logging.ERROR)

	src_faults = logging.StreamHandler(sys.stdout)
	src_faults.setLevel(logging.WARN)

	fault_fmt = logging.Formatter('{levelname}: {message}', style='{')
	info_fmt = logging.Formatter('{message}', style='{')

	# This needs some help, as turning it on means every msg with level >= ERROR gets printed twice
	if args.verbosity > 0:
		asm_info = logging.StreamHandler(sys.stdout)
		asm_info.setLevel(logging.INFO)
		asm_info.setFormatter(info_fmt)
		asm_log.addHandler(asm_info)

	if args.warnings == 0:
		src_faults.addFilter(lambda record: record.level != logging.WARN)

	asm_faults.setFormatter(fault_fmt)
	src_faults.setFormatter(fault_fmt)

	asm_log.addHandler(asm_faults)
	src_log.addHandler(src_faults)

	if args.debug > 0:
		com_logfile = logging.FileHandler('.logiasm_log')

		if args.debug == 2:
			com_logfile.setLevel(logging.DEBUG)
		else:
			com_logfile.setLevel(logging.INFO)

		com_logfile.setFormatter(logging.Formatter('{asctime}:{name}:{levelname}:{message}', style='{'))

		asm_log.addHandler(com_logfile)
		src_log.addHandler(com_logfile)

	# Load ISA?
	if args.isa:
		asm_log.info("Using {} as target ISA".format(args.isa))

	else:
		asm_log.debug("No ISA parsed, will infer from source file")

	# Open file, strip whitespace
	lines_of_code = []
	code = []

	with safe_open(args.filename,'r') as f:
		lines_of_code = f.readlines()
		code = list(filter(lambda x: x != '', (x[:x.find('#')].strip() for x in lines_of_code)))
		for line in code:
			print(line)

	# 1st pass
	label_map = {k[:k.find(':')]:v for v,k in enumerate(code) if k.find(':') > -1}
	print(label_map)
	# 2nd pass
	# Output
	sys.exit()


	# #process data
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


def load_isa(filename):
	'''Control function to load and parse an isa description.'''



def preProcess(line):
	'''Takes line from file and returns line without labels or comments'''
	global lnum, opnum, addrPos, header, labels
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


# RF -> simply calling int(num,0) should work
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


#RF -> Should be using an iterator, probably handed by hex()
def toHex(bNum):
	'''Takes two-compliment binary string and returns hex'''
	hexNum = ''
	while len(bNum) > 0:
		hexNum = str(hex(int(bNum[-4:],2))[2:]) + hexNum
		bNum = bNum[:-4]
	return hexNum

# Replacing with print_error(code, exception) ???
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


DESC = '''
    logiasm.py is an assembler which will convert assembly instructions into
    proper machine code for use with Logisim.  It is designed to be used with
    any MIPS-like (RISC) instruction set.  For more detailed help, please see
    the readme file.
'''

EPILOG = textwrap.dedent('''
	TIPS
	- All files must start with either '.data' or '.text'. Regardless of how a
	    file starts, before instructions are written, '.text' must be present.
	- Similarly, all files must have an '.asm' extension. This does not imply
	    any structure, it's for easy output naming conventions.
	- Most error messages print out the line number where the error was
	    encountered right after 'ERR:'.

	KNOWN BUGS
	No bugs are currently known, but to report any you find, please email
	brcooley@cs.wm.edu, or submit an issue at
	https://github.com/brcooley/logiasm.  The inclusion of the error message you
	received would be greatly appreciated.
''')

if __name__ == '__main__':
	main()
