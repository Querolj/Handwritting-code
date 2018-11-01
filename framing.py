from PIL.Image import *
from random import randrange
import os
import ready_pic as rp
import tools as tools
import cut_letter as cut
import Histograme as histo
import recadrage as rc

import copy
from math import *
#IMP : ZONE DE TEST TEMPORAIRE LIGNE 590

#Ici on utilise la matrice créée par ready_pic et les histogrammes pour découper les lignes de la feuille sous
#forme de plusieurs matrices
PRECISION = 1 #Initialement 5, plus la valeur est basse, plus ca augmente potentiellement le nombre de lignes
PRECISION_W = 0.2 # Précision pour les mots
ETALEMENT = 200 #Initialement 60
EPAISSEUR = 2 # L'épaisseur du trait (qui calcule l'écartype), défaut 2
DIFF_DIST = 30 # Défaut 10
SAUT = 5 # Défaut 5, hypothèse sur la taille du saut possible pour optimiser le framing
DEPLACEMENT_LIGNE = 125 # Défaut 125, mots et lignes confondus
#----------------------------------------------------------------------------------------------------------------
def moyenne(l):
	return sum(l)/len(l)
#----------------------------------------------------------------------------------------------------------------
def picture_segmentation_y(matrice, segments, picture):
	width = len(matrice[0])
	height = len(matrice)
	im = new("RGB", (width, height))
	pix = im.load()
	d = (255/100)
	for x in range(height):
		for y in range(width):
			if matrice[x][y] == 0:
				pix[y,x] = (0,0,0)
			elif matrice[x][y] == 1:
				pix[y,x] = (255,0,0)
			elif matrice[x][y] == 2:
				pix[y,x] = (0,255,0)
			else:
				pix[y,x] = (255,255,255)
	for segment in list(segments.keys()):
		for x in range(height):
			pix[segment,x] = (255,0,0)
	im.save(picture)
#----------------------------------------------------------------------------------------------------------------
def segment_points_words(matrice, histo_x, histo_y):
	pix_treshold_x = 40
	pix_treshold_y = 40

	height= len(matrice)
	width = len(matrice[0])

	segment_point_y = dict()
	local_range_y = int(width/ETALEMENT)

	min_loc_s = 0
	min_loc_e = 0
	n = 0
	sum_loc = 0
	for i in range(len(histo_y)): #Chope les min locaux Y (sur local_range)
		n = n + 1
		sum_loc = histo_y[i] + sum_loc
		if histo_y[min_loc_e] >= histo_y[i]:
			min_loc_e = i
		if histo_y[min_loc_s] > histo_y[i]:
			min_loc_s = i

		if n == local_range_y:
			moy = sum_loc/local_range_y
			if moy > 1:
				ecartype =( moyenne([(x-moy)**2 for x in histo_y[(i-local_range_y)::i]])) ** 0.5
			else:
				ecartype = 0
			if histo_y[min_loc_s] < pix_treshold_y and ecartype > PRECISION_W: #valeur prise au feeling
				segment_point_y[min_loc_s] = ecartype
			if min_loc_s != min_loc_e and histo_y[min_loc_e] < pix_treshold_y and ecartype > PRECISION_W: 
				segment_point_y[min_loc_e] = ecartype


			if i < len(histo_y) - 1: #On reboot pour les min locaux suivants
				min_loc_s = i + 1
				min_loc_e = i + 1
				n = 0
				sum_loc = 0

			else:
				break
	
	segment_point_y = correct_range_seg(segment_point_y)
	picture_segmentation_y(matrice, segment_point_y, "test_segmentation.png")
	return segment_point_y
#----------------------------------------------------------------------------------------------------------------
def correct_range_seg(segment_point_y, bad_range = 5):
	print("_____correct_range_______")
	old_i = -1
	key_to_del = []
	appended = False
	for i in segment_point_y.keys():
		if appended:
			old_i = i
			appended = False
		elif old_i == -1:
			old_i = i
		else:
			if i - old_i <= bad_range:
				key_to_del.append(i)
				appended = True
			else:
				old_i = i
	for i in key_to_del:
		del segment_point_y[i]
	return segment_point_y
