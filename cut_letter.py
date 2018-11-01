from PIL.Image import *
import os
import tools as tools
import math
import numpy as np
import Histograme as histo
import unification as unif
import learning_manager as lm
import recadrage as rc
#TODO : utilisiser l'unification de matrice au lieu de celle d'histo

# Sert à couper les lettres tel un katana, prend une image d'une ligne
STEP_H = 30 # Taille des pas dans la recherche de l'écriture (pour gagner du temps)
QUALITY_THRESHOLD  = 200# Seuil à partir du quel une lettre peut être considéré que bonne
#----------------------------------------------------------------------------------------------------------------
# cut_letter_in_line prend les segments (partie de découpe possible) et la matrice d'une phrase.
def cut_letter_in_line(segments, matrice):
	(l,r) = (-1,-1)
	c = 0 #pour teste
	index_letter = 0
	inc_index = True
	old_score = 999


	letter_read = dict()
	histo.load_static_model()
	for i in segments:
		if l == -1:
			l = i
		else:
			r = i
			# retourner la matrice encadrée (gérer les écritures en italique à faire)
			portion_matrice = frame_cluster((l,r), matrice)
			#portion_matrice = tools.get_portion_from_matrice((t,d), matrice)
			if portion_matrice == True:
				#print(" blanche : "+str((l,r)))
				pass
			elif portion_matrice != None:
				#print("saving portion "+str(c)+"...")
				# Ici on teste la portion_matrice
				#(letter, score) = test_portion(histo_unif(tools.get_histo_2axis(portion_matrice)));
				unif_portion = unif.numpy_unif(portion_matrice);
				res = tools.simple_build_picture(unif_portion, "portions_unif/unif_matrice_num_"+str(c)+":"+str(l)+"_"+str(r)+".png")
				(letter, score) = test_portion(unif_portion);
				
				# Si le résultat est bon et meilleur que le précédent, on le garde
				# Et on change la lettre si elle est différente
				if score <= QUALITY_THRESHOLD and score < old_score:
					letter_read[index_letter ] = (letter, score)
					old_score = score
				#Si le résultat est mauvais (moins bon que précédent), on passe à une nouvelle lettre
				#On change que quand on trouve un résultat mauvais
				
				else: 
					print("_____ LETTER FOUND : ")
					index_letter = True
					l = i 
					index_letter += 1
					old_score = 999
			else:
				print("portion trop petite.")
		c += 1
	print("letter_read : "+str(letter_read))

