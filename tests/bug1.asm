.data
#
# Assembly file to test the datapath
#


memdata: 22


# begin text section

        .text


main: 
    addi $2, $0, 4  # $2 <- 4

	  addi $3, $0, 5  # $3 <- 5

	  addi $4, $0, 9  # $4 <- 9

	  add $1, $2, $3  # $1 <- $2 + $3 = 9
	  bne $1, $4, fail

	  beq $1, $4, beqsuccess


main2:
    lw $7, $0, memdata  # $7 <- memdata (22)

	  addi $6, $0, 22     # $6 <- 22


    
	  beq $6, $7, success
    # fall through to fail


fail:
     mv $2, $0 # zero out $1 to show failure

	  j end


beqsuccess:
    addi $1, $0, 30 # $1 <- 30 to prove success
	  j main2


success: # completely successful execution
	  addi $2, $0, -1 # $1 <- -1 to show success


end:
      addi $1, $0, -1 # $1 <- -1 to show end