#----------------------------------------------------------------------------------------------------------------
def segment_points(matrice, histo_x, histo_y):
	pix_treshold_x = 40
	pix_treshold_y = 40

	height= len(matrice)
	width = len(matrice[0])

	segment_point_x = dict()
	segment_point_y = dict()
	local_range_x = int(height/ETALEMENT)
	local_range_y = int(width/ETALEMENT)
	n = 0
	min_loc_s = 0
	min_loc_e = 0
	sum_loc = 0
	#min_loc : La position du min local, sum_loc = la somme local des pixels
	for i in range(0,len(histo_x),EPAISSEUR): #Chope les min locaux X (sur local_range)
		n = n + 1
		sum_loc = histo_x[i] + sum_loc
		if histo_x[min_loc_e] >= histo_x[i]:
			min_loc_e = i
		if histo_x[min_loc_s] > histo_x[i]:
			min_loc_s = i

		if n == local_range_x:
			moy = sum_loc/local_range_x
			if moy > 1:
				ecartype =( moyenne([(x-moy)**2 for x in histo_x[(i-local_range_x)::i]])) ** 0.5
			else:
				ecartype = 0
			if histo_x[min_loc_s] < pix_treshold_x and ecartype > PRECISION: #valeur prise au feeling
				segment_point_x[min_loc_s] = (ecartype, histo_x[min_loc_s])
			if min_loc_s != min_loc_e and histo_x[min_loc_e] < pix_treshold_x and ecartype > PRECISION: 
				segment_point_x[min_loc_e] = (ecartype, histo_x[min_loc_e])

			if i < len(histo_x) - 1: #On reboot pour les min locaux suivants
				min_loc_s = i + 1
				min_loc_e = i + 1
				n = 0
				sum_loc = 0
			else:
				break

	return segment_point_x

#----------------------------------------------------------------------------------------------------------------
def find_clusters(segment_point_x): #Retourne les groupes de cluster (liste de liste)
	clusters = [[] for i in range(len(segment_point_x))]
	keys = [0 for i in range(len(segment_point_x))]
	dist_moy = 0
	c = 0
	reduction_moyenne = 1
	#Moyenne des distances entre les segments
	for i in segment_point_x:
		keys[c] = i
		c = c + 1
	c = 0
	for i in range(len(keys) - 1):
		dist_moy = dist_moy + (keys[i+1] - keys[i])
	dist_moy = (dist_moy/len(segment_point_x))/reduction_moyenne

	#On rentre les clusters
	clusters[0].append(keys[0])
	if len(keys) > 1:
		if (keys[1] - keys[0]) > dist_moy:
			c = 1
		for i in range(1,len(keys),1):
			if i==len(keys) - 1 and (keys[i] - keys[i-1]) > dist_moy: # <-- On arrive dans ce cas là 
																	  #seulement si le dernier 
				clusters[c].append(keys[i])							  # cluster ne contient qu'un élément
			elif i<len(keys) - 1 and (keys[i+1] - keys[i]) > dist_moy:
				if keys[i] not in clusters[c]:
					c = c + 1
					clusters[c].append(keys[i])
				else:
					c = c + 1
			else:
				if keys[i] not in clusters[c]:
					clusters[c].append(keys[i])
				if i<len(keys) - 1:
					clusters[c].append(keys[i+1])

	return (clusters, dist_moy)

#----------------------------------------------------------------------------------------------------------------
def perfect_clusting(clusters): #Cette fois clusters est juste une liste simple de valeurs, 1938 = arrêt
	keys = [0 for i in range(len(clusters))]
	dist_moy = 0
	delete = []
	limit_lines = []
	for i in range(len(clusters) - 1):
		if len(clusters[i])==0:
			del(clusters[i])


	for i in range(len(clusters) - 1):
		dist_moy = dist_moy + (keys[i+1] - keys[i])
	dist_moy = dist_moy/len(segment_point_x)

	for i in range(len(clusters) - 1):
		for j in range(len(clusters[i])):	
			if clusters[i] == 1938: # On s'arrête ici pour tester
				break
			if math.fasb(clusters[i][-1] - clusters[i+1][0]) > dist_moy: # On est tombé sur un couple de line
				limit_lines.append((clusters[i][-1], clusters[i+1][0]))

