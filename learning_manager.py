#from PIL.Image import *
import os
import char_model as cm
import tools as tools
import csv
import profil_manager as pm
# Fonction pour : Convertir une image d'un modèle static en fichier histo
#				  	
#
#

FOLDER_STATIC = 'static/'
FOLDER_STATIC_DEF = 'default/'
PROF_COEFF = 5 #Coefficient d'une lettre pour un profil
DEF_COEFF = 1
#Fait average histo de chaque matrice, et met les histo + la prop + le nombre dans un fichier à nom de la clé du dict matrices
def save_model(matrices, proportion, number, char, profil =''):
	histos_x = []
	histos_y = []
	if len(matrices) == 0:
		print("Aucun fichier à sauvegarder")
		return False
	for matrice in matrices:
		(histo_x,histo_y) = tools.get_histo_2axis(matrice)
		histos_x.append(histo_x)
		histos_y.append(histo_y)
			
	save_file(average_histo(histos_x),average_histo(histos_y),proportion,char,len(matrices),profil)
	return True

#----------------------------------------------------------------------------------------------------------------
def save_file(histo_x, histo_y, proportion, char, number, profil='', tmp = False, loc = None):
	if tmp:
		(i,j) = loc
		#with open("tmp/"+str(char)+" "+str(i)+" "+str(j)+'.csv', 'w', newline='') as f:
		with open("tmp/"+str(i)+" "+str(j)+'.csv', 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow([proportion,number])
			writer.writerow(histo_x)
			writer.writerow(histo_y)
	elif profil == '':
		with open(str(FOLDER_STATIC)+str(FOLDER_STATIC_DEF)+str(char)+'.csv', 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow([proportion,number])
			writer.writerow(histo_x)
			writer.writerow(histo_y)
	else:
		profil_path = str(FOLDER_STATIC)+str(profil)
		if not pm.profil_existence(profil):
			print("le profil n'existe pas, création...")
			pm.create_profil(profil)
		else:
			print("profil existant détecté")
		with open(profil_path+"/"+str(char)+'.csv', 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow([proportion,number])
			writer.writerow(histo_x)
			writer.writerow(histo_y)
#----------------------------------------------------------------------------------------------------------------
#Moyenne d'un histo
def average_histo(histos):
	avg_histo = [0 for i in range(100)]
	c = 0
	for histo in histos:
		c += 1
		for i in range(len(histo)):
			avg_histo[i] += histo[i]
	for i in range(len(avg_histo)):
		avg_histo[i] = avg_histo[i]/c
	return avg_histo

#----------------------------------------------------------------------------------------------------------------
#Ajoute les données à un fichier
#Version avec hist déjà
def add_letter_to_model(new_histo_x, new_histo_y, new_prop, char, profil=''):
	res = load_file(char, profil)
	if res != False:
		(histo_x, histo_y, proportion, char, number) = res
		number = number
		proportion = proportion
	else:
		print("le profil n'existe pas, pas d'ajout de "+str(char))
		return False

	if profil == '': #Coef 1 si pas de profil 
		coeff = DEF_COEFF
	else:
		coeff = PROF_COEFF
	for i in range(len(histo_x)):
		histo_x[i] = ((histo_x[i] * number) + (new_histo_x[i]*coeff))/(number+coeff)
	for i in range(len(histo_y)):
		histo_y[i] = ((histo_y[i] * number) + (new_histo_y[i]*coeff))/(number+coeff)


	proportion = ((proportion*number) + (new_prop*coeff))/(number+coeff)
	number += coeff
	save_file(histo_x, histo_y, proportion, char, number, profil)
	return True
#----------------------------------------------------------------------------------------------------------------
#Retourne histos+prop+nombre
def load_file(char, profil = ''):
	c = 0
	proportion = 0
	number = 0
	histo_x = []
	histo_y = []
	if profil == '':
		with open(str(FOLDER_STATIC)+str(FOLDER_STATIC_DEF)+str(char)+'.csv', newline='') as f:
			reader = csv.reader(f)
			for row in reader:
				if c == 0:
					proportion = float(row[0])
					number = int(row[1])
				elif c==1:
					histo_x = tools.convert_list(row)
				else:
					histo_y = tools.convert_list(row)
				c+=1
	else:
		profil_path = str(FOLDER_STATIC)+str(profil)
		if not pm.profil_existence(profil):
			print("le profil n'existe pas")
			return False
		with open(str(FOLDER_STATIC)+profil+"/"+str(char)+'.csv', newline='') as f:
			reader = csv.reader(f)
			for row in reader:
				if c == 0:
					proportion = float(row[0])
					number = int(row[1])
				elif c==1:
					histo_x = tools.convert_list(row)
				else:
					histo_y = tools.convert_list(row)
				c+=1
	
	return (histo_x, histo_y, proportion, char, number)

#----------------------------------------------------------------------------------------------------------------
#Retourne histos+prop+nombre
def load_file_tmp(file):
	c = 0
	proportion = 0
	number = 0
	histo_x = []
	histo_y = []
	with open("tmp/"+file, newline='') as f:
		reader = csv.reader(f)
		for row in reader:
			if c == 0:
				proportion = float(row[0])
				number = int(row[1])
			elif c==1:
				histo_x = tools.convert_list(row)
			else:
				histo_y = tools.convert_list(row)
			c+=1
	
	return (histo_x, histo_y, proportion, number)

#----------------------------------------------------------------------------------------------------------------
def read_coord(filename):
	c = 0
	i=""
	j=""
	for l in filename:
		if l == " " or l==".":
			c+=1
		if c==0:
			i = i + l
		if c==1:
			j = j + l
	return (int(i), int(j))
#----------------------------------------------------------------------------------------------------------------
def is_in(letter_to_add, i,j):
	c=0
	for d in letter_to_add:
		if c == i:
			if j <= d:
				return True
				break
	return False
#----------------------------------------------------------------------------------------------------------------
#Retourne le char correspondant aux coordonnées i j, sinon None
def get_char_from_text(text,i,j):
	line = 0
	char = 0
	for l in text:
		if j==char and i==line:
			return l
		char +=1
		if l == " ":
			line +=1
			char = 0

	return None
#----------------------------------------------------------------------------------------------------------------
#Prend une liste de letter_to_add en param, save ces dimensions correspondant aux .csv dans tmp dans les modèles static
# V2 : ajoute le text à la BDD, chaque lettre du texte est alloué à un fichier dans tmp
def add_in_tmp(text, profil=''):
	if profil == "":
		profil =''
	#letter_to_add = load_modif() # Charge tout le fichier letter_to_add
	#print(letter_to_add)
	for path, dirs, files in os.walk("tmp"):
		for filename in files:
			if filename != "." and filename != ".." and filename != ".DS_Store":
				(i,j) = read_coord(filename) #Coordonnées sur le nom du fichier 
				#On ajoute le caractère dans le string correspondant aux coor (i,j)
				
				char = get_char_from_text(text,i,j-1) #(Char pouvant éventuellement être changé )
				if char != None and char!=" ":
					(histo_x, histo_y, proportion, number) = load_file_tmp(filename)
					add_letter_to_model(histo_x, histo_y, proportion, char, profil)
				'''
				if is_in(letter_to_add, i, j):
					(histo_x, histo_y, proportion, char, number) = load_file_tmp(filename)
					#new_histo_x, new_histo_y, new_prop, char, profil=''
					add_letter_to_model(histo_x, histo_y, proportion, char, profil)
				'''
#----------------------------------------------------------------------------------------------------------------
#Cette fonction doit être utilisé en argument de add_in_tmp
def load_modif():
	i = 0
	letter_to_add = []
	with open("letter_to_add", newline='') as f:
		reader = csv.reader(f)
		for row in reader:
			letter_to_add(int(row))
			
		
	return letter_to_add


#----------------------------------------------------------------------------------------------------------------
#   		ZONE DE TESTS  
#----------------------------------------------------------------------------------------------------------------

#save_model([2,5,8,80,0,0,6],50)
#save_file([2,5,8,80,0,0,6], [1,2,8,10,6,0,4],[60], 'a', 'jean')
#load_file(0)
#dim = [(0,9),(0,21),(1,0),(1,1),(1,2)]
#add_in_tmp(dim)
#print(load_modif())
#(histo_x, histo_y, proportion, char, number) = load_file_tmp("7 0 13.csv")
#print(histo_x)
#print(proportion)
#print(char)
#new_histo_x, new_histo_y, new_prop, char, profil=''
#add_letter_to_model(histo_x, histo_y, proportion, char, "test")
#add_letter_to_model(histo_x, histo_y, proportion, char, "test")


#for s in row:
#				line += s
#			j = int(line)
#			if j != 0:
#				letter_to_add.append((i,j))
#			i += 1
s = "ollolola cavaou"
#print(get_char_from_text(s,5,0))
#(histo_x, histo_y, proportion, number) = load_file_tmp("0 2.csv")
#print((histo_x, histo_y, proportion, number))
#add_in_tmp(s)