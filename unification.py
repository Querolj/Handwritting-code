from PIL.Image import *
from random import randrange
import os
import math
import numpy
import ready_pic as rp
import tools as tools
import learning_manager as lm
import skimage.transform
#Convertit une image en format d'unification pour comparer ou/et réunir des samples
#la matrice unifié sera de TAILLE_UNIF*TAILLE_UNIF
#TODO : Gérer les restes

TAILLE_UNIF = 100 #Attention valeur partagée avec learning_function.py
#----------------------------------------------------------------------------------------------------------------
def numpy_unif_pic(image):
	matrice = tools.get_matrice_from_pic(image)
	return numpy_unif(matrice)

#----------------------------------------------------------------------------------------------------------------
def unification(image): #Retourne la matrice TAILLE_UNIF*TAILLE_UNIF (format d'unification)
	im = open(image)
	(width, height) = im.size
	matrice_unif = [[255 for j in range(TAILLE_UNIF)] for i in range(TAILLE_UNIF)]
	width_unif = width/TAILLE_UNIF # les proportions pour l'axe x
	height_unif = height/TAILLE_UNIF
	wc = 0 #Ces var s'incrémentent de facon à savoir ou on en est dans la complétion d'une case unifié
	hc = 0
	pixel_count = 0 #Somme des pixels noirs
	reste_y = 0
	reste_x = 0
	c = 0
	for x in range(TAILLE_UNIF):
		for y in range(TAILLE_UNIF):

			for i in range(math.ceil(hc),math.ceil(height_unif) + math.ceil(hc)):
				for j in range(math.ceil(wc), math.ceil(width_unif) + math.ceil(wc)):
					#print(str(hc)+" "+str(j)+" "+str(i))
					(r, g, b) = im.getpixel((j,i))
					if r==0:
						#Ici on ajoute les restes (le 0.25 de 18.75)
						if j==math.ceil(wc) and reste_y !=0: #Choper le reste éventuel
							cur_pix = pixel_count + reste_y 
							if i==math.ceil(hc) and reste_x !=0:
								cur_pix = cur_pix + reste_x
							pixel_count = pixel_count + cur_pix
						elif i==math.ceil(hc) and reste_x !=0:
							pixel_count = pixel_count + reste_x

						#Ici on gère le .75 de 18.75
						elif j == math.ceil(wc) + math.ceil(width_unif) - 1: #Si on est à la limite de l'axe y, on ajoute le reste
							cur_pix = math.fabs((math.ceil(width_unif) - 1) - width_unif)		
							if  i == math.ceil(height_unif) + math.ceil(hc):
								cur_pix = cur_pix*math.fabs((math.ceil(height_unif) - 1) - height_unif)
							pixel_count = pixel_count + cur_pix
						elif i == math.ceil(height_unif) + math.ceil(hc):
							pixel_count = pixel_count + math.fabs((math.ceil(height_unif) - 1) - height_unif)	
						else:
							pixel_count = pixel_count + 1

				if j == math.ceil(wc) + math.ceil(width_unif) - 1 and i == math.ceil(hc) + math.ceil(height_unif) - 1: 
				#reboot, cad fin d'un carré	
					matrice_unif[x][y] = pixel_count / (height_unif * width_unif)
					pixel_count = 0
					
					if math.ceil(wc) + math.ceil(width_unif)*2 < width - 1: #hc et wc doivent être maj qu'à la fin d'un carré
						wc = wc + width_unif
						reste_y = math.fabs(width_unif - math.ceil(width_unif))#Ce qu'il reste après la case (le 0.25 de 18.75)
						
					elif math.ceil(hc) + math.ceil(height_unif)*2 < height - 1:
						#On diminue l'axe y du carré
						hc = hc + height_unif
						reste_x = math.fabs(height_unif - math.ceil(height_unif))
						reste_y = 0
						wc = 0
					else:
						break #Fin du parcours de la matrice (break symbolique)
	return matrice_unif
#----------------------------------------------------------------------------------------------------------------
def numpy_unif(matrice):
	matrice = numpy.array(matrice)
	return skimage.transform.resize(matrice, (TAILLE_UNIF,TAILLE_UNIF),preserve_range=True)

