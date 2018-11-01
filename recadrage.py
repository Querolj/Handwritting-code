from PIL.Image import *
from random import randrange
import os
import ready_pic as rp
import tools as tools


#Ici on recadre les samples et image manuscrite (après traitement rapidos pour que ca soit binaire) au pixel près
#TODO après l'écriture de l'algo : Adapter pour pouvoir agrandir une matrice
#l'implenter dans ready_pic pour ne pas lire 2 fois l'image
#----------------------------------------------------------------------------------------------------------------
#Retourne 4 points (couple), haut, bas, gauche et droite, pour les extrémités de la lettre dans l'image
def reframe(image, bin = False):
	im = open(image)
	(width, height) = im.size
	step_x = int(width/100)
	step_y = int(height/100)
	haut = (0,0)
	bas = ()
	gauche = ()
	droit = ()
	pixel = 50
	#Coté haut
	stop = False
	for x in range(0, height, step_x):
		if stop:
			break
		for y in range(width):
			if stop:
				break
			if bin:
				r = im.getpixel((y,x))
			else:
				(r, g, b) = im.getpixel((y,x))
			if r<pixel:
				haut = (y, x)
				for z in range(x, x-step_x, -1): #Vu qu'on fait des grands pas, faut revenir en arrière pour choper le pixelquiva
					if z == 0:
						stop = True
						break
					for y in range(width):
						if bin:
							r = im.getpixel((y,z))
						else:
							(r, g, b) = im.getpixel((y,z))
						if r <pixel:
							haut = (y,z)
							y = 0
							if z > x-step_x - 1:
								z = z - 1
							else:
								break
				stop = True
			if stop:
				break
		if stop or x + step_x > height -1:
			break
	#Coté bas
	stop = False
	for x in range(height - 1, 0, -step_x):
		if stop:
			break
		for y in range(width):
			if stop:
				break
			if bin:
				r = im.getpixel((y,x))
			else:
				(r, g, b) = im.getpixel((y,x))
			if r<pixel:
				bas = (y, x)
				for z in range(x+1, x+step_x, 1):
					if stop:
						break
					for y in range(width):
						if z >= height - 1:
							stop = True
							break
						if bin:
							r = im.getpixel((y,x))
						else:
							(r, g, b) = im.getpixel((y,z))
						if r <pixel:
							bas = (y,z)
							y = 0
							if z < x+step_x - 1:
								z = z + 1
							else:
								break
				stop = True
			if stop:
				break
		if stop or x - step_x < 0:
			break

	#Coté gauche
	stop = False
	for y in range(0, width, step_y):
		for x in range(height):
			if bin:
				r = im.getpixel((y,x))
			else:
				(r, g, b) = im.getpixel((y,x))
			if r<pixel:
				gauche = (y, x)
				for z in range(y-1, y-step_y, -1): #Vu qu'on fait des grands pas, faut revenir en arrière pour choper le pixelquiva
					for x in range(height):
						if bin:
							r = im.getpixel((y,x))
						else:
							(r, g, b) = im.getpixel((z,x))

						if r<pixel:
							gauche = (z,x)
							x = 0
							if z > y-step_y - 1:
								z = z - 1
							else:
								break
				stop = True
			if stop:
				break
		if stop or y + step_y > width -1:
			break

	#Coté droit
	stop = False
	for y in range(width - 1, 0, -step_y):
		for x in range(height):
			if bin:
				r = im.getpixel((y,x))
			else:
				(r, g, b) = im.getpixel((y,x))
			if r<pixel:
				droit = (y, x)
				for z in range(y+1, y+step_y, 1):
					for x in range(height):
						if bin:
							r = im.getpixel((y,x))
						else:
							(r, g, b) = im.getpixel((z,x))

						if r <pixel:
							droit = (z,x)
							x = 0
							if z < y+step_y - 1:
								z = z + 1
							else:
								break
				stop = True
			if stop:
				break
		if stop or y - step_y < 0:
			break

	#haut, gauche
	(hx, hy) = haut
	(gx, gy) = gauche
	haut_gauche = (gx, hy)
	#haut, droit
	(dx, dy) = droit
	haut_droit = (dx, hy)
	#bas, gauche
	(bx, by) = bas
	bas_gauche = (gx, by)
	#bas, droit
	bas_droit = (dx, by)
	return (haut_gauche, haut_droit, bas_gauche, bas_droit, im)

#----------------------------------------------------------------------------------------------------------------


def create_fresh_sample(haut_gauche, haut_droit, bas_gauche, bas_droit, im, dir ,picture):
	(hgx, hgy) = haut_gauche
	(hdx, hdy) = haut_droit
	(bgx, bgy) = bas_gauche
	(bdx, bdy) = bas_droit
	width = hdx - hgx
	height = bgy - hgy
	new_im = new("RGB", (width, height))
	pix = new_im.load()
	for x in range(hgy, bgy):
		for y in range(hgx, hdx):
			(r, g, b) = im.getpixel((y,x))
			if r == 0:
				pix[y-hgx,x-hgy] = (0,0,0)
			else:
				pix[y-hgx,x-hgy] = (255,255,255)
	new_im.save(str(dir)+'/new_'+str(picture))

def create_rep_fresh_sample(folder, is_static):
	if not os.path.isdir(folder):
		reframing(folder)
	else:
		d = os.listdir(folder)
		for path, dirs, files in os.walk(folder):
		    for filename in files:
		    	cur_dir = os.path.basename(path)
		    	if filename != "." and filename != ".." and (tools.is_new(filename) or is_static):
		    		filename_path = cur_dir +"/" + filename
		    		(haut_gauche, haut_droit, bas_gauche, bas_droit, im) = reframe(filename_path)
		    		create_fresh_sample(haut_gauche, haut_droit, bas_gauche, bas_droit, im, cur_dir, filename)
#----------------------------------------------------------------------------------------------------------------
def reframing(picture):
	(haut_gauche, haut_droit, bas_gauche, bas_droit, im) = reframe(picture)
	create_fresh_sample(haut_gauche, haut_droit, bas_gauche, bas_droit, im, picture) 
#----------------------------------------------------------------------------------------------------------------
#Reframe une image "presque" binaire, cad prise d'un ipad (certains pixel d'ecriture ne sont pas entièrement noir)
#, d'ou r < 50
def reframing_ret_mat(picture, bin = False):
	(haut_gauche, haut_droit, bas_gauche, bas_droit, im) = reframe(picture, bin)
	(hgx, hgy) = haut_gauche
	(hdx, hdy) = haut_droit
	(bgx, bgy) = bas_gauche
	(bdx, bdy) = bas_droit
	width = hdx - hgx
	height = bgy - hgy
	new_im = new("RGB", (width, height))
	pix = new_im.load()
	for x in range(hgy, bgy):
		for y in range(hgx, hdx):
			if bin:
				r= im.getpixel((y,x))
			else:
				(r, g, b) = im.getpixel((y,x))
			if r < 50:
				pix[y-hgx,x-hgy] = (0,0,0)
			else:
				pix[y-hgx,x-hgy] = (255,255,255)
	matrice = tools.get_matrice_from_pic(new_im)
	#tools.build_picture(matrice, "new_"+picture)
	return matrice
#----------------------------------------------------------------------------------------------------------------
# TEST UNITAIRE :
#----------------------------------------------------------------------------------------------------------------
#create_rep_fresh_sample("test_rdy")
#print(reframe("code_public.jpg", True))
#reframing_ret_mat("code_public.jpg", True)