#----------------------------------------------------------------------------------------------------------------
# Version simplifié de cut_letter qui coupe les lettres espacées
def cut_letter_with_space(space_clusters,avg_space_lenght,line_matrice, line_num,profil=''):
	c = 0 #for test
	index_letter = 0
	letter_read = []

	left_letter = -1
	start = True
	char_cluster = []
	for (l,r) in space_clusters:
		if start:
			left_letter = r
			start = False
		else:
			char_cluster.append(((left_letter,l),'l'))
			left_letter = r
			if r-l >= avg_space_lenght:
				char_cluster.append(((l,r),'e'))
			else:
				char_cluster.append(((l,r),'s'))

	#Clean les clusters grains
	i = 0
	for ((l,r),n) in char_cluster:
		if i >= len(char_cluster):
			break
		if (n=='s' or n=='e') and i < len(char_cluster) -1:
			((l2,r2),n2) = char_cluster[i+1]

			while r2-l2 < avg_space_lenght/5:
				if i == len(char_cluster) - 2:
					char_cluster[i] = ((l,len(line_matrice)),n)
					char_cluster.remove(((l2,r2),n2))
				else:
					((l3,r3),n3) = char_cluster[i+2]
					char_cluster[i] = ((l,r3),n)
					char_cluster.remove(((l3,r3),n3))
					char_cluster.remove(((l2,r2),n2))	
				if i == len(char_cluster) - 1:
					break
				((l2,r2),n2) = char_cluster[i+1]
		i += 1		


	#Après on frame
	#Et on test chaqu'une des matrices framed
	c = 0
	res = []
	for ((l,r),n) in char_cluster:
		if n=='l' and line_matrice != []:
			portion_matrice = frame_cluster((l,r), line_matrice)
			#print(portion_matrice)
			if portion_matrice != [] and portion_matrice != None:
				#print("----------------------")
				#print(portion_matrice)
				unif_portion = unif.numpy_unif(portion_matrice);
				res = tools.simple_build_picture(unif_portion, "portions_unif/unif_matrice_num_"+str(c)+":"+str(l)+"_"+str(r)+".png")
				
				(histo_x, histo_y) = tools.get_histo_2axis(unif_portion)
				(w,h) = tools.getWH(portion_matrice)
				proportion = w/h

				res = histo.found_letter_matrice(unif_portion, proportion)
				#print(str(res)+"\n")
				(letter,score) = res[0]
				letter_read.append((letter,score))
				# .csv pour chaque lettre
				
				c +=1
				lm.save_file(histo_x, histo_y, proportion, letter, 1, tmp = True, loc = (line_num,c))

			else:
				print("empty portion")
		elif n=='e' and line_matrice != []:
			(letter,score) = (" ",0)
			letter_read.append((letter,score))

	letter = ""
	for (l,s) in letter_read:
		letter = letter + str(l)

	print("#"+letter) # Le print est parsé en java
#----------------------------------------------------------------------------------------------------------------
#retourne la lettre trouvée et le score
def test_portion(matrice_unif):
	(letter,score) = (None, 0)
	#Tester la matrice avec histo.py
	res = histo.found_letter_matrice(matrice_unif)
	(letter,score) = res[0]
	return (letter, score)

#----------------------------------------------------------------------------------------------------------------
#Envoie le cluster pour le check via les tests des modèles statics
def send_cluster(cluster, matrice):
	(l,r) = cluster
	pass

#----------------------------------------------------------------------------------------------------------------
#Retourne le couple d'axe (u,d) qui encadre la portion
def frame_cluster(cluster, matrice):
	(l,r) = cluster
	if r-l<4:
		return None
	(width, height) = tools.getWH(matrice)
	width_cluster = r-l
	STEP_H = height/100
	if STEP_H < 1:
		STEP_H = 1
	(u,d) = (-1,-1)
	stop = False

	for x in range(0, height, math.floor(STEP_H)):
		if stop:
			break
		for y in range(l,r,1):
			if stop:
				break
			if matrice[x][y] == 0:
				for z in range(x, x-math.floor(STEP_H)-1, -1):
					if z == 0:
						u = z
						stop = True
						break
					if stop:
						break
					for a in range(l,r,1):
						if matrice[z][a] == 0:							
							break
						if a == r - 1:
							u = z
							stop = True
							break

	#vérifie si la portion est blanche
	if u >= height - 2 or u==-1:
		return True

	stop = False
	for x in range(height - 1, u, math.floor(-STEP_H)):
		if stop:
			break
		for y in range(l,r,1):
			if stop:
				break
			if matrice[x][y] == 0:	
				for z in range(x, x+math.floor(STEP_H)+2, 1):
					if z == height - 1:
						d = z
						stop = True
						break
					if stop:
						break
					for a in range(l,r,1):
						if matrice[z][a] == 0:
							break
						if a == r - 1:
							d = z
							stop = True
							break

	portion_matrice = [[255 for j in range(r-l)] for i in range(d-u)]
	#prend la bonne portion en fonction des couples d'intervalles calculés
	for i in range(u,d,1):
		for j in range(l,r,1):
			portion_matrice[i- u][j - l] = matrice[i][j]	

	return portion_matrice #(u,d)


#----------------------------------------------------------------------------------------------------------------
# 						FONCTIONS PLUS UTILISEE
#
#----------------------------------------------------------------------------------------------------------------

