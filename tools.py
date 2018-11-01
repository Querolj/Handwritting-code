from PIL.Image import *
from random import randrange
import os
'''
Contient des fonctions pour gérer les fichiers et dossiers
'''

#----------------------------------------------------------------------------------------------------------------
def check_type(var):
	for c in var:
		if c=='.':
			try:
				var = float(var)
				return var
			except ValueError:
				return var
	try:
		var = int(var)
		return var
	except ValueError:
		return var	

def convert_list(l):
	return [float(s) for s in l]

def erase_tmp():
	for path, dirs, files in os.walk("tmp"):
		for filename in files:
			if filename != "." and filename != ".." and filename != ".DS_Store":
				os.unlink("tmp/"+str(filename))

def n_min(res,n,mins):
    mini = 9999
    val_ret = (0,0)
    for k,v in res.items():
        if v < mini:
            mini = v
            val_ret = (k,v)
    (k,v) = val_ret
    mins.append(val_ret)
    del res[k]
    if n != 0:
        return n_min(res, n-1, mins)
    else:
        return mins
        
def getWH_from_pic(picture):
	im = open(picture)
	return im.size

def getWH(matrice):
	return (len(matrice[0]), len(matrice))

def get_matrice_from_pic(im):
	#im = open(picture)
	(width, height) = im.size
	matrice = [[255 for j in range(width)] for i in range(height)]

	for i in range(height):
		for j in range(width):
			(r,g,b) = im.getpixel((j,i));
			if r<50:
				matrice[i][j] = 0;
	return matrice

def get_histo_2axis(matrice):
	(width, height) = getWH(matrice)
	histo_x = [0 for i in range(height)]
	histo_y = [0 for i in range(width)]

	for i in range(height):
		for j in range(width):
			if matrice[i][j] == 0:
				histo_y[j] = histo_y[j] + 1
				histo_x[i] = histo_x[i] + 1
	return (histo_x, histo_y)

def split_file_rep(path):
	file = ""
	rep = ""
	was_path = False
	for i in range(len(path) -1,0,-1):
		if path[i] == "/":
			file = path[:i+1] + path[i+1:len(path)]
			rep = path[:i+1]
			was_path = True
	return (file, rep, was_path)

def is_new(path):
	for i in range(len(path) - 5):
		if path[i] == "n":
			if path[i:i+3] == "new":
				return True
	return False

def is_unified(path):
	for i in range(len(path) - 5):
		if path[i] == "u":
			if path[i:i+7] == "unified":
				return True
	return False

def open_csv(csv_file, mode, newline=''):
	return open(csv_file, mode)

def build_picture(matrice, picture, red = False, green = False):
	width = len(matrice[0])
	height = len(matrice)
	im = new("RGB", (width, height))
	pix = im.load()
	d = (255/100)
	for x in range(height):
		for y in range(width):
			if matrice[x][y] == 0:
				pix[y,x] = (0,0,0)
			elif red and matrice[x][y] == 1:
				pix[y,x] = (255,0,0)
			elif green and matrice[x][y] == 2:
				pix[y,x] = (0,255,0)
			else:
				pix[y,x] = (255,255,255)
	im.save(picture)

def simple_build_picture(matrice, picture, reverse = False):
	width = len(matrice[0])
	height = len(matrice)
	im = new("RGB", (width, height))
	pix = im.load()
	d = (255/100)
	if reverse:
		c1 = 255
		c2 = 0
	else:
		c1 = 0
		c2 = 255
	for x in range(height):
		for y in range(width):
			if matrice[x][y] == 0:
				pix[y,x] = (c1,c1,c1)
			else:
				pix[y,x] = (c2,c2,c2)
	im.save(picture)

#retourne True si 0 octet
def is_file_null(file):
	info = os.stat(file)
	if info.st_size == 0:
		return True
	return False

def fus_matrice(m1,m2):
	pass

#Interval sur l'axe x
def get_portion_from_matrice(interval, matrice):
	(l,r) = interval
	return matrice[l:r]
	#return [for j in range(l,r,1) for i in range(len(matrice)))]

#----------------------------------------------------------------------------------------------------------------
# TEST UNITAIRE :
#----------------------------------------------------------------------------------------------------------------