#----------------------------------------------------------------------------------------------------------------
def unification_from_matrice(matrice): #Retourne la matrice TAILLE_UNIF*TAILLE_UNIF (format d'unification)
	if matrice == []:
		print("Matrice vide (unification_from_matrice)")
		return False
	(width, height) = tools.getWH(matrice)
	matrice_unif = [[255 for j in range(TAILLE_UNIF)] for i in range(TAILLE_UNIF)]
	width_unif = width/TAILLE_UNIF # les proportions pour l'axe x
	height_unif = height/TAILLE_UNIF
	wc = 0 #Ces var s'incrémentent de facon à savoir ou on en est dans la complétion d'une case unifié
	hc = 0
	pixel_count = 0 #Somme des pixels noirs
	reste_y = 0
	reste_x = 0
	c = 0
	for x in range(TAILLE_UNIF):
		for y in range(TAILLE_UNIF):
 
			for i in range(math.ceil(hc),math.ceil(height_unif) + math.ceil(hc)):
				for j in range(math.ceil(wc), math.ceil(width_unif) + math.ceil(wc)):
					#print(str(hc)+" "+str(j)+" "+str(i))
					r = matrice[i][j]
					if r==0:
						#Ici on ajoute les restes (le 0.25 de 18.75)
						if j==math.ceil(wc) and reste_y !=0: #Choper le reste éventuel
							cur_pix = pixel_count + reste_y 
							if i==math.ceil(hc) and reste_x !=0:
								cur_pix = cur_pix + reste_x
							pixel_count = pixel_count + cur_pix
						elif i==math.ceil(hc) and reste_x !=0:
							pixel_count = pixel_count + reste_x

						##Ici on gère le .75 de 18.75
						elif j == math.ceil(wc) + math.ceil(width_unif) - 1: #Si on est à la limite de l'axe y, on ajoute le reste
							cur_pix = math.fabs((math.ceil(width_unif) - 1) - width_unif)		
							if  i == math.ceil(height_unif) + math.ceil(hc):
								cur_pix = cur_pix*math.fabs((math.ceil(height_unif) - 1) - height_unif)
							pixel_count = pixel_count + cur_pix
						elif i == math.ceil(height_unif) + math.ceil(hc):
							pixel_count = pixel_count + math.fabs((math.ceil(height_unif) - 1) - height_unif)	
						else:
							pixel_count = pixel_count + 1

				if j == math.ceil(wc) + math.ceil(width_unif) - 1 and i == math.ceil(hc) + math.ceil(height_unif) - 1: 
				#reboot, cad fin d'un carré	
					matrice_unif[x][y] = pixel_count / (height_unif * width_unif)
					pixel_count = 0
					
					if math.ceil(wc) + math.ceil(width_unif)*2 < width - 1: #hc et wc doivent être maj qu'à la fin d'un carré
						wc = wc + width_unif
						reste_y = math.fabs(width_unif - math.ceil(width_unif))#Ce qu'il reste après la case (le 0.25 de 18.75)
						
					elif math.ceil(hc) + math.ceil(height_unif)*2 < height - 1:
						#On diminue l'axe y du carré
						hc = hc + height_unif
						reste_x = math.fabs(height_unif - math.ceil(height_unif))
						reste_y = 0
						wc = 0
					else:
						break #Fin du parcours de la matrice (break symbolique)
	return matrice_unif
#----------------------------------------------------------------------------------------------------------------
def create_unif_sample(matrice, new_pic):
	im = new("RGB", (TAILLE_UNIF, TAILLE_UNIF))
	pix = im.load()	
	for x in range(TAILLE_UNIF):
			for y in range(TAILLE_UNIF):
				if matrice[x][y] == 0:
					c = 0
				elif matrice[x][y]>254:
					c = 255
				else:
					c = math.floor(math.fabs((matrice[x][y]*255) - 255))

				pix[y,x] = (c,c,c)

	im.save(new_pic)
				

def create_unif_rep_sample(folder, is_static):
	(width_s, height_s) = (0,0)
	matrices_unif = dict()
	c = 0
	if not os.path.isdir(folder):
		create_unif_sample(unification(folder), "unified_"+folder)
	else:
		d = os.listdir(folder)
		for path, dirs, files in os.walk(folder):
		    for filename in files:
		    	cur_dir = os.path.basename(path)
		    	if filename != "." and filename != ".." and (tools.is_new(filename) or is_static):
		    		filename_path = cur_dir +"/" + filename
		    		image = open(filename_path)
		    		char_name = filename[0:len(filename)-4]
		    		if not char_name in matrices_unif:
		    			matrices_unif[char_name] = []
		    		matrices_unif[char_name].append(numpy_unif_pic(image))

		    		(width, height) = tools.getWH_from_pic(filename_path)
		    		width_s += width
		    		height_s += height
		    		c +=1

def create_unif_model_final(folder, char): #Prend un dossier et construit le modèle static de char avec les images dedans
	(width_s, height_s) = (0,0)
	matrices_unif = []
	c = 0
	if not os.path.isdir(folder):
		print("le dossier n'existe pas")
		return
	else:
		d = os.listdir(folder)
		for path, dirs, files in os.walk(folder):
		    for filename in files:
		    	cur_dir = os.path.basename(path)
		    	if filename != "." and filename != ".." and (tools.is_new(filename)):
		    		filename_path = cur_dir +"/" + filename
		    		image = open(filename_path)
		    		#char_name = filename[0:len(filename)-4]
		    		matrices_unif.append(numpy_unif_pic(image))

		    		(width, height) = tools.getWH_from_pic(filename_path)
		    		width_s += width
		    		height_s += height
		    		c +=1
		if c==0:
			print("Aucun fichier unifié & fusionné")
		else:
			proportion = (width_s/c)/(height_s/c)
   		
#----------------------------------------------------------------------------------------------------------------
# TEST UNITAIRE :
#----------------------------------------------------------------------------------------------------------------
#create_unif_model_final('Sample001', 0)