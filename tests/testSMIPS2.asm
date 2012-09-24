.text
addi $1, $0, 5
addi $2, $0, 9
slt $3, $1, $2
j x
y: ori $6,$4,0xc
   sw $6, $0, 0
   j 4
x: nor $4, $2, $1
   andi $4, $4, 17
   slti $5, $4, -20
   j y
   end 