#----------------------------------------------------------------------------------------------------------------
def good_candidate_lines(clusters, dist_moy): #Retourne des bons candidats de split des lignes(une liste de tuple)
	lines_tuples = [None for i in range(4)]
	for i in range(len(lines_tuples)):
		if len(clusters) > i + 1 and (clusters[i+1][0] - clusters[i][len(clusters[i]) - 1] ) > dist_moy:
			(t,d) = (clusters[i][len(clusters[i]) - 1], clusters[i+1][0])
			lines_tuples[i] = (t,d)
	return lines_tuples	
#----------------------------------------------------------------------------------------------------------------
def one_pix_histo_words(matrice, line): # Retourne l'histo d'une bande de largeur 1 px
	return [1 if matrice[i][line] == 0 else 0 for i in range(len(matrice))]
def one_pix_histo(matrice, line): # Retourne l'histo d'une bande de largeur 1 px
	return [1 if matrice[line][i] == 0 else 0 for i in range(len(matrice[line]))]
def fus_histo(h1, h2, width): #h1 est au dessus (mais peu importe), retourne la fusion de h1 et h2
	h = [0 for i in range(width)]
	for i in range(width):
		h[i] = h1[i] + h2[i]
	return h
def dist_couple(c1, c2): # retourne -1 si la distance est trop grande
	(g,d) = c1
	(g2, d2) = c2
	loc_dist = math.fabs(d - d2) + math.fabs(g - g2)
	connected = False
	if g <= g2:
		if d >= g2:
			connected = True
	if g >= g2:
		if d2 >= g:
			connected = True
	taille_dist = math.fabs((g-d) - (g2-d2))
	#med_res = compare_mediane(c1,c2)
	dist = taille_dist+ loc_dist
	if connected or DIFF_DIST > dist:
		return dist
	else:
		return -1
	



def check_dic(links, v): #Retourne vrai si c'est dans le dic avec la distance et le b1 lié
	for (b2, (b1, dist) ) in links.items():
		if v == b1:
			return (True, dist,b2)
	return (False, 0, 0)
def find_key(input_dict, value):
    return next((k for k, v in input_dict.items() if v == value), None)
#----------------------------------------------------------------------------------------------------------------
def histo_bosses(h): #Retourne des couples encadrants toutes les bosses d'un histo de largeur 1 PX!!
	bosses = []
	(t,d) = (-1,-1)
	for i in range(len(h)):
		if h[i] == 1 and t == -1: #On chope le début d'une bosse
			t = i
		elif t != -1 and d == -1 and h[i] == 0: # On chope la fin de la bosse
			d = i - 1
			bosses.append((t,d))
			(t,d) = (-1,-1)
	return bosses
#----------------------------------------------------------------------------------------------------------------
def compare_mediane(c1, c2):
	(g,d) = c1
	(g2, d2) = c2
	m1 = math.fabs(g-d)
	m2 = math.fabs(g2-d2)
	return math.fabs(m1-m2)

#----------------------------------------------------------------------------------------------------------------
def min_links(links, b1, index = 0): #Retourne le couple possédant la valeur minimal (un c2), cette valeur est
	link_min = -1					 # supprimée du dico
	c1_trash = 0
	for i in range(len(links)):
		if len(links[b1[i]]) == 0:
			del links[b1[i]]
			del b1[i]
		else:
			if link_min == -1:

				link_min = links[b1[i]][index]
				(c2, dist) = links[b1[i]][index]
			else:
				(n_c2, n_dist) = links[b1[i]][index]
				if n_dist < dist:
					link_min = links[b1[i]][index]
					c1_trash = i
				(c2, dist) = (n_c2, n_dist)

	links = del_links(links, link_min, b1[c1_trash])
	(c2, dist) = link_min
	return (links,c2)

#----------------------------------------------------------------------------------------------------------------
def del_links(links, link_min, key_to_del): #Suppression de toute les redondances de c2 dans link_min dans links
	# key_to_del est le b1 qu'il faut supprimer
	(c2_min, dist) = link_min
	del links[key_to_del]

	for i in links:
		for j in i:
			(c2, dist) = j
			if c2 == c2_min:
				del j
	del key_to_del
	return links
#----------------------------------------------------------------------------------------------------------------


