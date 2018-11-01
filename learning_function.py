from PIL.Image import *
import os
import char_model as cm
import tools as tools
import csv
import sqlite3
#Vielle base de donnée, ne sert plus


TAILLE_UNIF = 100 #Attention valeur partagée avec unification.py

def process_sample(sample, char_name, model_path):
	i = open(sample)
	model = cm.Char_model(char_name, model_path)
	model.add_sample(sample, model_path)
	return model
#----------------------------------------------------------------------------------------------------------------
#Charge une image static et la met dans all_model et le retourne (ne gère pas l'exeption si ce n'est pas dans all_model)
def load_base(static_model, sample_num, char_name):
	im = open(static_model)
	(width, height) = im.size
	model = cm.Char_model(char_name)
	model.sample_len = sample_num
	for x in range(TAILLE_UNIF):
		for y in range(TAILLE_UNIF):
			(r, g, b) = im.getpixel((y,x))
			if r != 255:
				model.matrice[x][y] = r

	return model
#----------------------------------------------------------------------------------------------------------------
def Load_csv_to_all_model():
	all_model = dict()
	if os.path.exists("all_model.csv"):
		static_model = csv.writer(csv.open("all_model.csv", "r"))
		for row in static_model:
			all_model[row[0]] = load_base(row[2], row[1], row[0])

	return all_model

#----------------------------------------------------------------------------------------------------------------

#Ce modèle existe-t-il dans all_model.csv ?
def is_existing(model_name):
	static_model = csv.writer(csv.open("all_model.csv", "rb"))
	for row in static_model:
		if model_name in row:
			return True
	return False
#Ecrit une colonne simple dans all_model.csv, sans check quoi que ce soit
def write_base(model_name, sample_num):
	static_model = csv.writer(csv.open("all_model.csv", "wb"))
	static_model.writerow([model_name, sample_num])
#----------------------------------------------------------------------------------------------------------------
#Fusionne les fichiers d'un dossier
def learn_base(rep, model_name):
	#all_model = Load_csv_to_all_model()
	all_model = dict()
	d = os.listdir(rep)
	n = 0
	for path, dirs, files in os.walk(rep):
	    for filename in files:
	    	cur_dir = os.path.basename(path)
	    	if tools.is_unified(filename) :#!= "." and filename != "..":
	    		cur_sample = os.path.abspath(rep+"/"+filename)
	    		print(cur_sample)
	    		model_path = rep+"/"+filename
	    		if model_name in all_model:
	    			all_model[model_name].add_sample(cur_sample, model_path)
	    		else:
	    			all_model[model_name] = process_sample(cur_sample, model_name, model_path)

	return all_model

#----------------------------------------------------------------------------------------------------------------
def create_db():
	all_model_db = sqlite3.connect("all_model.db")
	c = all_model_db.cursor()
	# Create table
	c.execute('''CREATE TABLE all_model
	             (model_name text PRIMARY KEY, sample_len real, model_path text)''')
	all_model_db.close()
#----------------------------------------------------------------------------------------------------------------
#Insert les données d'un modèle dans la DB, met à jour si le modèle existe déjà
def upsert_db(model_name, sample_len, model_path = ""):
	print(model_path[0:len(model_path) - 4])
	model_path = model_path[0:len(model_path) - 4]
	all_model_db = sqlite3.connect("all_model.db")
	c = all_model_db.cursor()
	c.execute("INSERT OR REPLACE INTO all_model VALUES ('"+model_name+"','"+str(sample_len)+"','"+model_path+"')")
	all_model_db.commit()
	all_model_db.close()
#----------------------------------------------------------------------------------------------------------------
#retourne all_model avec tout le contenu de la db
def load_db():
	all_model = dict()
	all_model_db = sqlite3.connect("all_model.db")
	c = all_model_db.cursor()
	for row in c.execute("SELECT * FROM all_model"):
		(model_name, sample_len, model_path) = row
		print((model_name, sample_len, model_path))
		all_model[model_name] = cm.Char_model(model_name, model_path, sample_len)
	return all_model
#----------------------------------------------------------------------------------------------------------------
def print_db():
	all_model_db = sqlite3.connect("all_model.db")
	c = all_model_db.cursor()
	for row in c.execute("SELECT * FROM all_model"):
		print(row)
	all_model_db.close()
#----------------------------------------------------------------------------------------------------------------
#Met tout ce qu'il y a dans all model dans le fichier csv
def init_csv(all_model):
	if os.path.exists("all_model.csv"):
		static_model = csv.writer(csv.open("all_model.csv", "w"))
		for model in all_model:
			static_model.writerow([model.model_name, model.sample_len, model.model_path])
	else:
		print("le fichier csv n'existe pas"	)

#----------------------------------------------------------------------------------------------------------------
#Supprime le model_name de la db
def remove_db(model_name):
	all_model_db = sqlite3.connect("all_model.db")
	c = all_model_db.cursor()
	c.execute("DELETE FROM all_model WHERE model_name="+model_name)
	all_model_db.commit()
#----------------------------------------------------------------------------------------------------------------
#la picture doit être unifié, le model_name doit exister dans all_model
def add_knowledge(model_name, picture, all_model, create_picture = True):
	im_to_add = open(picture)
	im_static = open(all_model[model_name].model_path+".png")
	(width, height) = im_to_add.size
	matrice = [[0 for j in range(width)] for i in range(height)]
	all_model[model_name].sample_len = all_model[model_name].sample_len + 1
	print(all_model[model_name].sample_len)
	for x in range(height):
		for y in range(width):
			(r, g, b) = im_to_add.getpixel((y,x))
			(moy, g, b) = im_static.getpixel((y,x))
			pixel = (moy - r) / all_model[model_name].sample_len
			matrice[x][y] = moy - pixel
	if create_picture:
		all_model[model_name].matrice = matrice
		create_matrix_image(all_model[model_name], False)
#----------------------------------------------------------------------------------------------------------------
#Fout tous les images chargées dans le rep, dans all_model[model_name]
def start(rep, model_name):
	all_model = learn_base(rep, model_name)
	l = all_model.values()
	return all_model
#----------------------------------------------------------------------------------------------------------------

def create_matrix_image(model, percentage = True):
	im = new("RGB", (100, 100))
	pix = im.load()
	d = (255/100)
	for x in range(100):
			for y in range(100):
				if percentage:
					r = model.matrice[x][y] * d
				else:
					r = model.matrice[x][y]
				pix[y,x] = (int(r),int(r),int(r))
	im.save(model.model_name+".png")

#Met à jour all_model.csv et les images des modèles static
def create_all_matrix(all_model):
	#create_db()
	for i in all_model:
		upsert_db(all_model[i].model_name, all_model[i].sample_len, all_model[i].model_path)
		create_matrix_image(all_model[i])
	print_db()

