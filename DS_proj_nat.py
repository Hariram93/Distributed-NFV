import ipaddress
def parseInput(inputTuple):
	input_data = inputTuple.split()
	source_ip = input_data[0]
	source_port = input_data[1]
	dest_ip = input_data[2]
	dest_port = input_data[3]
	direction = input_data[4]
	
	return (source_ip,source_port,dest_ip,dest_port,direction)

def parseRule(ruleTuple):
	rule_data = ruleTuple.split()
	ip1 = rule_data[0]
	p1 = rule_data[1]
	ip2 = rule_data[2]
	p2 = rule_data[3]
	return(ip1,p1,ip2,p2)

		


print (" NAT Implementation \n")
i = open('nat_input','r')
for line in i:
	s_ip,s_port,d_ip,d_port,direc = parseInput(line)
	####Errors #######
        
        if not s_ip:
            raise AddressValueError('Address cannot be empty')

        octets = s_ip.split('.')
	#print octets
        if len(octets) != 4:
            raise AddressValueError("Expected 4 octets in %r" % s_ip)

	n = open('nat_table', 'r')
	o = open('private_to_public.txt','a')
	o1 = open('public_to_private.txt','a')
	for rule in n:
		
		inp_ip1,inp_p1,inp_ip2,inp_p2 = parseRule(rule)

		if direc == "out":
		
			if s_ip ==inp_ip1 and s_port ==inp_p1:
				
				source_ip =inp_ip2
				source_port = inp_p2
				
				output = source_ip +" " + source_port +" " + d_ip + " " + d_port +  '\n'
				o.write(output)
		
		else:
			if d_port == inp_p2:
				dest_ip = inp_ip1
				dest_port = inp_p1
				output = s_ip + " " + s_port + " " + dest_ip+" "+ dest_port +'\n'
				o1.write(output)


		

	o.close()
	o1.close()
	n.close()