''' tips&tricks : 
	b1 et b2 sont des tableaux de couples (appelés c1 ou c2), les couples représentent les bosses d'une ligne
'''
def compare_bosses(b1, b2): 
	# supprimer avant de passer à la prochaine comparaison
	# Compare le premier couple de b2 avec tout ceux de b1
	# links ne contient que des distances acceptables
	# Retourne : les couples de b2 acceptables
	links = dict() #Clé : b1, valeur : tableau de 0 à len(b2) de couple (b2, dist) 
	ok_c2 = 0 #Couple de b2 acceptable
	clean_b2 = [] #b2 sans toutes ces bosses appartenant à une autre ligne
	if len(b1) == 0: # Alors on a finit la segmentation
		return True
	#1st step : Rassembler les couples proches dans link
	for i in range(len(b1)):
		links[b1[i]] = None
		for j in range(len(b2)):
			dist = dist_couple(b1[i], b2[j])
			if dist != -1:
				if links[b1[i]] == None:
					links[b1[i]] = (b2[j],dist)
				else:
					(c2, d) = links[b1[i]]
					if dist < d:
						links[b1[i]] = (b2[j],dist)

	for i in links.values():
		if i != None:
			(c2, d) = i
			clean_b2.append(c2)

	return clean_b2

#----------------------------------------------------------------------------------------------------------------
def left_line(t, matrice, width, height):
	if t < width - DEPLACEMENT_LIGNE:
		return None

	h1 = one_pix_histo_words(matrice,t)
	b1 = histo_bosses(h1)
	new_t = t
	old_r = 0
	for i in range(t-1, t-125, -1):
		if i != t - 1:
			b1 = b2	

		h2 = one_pix_histo_words(matrice,i)
		b2 = histo_bosses(h2)
		b2 = compare_bosses(b1,b2)

		if b2 == [] or b2 == True:
			new_t = i
			break
		for (l,r) in b2:
			for j in range(old_r, l, 1):
				matrice[i][j] = 255
			for j in range(l, r, 1):
				matrice[i][j] = 2	
			old_r = r	

		for j in range(old_r, len(matrice[0]), 1):
			matrice[i][j] = 255
		old_r = 0
	return new_t

#----------------------------------------------------------------------------------------------------------------
def right_line(d, matrice, width, height):
	if d < width - DEPLACEMENT_LIGNE:
		return None
	h1 = one_pix_histo_words(matrice,d)
	b1 = histo_bosses(h1)

	new_d = 0
	old_r = 0
	for i in range(d+1, d+125, 1):
		if i != d + 1:
			b1 = b2	

		h2 = one_pix_histo_words(matrice,i)
		b2 = histo_bosses(h2)

		b2 = compare_bosses(b1,b2)
		if b2 == [] or b2 == True:
			new_d = i
			break

		for (l,r) in b2:
			for j in range(old_r, l, 1):
				matrice[i][j] = 255
			for j in range(l, r, 1):
				matrice[i][j] = 1
			old_r = r

		for j in range(old_r, len(matrice[0]), 1):
			matrice[i][j] = 255
		old_r = 0

	return new_d
#----------------------------------------------------------------------------------------------------------------
def down_line(d, matrice, width, height):
	h1 = one_pix_histo(matrice,d)
	b1 = histo_bosses(h1)

	new_d = 0
	old_r = 0
	for i in range(d+1, d+400, 1):
		if i != d + 1:
			b1 = b2	

		h2 = one_pix_histo(matrice,i)
		b2 = histo_bosses(h2)
		b2 = compare_bosses(b1,b2)
		if b2 == [] or b2 == True:
			new_d = i
			break

		for (l,r) in b2:
			for j in range(old_r, l, 1):
				matrice[i][j] = 255
			for j in range(l, r, 1):
				matrice[i][j] = 0
			old_r = r

		for j in range(old_r, len(matrice[0]), 1):
			matrice[i][j] = 255
		old_r = 0
	return new_d
