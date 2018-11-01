from subprocess import call
import os


#----------------------------------------------------------------------------------------------------------------
#Appel bloquant
def launch_command(commands):
	out = open("stdout", "w") 
	errout = open("stderr", "w") 
	try:
		call(commands, stdout=out, stderr=errout)
	except ValueError:
			print("erreur")
	out = open("stdout", "r")
	errout = open("stderr", "r") 
	print(out.read())  
	print(errout.read()) 
#----------------------------------------------------------------------------------------------------------------
def compile_java(code_files, main_file, args = []):
	if len(code_files) == 0:
		print("aucun fichier")
		return 	
	comp_java = ["javac"]
	exec_java = ["java"]
	for file in code_files:
		comp_java.append(file)
	launch_command(comp_java)
	main_file = main_file[0:len(main_file)-5]
	exec_file = ""
	for l in range(len(main_file)-1, 0, -1):
		last_letter = l
		if main_file[l]=="/" or main_file[l]==".":
			break
		exec_file +=main_file[l]
	exec_file = main_file#exec_file[::-1]
	exec_java.append(exec_file)
	for arg in args:
		exec_java.append(arg)
	launch_command(exec_java)
#----------------------------------------------------------------------------------------------------------------
def compile_python(code_files, args = [], version=3):
	if len(code_files) == 0:
		print("aucun fichier")
		return	
	if version==3:
		comp_python = ["python3"]
	else:
		comp_python = ["python"]
	for file in code_files:
		comp_python.append(file)
	for arg in args:
		comp_python.append(arg)
	launch_command(comp_python)
#----------------------------------------------------------------------------------------------------------------
def compile_c(code_files, main_file = None, args = [], libs = [], cpp=False):
	#Compilation
	if len(code_files) == 0:
		print("aucun fichier")
		return 
	if cpp:
		comp_c = ["g++", "-Wall"]
	else:
		comp_c = ["gcc", "-Wall"]
	if main_file != None:
		if not cpp:
			exec_c = [str(main_file[0:len(main_file)-2])]
		else:
			exec_c = [str(main_file[0:len(main_file)-4])]
	else:
		if not cpp:
			exec_c = code_files[0][0:len(main_file)-2]
		else:
			exec_c = code_files[0][0:len(main_file)-4]

	for file in code_files:
		comp_c.append(file)
	for lib in libs:
		comp_c.append(lib)

	comp_c.append("-o") 
	exec_file = ""
	
	exec_file = main_file[0:len(main_file)-2]#exec_file[::-1]
	comp_c.append(exec_c[0])
	launch_command(comp_c)
	#Exécution
	for arg in args:
		exec_c.append(arg)
	launch_command(exec_c)

#l = ["t.java", "main.java"]
#compile_java(l, "main",["salut",'8'])
#compile_python(["t.py"])
