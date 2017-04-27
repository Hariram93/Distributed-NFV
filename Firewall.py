def validateInput(inputPacket):
    input_string = inputPacket.split()
    #print (input_string)
    size = len(input_string)
    
    if (size != 6):
        return (1, input_string[0])

    elif(validateIP(input_string[0])):
        return (2, input_string[0])

    elif(int(input_string[1])>65535 or int(input_string[3])>65535):
        return (3, input_string[0])

    
    elif(input_string[4] != "TCP"  and  input_string[4] != "UDP"):
        return (4, input_string[0])
    else:
        return (0,input_string[0])

def validateIP(s):
    a = s.split('.')
    if len(a) != 4:
        return True
    for x in a:
        if not x.isdigit():
            return True
        i = int(x)
        if i < 0 or i > 255:
            return True

    return False

def parseInput(inputTuple):
        input_data = inputTuple.split()
        source_ip = input_data[0]
        source_port = input_data[1]
        dest_ip = input_data[2]
        dest_port = input_data[3]
        proto = input_data[4]
        state = input_data[5]

	#print "Source IP: ",source_ip, "Protocol: ", proto
        return (source_ip,proto,state)
        
            
def parseRule(rule,sip,proto,cstate):
	rule_data = rule.split()
	if rule_data[1] == sip:
		#print "SourceIP matched"
		if rule_data[3] == proto:
			#print "Protocol matched"
                        if rule_data[4] == cstate:

                                return rule_data[5]
                        else:
                                return "Not Matched"
		else:
			return "Not Matched"
	else:
		return "Not Matched"
		


print ("This is the Demo for firewall\n")


while True:
	i = open('input.txt','r')

	for line in i:
		#print "calling pareser"
			isValid,sourceIP = validateInput(line)
			#print (isValid)
			if (isValid == 0):
				sip_input, proto_input, conn_state = parseInput(line)
				j = open('rules.txt', 'r')
				for rule in j:
					result = parseRule(rule,sip_input,proto_input,conn_state)
					if (result == "ACCEPT" or result == "DROP"):
						#print (result)
						break
					else:
						result = "DROP"

				outfile = open('output.txt','w')
				entry = sip_input +" " +result + '\n'
				print (entry)
				outfile.write(entry)
				outfile.close()
			else:
				#print ("Input packet corruopted")
				outfile = open('output.txt','w')
				entry = sourceIP + " Packet Corrupted: Error Code "+ str(isValid) + '\n'
				print (entry)
				outfile.write(entry)
				outfile.close()



            