#----------------------------------------------------------------------------------------------------------------
def top_line(t, matrice, width, height):
	h1 = one_pix_histo(matrice,t)
	b1 = histo_bosses(h1)
	new_t = t
	old_r = 0
	for i in range(t-1, t-125, -1):
		if i != t - 1:
			b1 = b2	

		h2 = one_pix_histo(matrice,i)
		b2 = histo_bosses(h2)

		b2 = compare_bosses(b1,b2)
		if b2 == [] or b2 == True:
			new_t = i
			break
		for (l,r) in b2:
			for j in range(old_r, l, 1):
				matrice[i][j] = 255
			for j in range(l, r, 1):
				matrice[i][j] = 0
			old_r = r	

		for j in range(old_r, len(matrice[0]), 1):
			matrice[i][j] = 255
		old_r = 0
	return new_t

#----------------------------------------------------------------------------------------------------------------

def line_delimit_words(cluster, matrice, width, height): 
	# Encadre la ligne, efface les écritures n'appartenant pas à la ligne 
	(t,d) = cluster							 # puis retourne
	new_cluster = 0
	i = 0
	new_d = right_line(d, matrice, width, height)
	new_t = left_line(t, matrice, width, height)
	if new_t == None or new_d == None:
		return None
	new_clusters = (new_t, new_d)

	return new_clusters

def line_delimit(cluster, matrice, width, height): 
	# Encadre la ligne, efface les écritures n'appartenant pas à la ligne 
	(t,d) = cluster							 # puis retourne
	new_cluster = 0
	i = 0
	new_d = down_line(d, matrice, width, height)
	new_t = top_line(t, matrice, width, height)
	if new_t == None or new_d == None:
		return None
	new_clusters = (new_t, new_d)

	return new_clusters
#----------------------------------------------------------------------------------------------------------------
def copy_matrice(matrice):
	old_matrice = [[255 for j in range(len(matrice[0]))] for i in range(len(matrice))]
	for i in range(len(matrice)):
		for j in range(len(matrice[0])):
			old_matrice[i][j] = matrice[i][j]
	return old_matrice
#----------------------------------------------------------------------------------------------------------------
def in_cluster(cluster1, cluster2): 
	# Vérifie si cluster1 est dans cluster2, en supposant que cluster 2 est en haut
	(t1,d1) = cluster1
	(t2,d2) = cluster2
	if t2 - t1 >= 0 :
		return True
	elif d2 - d1 >= 0 :
		return True
	return False


#----------------------------------------------------------------------------------------------------------------
# Retourne les clusters là ou l'histo est nul
# Avec un nombre représentant l'écart d'un espace moyen
def check_space(histo):
	acceptable_length = 5
	space_clusters = []
	left = -1
	somme_letter_cluster = 0
	cur_somme = 0
	number_of_letter_cluster = 0
	inside = False
	#Première espace
	(fi, fj) = (0,-1)
	for i in range(len(histo)):
		if histo[i] != 0 and fj == -1:
			fj = i
			space_clusters.append((fi,fj))
		else:
			if histo[i] != 0:
				cur_somme += 1
			if histo[i] == 0 and left == -1:
				if cur_somme>acceptable_length:	
						number_of_letter_cluster += 1
						somme_letter_cluster += cur_somme
						cur_somme = 0
				left=i

			elif histo[i] != 0 and left != -1:
				space_clusters.append((left,i))
				left = -1
				inside = True

	#chope le dernier espace
	for i in range(len(histo)-1, 0,-1):
		if histo[i] != 0:
			space_clusters.append((i+1,len(histo)-1))
			break

	if number_of_letter_cluster > 0:
		avg_space_lenght = somme_letter_cluster/number_of_letter_cluster
	else:
		avg_space_lenght = 0
	print(space_clusters)
	return (space_clusters,avg_space_lenght)

