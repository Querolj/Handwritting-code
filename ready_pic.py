from PIL.Image import *
from random import randrange
import tools as tools
import os

colors = dict()# Contient les clés : "carreau", "feuille", "trait". Les valeurs sont des tuples (color, nbr_de_pixel)
#La couleur de la feuille doit TOUJOURS être celle avec le plus de pixel.
#La couleur du carreau doit observer une REGULARITE
#Le reste c'est des traits (ou des carreaux bizarres, mais on verra par la suite)

#Last minute info !! : On ne fait pas encore les carreaux, d'abord feuille et trait (on verra plus tard les carreaux)
# -idem pour les carrés prient au hasard

#A partir de cb on a du blanc ? 95 = ca va
WHITE = 95
PICTURE = ""
#----------------------------------------------------------------------------------------------------------------
def select_point(size, n, square_size):
	(width, height) = size
	if n == 0: #Sur le quart gauche de la feuille
		px = randrange(0,width/2 - square_size )
		py = randrange(0, height/2 - square_size)
	elif n == 1:
		px = randrange(width/2,width - square_size )
		py = randrange(0, height/2 - square_size)
	elif n == 2:
		px = randrange(0,width/2 - square_size )
		py = randrange(height/2, height - square_size)
	elif n == 3:
		px = randrange(width/2,width - square_size )
		py = randrange(height/2, height - square_size)
	return (px, py)

#----------------------------------------------------------------------------------------------------------------
			
def check_color_order(): #Remet la couleur de la feuille à sa place (cad c'est la couleur avec le plus d'itération)
	(color, it) = colors["feuille"]
	(color3, it3) = colors["trait"]
	if it < it3:
		f = colors["trait"]
		colors["trait"] = colors["feuille"]
		colors["feuille"] = f

#----------------------------------------------------------------------------------------------------------------

def init_colors(n, color):
	if n==0:
		colors["feuille"] = (color, 1)
	elif n == 1:
		colors["trait"] = (color, 1)

#----------------------------------------------------------------------------------------------------------------
def color_detector(color): # Retourne True si une couleur similaire a déjà été récupérée et incrémente le nbr de pixels vu
						   # sinon False et ajoute cette couleur
	(r,g,b) = color
	for k in colors:
		((r2, g2, b2), it) = colors[k]
		if distance_color((r,g,b), (r2, g2, b2)) < 20:
			it = it + 1 
			return True

#----------------------------------------------------------------------------------------------------------------

#TODO : teste d'assombrissement de la couleur
def distance_color(color1, color2):  # Retourne la distance entre deux couleurs, min = 0 (couleurs identiques), 
									 #max = 255*3 (blanc et noir)
	(r,g,b) = color1
	(r2, g2, b2) = color2
	return abs(r2-r) + abs(g2-g) + abs(b2-b)
#----------------------------------------------------------------------------------------------------------------
def is_black(color): # Vrai = noir
	(r,g,b) = color
	if r < WHITE and g < WHITE and b < WHITE:
		return True
	return False

#----------------------------------------------------------------------------------------------------------------
def no_grain(matrice, x, y, width, height): #Vérifie les pixels voisins pour voir si le pixel n'est pas un grain paumé
	n = 0
	anti_grain_strenght = 1 #Conseillé : 1 max, plus fort et on commence à affiner l'écriture donc perdre de l'info
	if y > 1 and matrice[x][y - 1] == 0:
		n = n + 1
	if y < width - 2 and matrice[x][y + 1] == 0:
		n = n + 1
	if x > 1:
		if x > 0 and matrice[x - 1][y] == 0:
			return True
		if x > 0 and y > 0 and matrice[x - 1][y - 1] == 0:
			return True
		if y < width -1 and x > 0 and matrice[x - 1][y + 1] == 0:
			return True
	#Si c'est au bord gauche
	if n > anti_grain_strenght:
		return True # C'est un trait
	else:
		return False # propablement un grain random


#----------------------------------------------------------------------------------------------------------------
def read_picture(im,width, height, picture, bin = False):
	n = 0 # n sert à initialiser le dictionnaire
	histo_x = [0 for i in range(height)]
	histo_y = [0 for i in range(width)]
	matrice = [[100 for j in range(width)] for i in range(height)]
	(nr, ng, nb) = (0,0,0)
	for x in range(height):
		for y in range(width):
			if x == 0 or x == height - 1 or y == width - 1: 
				#on veut encadrer l'image d'une couche de taille un pixel de couleur blanc
				matrice[x][y] = 255
			elif y == 0:
				matrice[x][y] = 255
				if bin:
					nr = im.getpixel((y+1,x))
				else:
					(nr, ng, nb) = im.getpixel((y+1,x))
				if x % 3 == 0 and n>1:
					check_color_order() #On vérifie périodiquement si la couleur de la feuille est la bonne
			else:
				if is_black((nr, ng, nb)):
					matrice[x][y] = 0
					#Ranger dans les deux histogrammes les pixels car le trait est noir
					histo_x[x] = histo_x[x] + 1
					histo_y[y] = histo_y[y] + 1
				else:
					matrice[x][y] = 255
				if n < 2:
					init_colors(n, (nr, ng, nb))
					n = n + 1
				if y < width - 1:
					if bin:
						nr = im.getpixel((y+1,x))
					else:
						(nr, ng, nb) = im.getpixel((y+1,x))

			

			
			#if x > 4 and x % 2 ==0:
			#	check_regularity() #Vérifie la régularité de carreau et trait
	create_pict_test(matrice, width, height, picture)
	return (matrice, width, height, histo_x, histo_y)
	

def create_pict_test(matrice, width, height, picture):
	im = new("RGB", (width, height))
	pix = im.load()
	for x in range(height):
			for y in range(width):
				if matrice[x][y] == 0 and no_grain(matrice, x, y, width, height):
					pix[y,x] = (0,0,0)
				else:
					pix[y,x] = (255,255,255)
	im.save(picture)

#----------------------------------------------------------------------------------------------------------------
def ready_pic(picture_path, bin = False):
	was_path = False
	picture =""
	picture_to_save = ""
	for i in range(len(picture_path) -1,0,-1):
		if picture_path[i] == "/":
			picture = picture_path[:i+1] + picture_path[i+1:len(picture_path)]
			picture_to_save = picture_path[:i+1] + "new_"+picture_path[i+1:len(picture_path) - 3]+"png"
			was_path = True
	if not was_path:
		for i in range(len(picture_path)):
			if picture_path[i] == ".":
				picture = "new_"+picture_path[:i+1]+"png"
				picture_to_save = picture
				break


	print(picture_path)
	im = open(picture_path)
	(width, height) = im.size
	if was_path:
		return read_picture(im,width, height, picture_to_save, bin)
	else:
		print("saving : "+picture_to_save)
		return read_picture(im,width, height, picture_to_save, bin)

#----------------------------------------------------------------------------------------------------------------
def ready_rep(folder):
	if not os.path.isdir(folder):
		ready_pic(folder)
	else:
		d = os.listdir(folder)
		for path, dirs, files in os.walk(folder):
		    for filename in files:
		    	cur_dir = os.path.basename(path)
		    	if filename != "." and filename != "..":
		    		filename_path = cur_dir +"/" + filename
		    		ready_pic(filename_path)

#----------------------------------------------------------------------------------------------------------------
# TESTS UNITAIRES :
#----------------------------------------------------------------------------------------------------------------
#ready_pic("a4.jpg")
#ready_rep("test_rdy")