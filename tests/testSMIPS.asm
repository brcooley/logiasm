.data
toSave: 0
x: 2
y: 3
z: -1
list: 9, 8, 6, 0o4, 0b10, 0xb
#avg: 82

.text
      lw $1, $0, x
      lw $2, $0, y
      and $3, $2, $1
      sub $3, $3, $1
pos1: beq $3, $0, pos3
      mv $2, $0
      addi $3, $0, 5
      lui 2
      addi $1, $1, 8
pos2: lw $4, $2, list
      add $6, $6, $4
      addi $2, $2, 1
      bne $6, $1, pos2     
      jr $7
pos3: addi $2, $2, 3
      add $2, $2, $1
      or $3, $2, $1
      andi $3, $3, 24
      sw $3, $0, toSave
      jal pos1
      slt $1, $6, $1
      ori $1, $
      end