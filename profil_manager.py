from PIL.Image import *
from random import randrange
from distutils.dir_util import copy_tree
import os
import math
import numpy
import ready_pic as rp
import tools as tools
FOLDER_STATIC = 'static/'
FOLDER_STATIC_DEF = 'default/'

#----------------------------------------------------------------------------------------------------------------
#Créer un profil
def create_profil(name):
	if profil_existence(name):
		print("profil "+str(name)+" déjà existant")
		return
	profil_path = FOLDER_STATIC+str(name)
	os.mkdir(profil_path , 770 )
	os.chmod(profil_path, 0o777)
	#Copie du folder par défaut dans le nouveau!
	copy_tree(str(FOLDER_STATIC)+str(FOLDER_STATIC_DEF), profil_path)
	print("création du profil réussi")

#----------------------------------------------------------------------------------------------------------------
#Vérifie l'existence d'un profil
def profil_existence(name):
	if not os.path.isdir(FOLDER_STATIC+str(name)):
		print("le profil n'existe pas")
		return False
	return True
#----------------------------------------------------------------------------------------------------------------
#Delete le profil
def delete_profil(name):
	profil_path = FOLDER_STATIC+str(name)
	pass
#----------------------------------------------------------------------------------------------------------------
def get_profils():
	profils = ""
	for path, dirs, files in os.walk("static"):
		for dirname in dirs:
			if dirname != "default" and dirname != "." and dirname != "..":
				profils += str(dirname)+" "
	print(profils)
	return profils

