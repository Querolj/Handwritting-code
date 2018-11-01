import learning_function as learning_function
import learning_manager as lm
import ready_pic as ready_pic
import recadrage as reframing
import unification as unification
import profil_manager as pm
import Histograme as histo
import command_prompt as cp
import tools as tools
import framing as fm
import os
import sys




'''
Options utiles : 
-add profil ='' : Ajoute les lettres dans tmp nécessaire à la BDD
-st dirpath char : Créer le modèle static à partir des samples dans dirpath
-java code_files - main - args : Compilation java
-c code_files - main - args -libs : Compilation c
-rd pic_path : Lecture d'une photo
-rbw pic_path : Lecture d'un mot (pas de segmenation de ligne)
-rdb pic_path : Lecture d'une photo binaire
-rbwb pic_path : Lecture d'un mot binaire (pas de segmenation de ligne)


'''


def create_model_manu(picture):
	ready_pic.ready_pic(picture)
	for i in range(len(picture)):
		if picture[i] == ".":
			picture = "new_"+picture[:i+1]+"png"
			break
	reframing.reframing(picture)
	unification.unification(picture)

def create_manu_model_from_rep(folder):
	print("Préparation des images...")
	ready_pic.ready_rep(folder)
	print("Encadrage...")
	reframing.create_rep_fresh_sample(folder, False)
	print("Unification...")
	unification.create_unif_rep_sample(folder, False)

#Unifie toutes les images d'un dossier
#def create_static_model_from_rep(folder):
#	print("Encadrage...")
#	reframing.create_rep_fresh_sample(folder, True)
#	print("Unification...")
#	unification.create_unif_rep_sample(folder, True)

#Fusionne les lettres unifiées dans un dossier
def fusion(folder, model_name): 
	all_model = learning_function.start(folder, model_name)
	learning_function.create_all_matrix(all_model)

#Nouvelle version, unifie toutes les images d'un dossier et fusionne, puis sauvegarde (-st)
def create_static_model_from_rep(folder, char):
	print("Encadrage...")
	reframing.create_rep_fresh_sample(folder, True)
	print("Unification...")
	unification.create_unif_model_final(folder, char)

#Ajoute une lettre à un modèle static
def add_model_to_static(model_name, picture):
	#all_model = learning_function.load_db()
	#print(all_model)
	reframing.reframing(picture)
	matrice = unification.unification(picture)
	(histo_x, histo_y) = tools.get_histo_2axis(matrice)
	print((histo_x, histo_y))

	#unification.create_unif_sample(unification.unification(picture), "unified_"+picture)
	#learning_function.add_knowledge(model_name, "unified_"+picture, all_model)
def print_db():
	learning_function.print_db()

def compare(model_name):
	histo.found_letter(model_name)
if sys.argv[1] == "-t":
	print("Zone de tests")
if sys.argv[1] == "-st":
	if len(sys.argv) == 4:
		create_static_model_from_rep(sys.argv[2], sys.argv[3])
	else:
		print("le nombre d'argument est mauvais")
elif sys.argv[1] == "-manu":
	create_manu_model_from_rep(sys.argv[2])
elif sys.argv[1] == "-fus":#2 = folder, 3 = caractère
	fusion(sys.argv[2], sys.argv[3])
#elif sys.argv[1] == "-add": 
#	add_model_to_static(sys.argv[2], sys.argv[3])
elif sys.argv[1] == "-print":
	print_db()
elif sys.argv[1] == "-del": #2 = caractère à supprimer, 3 = "u" si on veut aussi supprimer le modèle créé
	learning_function.remove_db(sys.argv[2])
	print_db()
	if len(sys.argv) > 3:
		os.remove(sys.argv[3]+".png")
		print(sys.argv[2]+" et " +sys.argv[2]+".png ont été supprimé.")
	else:
		print(sys.argv[2]+" a été supprimé.")
elif sys.argv[1] == "-cmp": 
	compare(sys.argv[2])
elif sys.argv[1] == "-rd": # 2 : Photo
	histo.load_static_model()	
	fm.complet_cut(sys.argv[2])
elif sys.argv[1] == "-rdb": # 2 : Photo
	histo.load_static_model()	
	fm.complet_cut(sys.argv[2], True)
elif  sys.argv[1] == "-rdwb": #Lire mot ou phrase qui vient d'un ipad
	histo.load_static_model()	
	fm.cut_word_bin(sys.argv[2], True)
elif  sys.argv[1] == "-rdw": #Lire mot ou phrase qui vient d'un ipad
	histo.load_static_model()	
	fm.cut_word_bin(sys.argv[2], False)
elif sys.argv[1] == "-add": #Argument = nom de profil
	if len(sys.argv) > 3:
		lm.add_in_tmp(sys.argv[2], sys.argv[3])
	else:
		lm.add_in_tmp(sys.argv[2])
elif sys.argv[1] == "-create" and len(sys.argv) > 2:
	pm.create_profil(sys.argv[2])
elif sys.argv[1] == "-prof":
	pm.get_profils()






#----------------------------------------------------------------------------------------------------------------
#   		COMPILATION ET EXECUTION
#----------------------------------------------------------------------------------------------------------------
#python3 main.py -java code_files - main - args
#Exemple : python3 main.py -java k.java oi.java - oi.java - 5.2 lol 4
elif sys.argv[1] == "-java":
	i = 0
	c = 0
	code_files = []
	args = []
	main_file = ""
	for i in range(2,len(sys.argv),1):
		if sys.argv[i] == "-":
			c = i
			break
		code_files.append(sys.argv[i])
	main_file = sys.argv[c+1]
	if len(sys.argv) >= c+3:
		for i in range(c+3, len(sys.argv), 1):
			args.append(sys.argv[i])
	cp.compile_java(code_files, main_file, args)

#python3 main.py -c code_files - main - args -libs
elif sys.argv[1] == "-c":
	i = 0
	c = 0
	code_files = []
	args = []
	libs = []
	main_file = ""
	for i in range(2,len(sys.argv),1):
		if sys.argv[i] == "-":
			c = i
			break
		code_files.append(sys.argv[i])
	main_file = sys.argv[c+1]
	if len(sys.argv) >= c+3:
		c = c + 3
		if c != "-": #Alors il y a des arguments 
			for i in range(c, len(sys.argv), 1):
				if sys.argv[i] == "-":
					c = i
					break
				args.append(sys.argv[i])

	if len(sys.argv) >= c+1:
		for i in range(c+1, len(sys.argv), 1):
			libs.append(sys.argv[i])
	cp.compile_c(code_files, main_file=main_file, args = args, libs = libs)

#----------------------------------------------------------------------------------------------------------------
#   		ZONE DE TESTS  
#----------------------------------------------------------------------------------------------------------------

#print(check_type("lol"))
#lm.add_in_tmp()
