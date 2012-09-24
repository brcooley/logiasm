# LogiAsm - Generic Logisim Assembler #

The goal of this project is to have a generic assembler available for assembling arbitrary instruction sets into 
machine code suitable for use in [Logisim][lg].  

## Current Work ##

Currently, work is being done to transform smasm.py into a more readable, and generic assembler, [logiasm.py][self].  As of this commit, logiasm is not functional.  See the todo list below for progress.

#### Todo ####
 + ~~Argument parsing~~
 + Logging infrastructure
 + ISA spec definition
  + ~~Filesystem semantics~~
  + Syntax
  + Parser
  + Runtime error checking
 + 1st pass overhaul
  + Label mapping
  + Pseudo-op expansion
   + Recursive?
 + 2nd pass overhaul
  + Label resolution
  + Static verification
   + Register access
   + Over/underflow
   + Label usage
  + Encoding

Below are bonus items, which will come after a working assembler

 + Generic target system (Assembling for more than just Logisim)
 + Test instruction generation
 + Operation tagging (for generated pseudo instructions for free)
 + Automated datapath debugging

## Instruction Sets ##

logiasm is designed to be a generic assembler, which should be able to take any RISC architecture, and output machine code suitable for direct loading into Logisim.  Obviously there are limitations to what "any" means, but if you can express your target ISA within the confines of the ISA file syntax, then logiasm should be able to handle it.  

### Defining an ISA ###

To define your own ISA, you'll need to create a file `my_isa_name.isa` in the isa directory.  This enables the assembler to automatically load your ISA when it is the target of an assembly file.  Otherwise, you must specify the name of your ISA file at runtime with the `--isa` flag.

#### ISA Syntax ####

All ISA files are specified in [JSON][json], and must conform to the following spec.  Note that order does not matter, and the bold keys are required.

**registers** : _[int | object]_  
This should either specify the number of usable registers as an int, or pass an object with a key for each register mapping to an object describing the register traits.  There are no required keys in the register trait object, but optional values include a boolean write key telling the assembler if writes to this register are allowed in user code, a , and a 

**bits:** : _int_  
**instructions** : _object_  
types : _object_  

## History ##

#### SMIPS ####

SMIPS (Simple MIPS) was the instruction set for which LogiAsm was originally written, then called SMasm.  This version 
is preserved under the legacy directory.


[lg]:http://ozark.hendrix.edu/~burch/logisim

[self]:https://github.com/brcooley/logiasm/logiasm.py
[json]:http://www.json.org/