#----------------------------------------------------------------------------------------------------------------
def add_lines_to_image(segment_point, matrice, width, height, image):
	'''
	retourne une liste de matrice correspondant à chaque lignes coupées
	'''
	if len(segment_point) == 0:
		print("la taille de segment_point est égale à 0, pas de min/max locaux intéressants (add_lines_to_image)")
		return None
	(width, height) = (len(matrice[0]),len(matrice))
	dist_moy = 0

	(clusters,dist_moy) = find_clusters(segment_point)
	clusters = [i for i in clusters if i != []]
	clusters = good_candidate_lines(clusters,dist_moy)
	print(clusters)
	
	#On retire les None de clusters
	n_clusters= []
	for c in clusters:
		if c != None:
			n_clusters.append(c)
	clusters = n_clusters
	print(clusters)
	#Ajustement des clusters pour rendre l'encadrement des lignes plus juste
	AJUST = 30
	c = 0
	for (t,d) in clusters:
		t = t + AJUST
		d = d - AJUST
		clusters[c] = (t,d)
		c += 1
	#print("clusters : "+str(clusters))

	
	
	old_matrice = copy_matrice(matrice)
	matrice_line = []
	(old_t, old_d) = (0,0)
	lines_matrices = []

	for (t,d) in clusters:
		(new_t, new_d) = line_delimit((t,d), matrice, width, height)
		if (old_t, old_d) != (0,0) and in_cluster((t,d),(old_t, old_d)):
			print("Le cluster "+str((t,d)) +" est dans le cluster" + str((old_t, old_d)))
		for i in range(new_t, new_d, 1):
			matrice_line.append(matrice[i])
		tools.build_picture(matrice_line, "line"+str((new_t, new_d))+".png", True, True)
		lines_matrices.append(matrice_line)
		matrice = copy_matrice(old_matrice)
		matrice_line = []
		(old_t, old_d) = (t,d)

	return lines_matrices
#----------------------------------------------------------------------------------------------------------------
def add_words_to_image(segment_point, matrice, width, height, image):
	pass

#----------------------------------------------------------------------------------------------------------------
def get_histo_from_matrice(matrice):
	histo_x = [0 for i in range(len(matrice))]
	histo_y = [0 for i in range(len(matrice[0]))]

	for x in range(len(matrice)):
		for y in range(len(matrice[0])):
			if matrice[x][y] == 0:
				histo_x[x] = histo_x[x] + 1 
				histo_y[y] = histo_y[y] + 1 
	return (histo_x, histo_y)



#----------------------------------------------------------------------------------------------------------------
def cut_words(lines_matrices):
	i = 0 
	for line_matrice in lines_matrices:
		(histo_x, histo_y) = get_histo_from_matrice(line_matrice)
		#Récupération des cluters avec espace
		(space_clusters,avg_space_lenght) = check_space(histo_y);			
		cut.cut_letter_with_space(space_clusters,avg_space_lenght,line_matrice,i)
		i =+ 1	
	
#----------------------------------------------------------------------------------------------------------------
def complet_cut(image_path, bin = False):
	tools.erase_tmp()
	#Transforme l'image en binaire
	(matrice, width, height, histo_x, histo_y) = rp.ready_pic(image_path, bin) 
	# chope les deux listes de lignes
	segment_point_x = segment_points(matrice, histo_x, histo_y)
	lines_matrices = add_lines_to_image(segment_point_x, matrice, width, height, 
		"new_"+image_path[0:len(image_path) - 3]+"png")
	cut_words(lines_matrices)

#----------------------------------------------------------------------------------------------------------------
def cut_word(image_path):
	tools.erase_tmp()
	#get matrice de l'espace
	(matrice, width, height, histo_x, histo_y) = rp.ready_pic(image_path) 
	(histo_x, histo_y) = get_histo_from_matrice(matrice)
	#check space sur la matrice
	(space_clusters,avg_space_lenght) = check_space(histo_y);
	#Appel à cut_letter
	cut.cut_word_alone(matrice)
#----------------------------------------------------------------------------------------------------------------
#Coupe un mot ou une phrase unique (pas besoin de passer par la segmentation de ligne)
def cut_word_bin(image_path, bin = True):
	tools.erase_tmp()
	matrice = rc.reframing_ret_mat(image_path, bin)
	#matrice = tools.get_matrice_from_pic(open(image_path))
	(histo_x, histo_y) = get_histo_from_matrice(matrice)
	(space_clusters,avg_space_lenght) = check_space(histo_y);
	cut.cut_letter_with_space(space_clusters,avg_space_lenght,matrice,0)
#----------------------------------------------------------------------------------------------------------------
#	TEST 
#----------------------------------------------------------------------------------------------------------------
#histo.load_static_model()
#complet_cut("code_public.jpg")
#complet_cut("letters_test.jpg")
#cut_word_bin("code_public.jpg")
#matrice = tools.get_matrice_from_pic("unified_td.png")
#get_histo_from_matrice(matrice)