# Unification d'histogramme, ne sert plus avec la nouvelle implémentation de la BDD et de l'unification
def histo_unif(histos):#100 = valeur d'unification
	(histo_x, histo_y) = histos
	step_x = len(histo_x)/100
	step_y = len(histo_y)/100
	histo_unif_x = [0 for i in range(100)]
	histo_unif_y = [0 for i in range(100)]


	coef = 0
	to_pass = False
	step_tmp = step_x
	end_x = step_x
	#Censé marcher dans les 2 cas, step</> 1, commence à 0 ?
	list_x = np.arange(0,len(histo_x), step_x)
	c = 0

	begin = True
	for i in list_x:
		step_tmp = step_x
		for a in range(math.floor(i),math.ceil(end_x),1):
			if c > 99 or a > len(histo_x) - 1: #A changer (condition si on arrive à la fin)
				break		
			if begin: # Premier pas, premier tour, 
				if (step_tmp - 1 )> 0:
					histo_unif_x[c] += histo_x[a]
					to_pass = True
					step_tmp -= 1 #On continue que dans ce cas
				elif (step_tmp - 1)<0:
					coef = step_x
					histo_unif_x[c] += coef * histo_x[a]
					to_pass = False
					break
				else:
					histo_unif_x[c] += histo_x[a]
					to_pass = False
					break
				begin = False
				#step_tmp = step_x 
			else:
				if step_tmp + i > math.ceil(i): #On doit continuer
					coef = math.ceil(i) - i
					histo_unif_x[c] += coef* histo_x[a]
					to_pass = True
					step_tmp -= coef
				elif step_tmp + i < math.ceil(i): #Là on finit
					coef = step_tmp
					histo_unif_x[c] += coef* histo_x[a]
					to_pass = False
					break
				else:
					histo_unif_x[c] += histo_x[a]
					to_pass = False


		end_x = end_x + step_x
		c += 1
	# Pour l'axe y :
	coef = 0
	to_pass = False
	step_tmp = step_y
	end_y = step_y
	#Censé marcher dans les 2 cas, step</> 1, commence à 0 ?
	list_y = np.arange(0,len(histo_y), step_y)
	c = 0

	begin = True	

	for i in list_y:
		step_tmp = step_y
		for a in range(math.floor(i),math.ceil(end_y),1):
			if c > 99 or a > len(histo_y) - 1: #A changer (condition si on arrive à la fin)
				break		
			if begin: # Premier pas, premier tour, 
				if (step_tmp - 1 )> 0:
					histo_unif_y[c] += histo_y[a]
					to_pass = True
					step_tmp -= 1 #On continue que dans ce cas
				elif (step_tmp - 1)<0:
					coef = step_y
					histo_unif_y[c] += coef * histo_y[a]
					to_pass = False
					break
				else:
					histo_unif_y[c] += histo_y[a]
					to_pass = False
					break
				begin = False
				#step_tmp = step_x 
			else:
				if step_tmp + i > math.ceil(i): #On doit continuer
					coef = math.ceil(i) - i
					histo_unif_y[c] += coef* histo_y[a]
					to_pass = True
					step_tmp -= coef
				elif step_tmp + i < math.ceil(i): #Là on finit
					coef = step_tmp
					histo_unif_y[c] += coef* histo_y[a]
					to_pass = False
					break
				else:
					histo_unif_y[c] += histo_y[a]
					to_pass = False


		end_y = end_y + step_y
		c += 1

	return (histo_unif_x,histo_unif_y)
#----------------------------------------------------------------------------------------------------------------
#   		ZONE DE TESTS  
#----------------------------------------------------------------------------------------------------------------
#matrice = tools.get_matrice_from_pic("at1.png")
#(histo_x, histo_y) = tools.get_histo_2axis(matrice)
#(histo_x, histo_y) = histo_unif((histo_x, histo_y))
#print((histo_x, histo_y))
