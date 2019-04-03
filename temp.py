import os

def os_mkdir(dirname) :
	if not os.path.exists(dirname) :
		os.system('mkdir -p ' + dirname)

if __name__ == '__main__':
	ps_filepath = '/tmp/psfiles/' + 'ps_' + str(100000897) + '.ps'
	print(ps_filepath)
