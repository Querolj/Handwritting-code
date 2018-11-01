import math
from PIL import Image as pl
from PIL import ImageDraw as id
import os
import tools as tools
import learning_manager as lm

#Variation de proportion acceptable : (lp/mp )
PROP_OK = 2
#Dans cette classe sont classés tous les modèles statics
model_static = []


def convert_list(l):
    for i in range(len(l)):
        l[i] = float(l[i])
    return l
class Histogram:

    def __init__(self,image):
        self.imageNom = image[0:len(image)-4]
        #self.image = pl.open(image)
        (histo_x, histo_y, proportion, char, number) = lm.load_file(self.imageNom)
        self.proportion = proportion
        self.liste_xpixel = convert_list(histo_x)
        self.liste_ypixel = convert_list(histo_y)
        self.scoreCurve = []
        self.scoreCurveBool = []
        self.matriceVectorPixel = [[]]
        self.resultList = []


    def scoringPart(self,list):
        score = 0
        for elt in range(len(list)-1):
            score += (list[elt]-list[elt+1])
            #score += (list[elt][1]-list[elt+1][1])
        self.scoreCurve.append(score)

    def compareScoring(self,listToCompare, proportion):
        score = 0
        cmp_prop = proportion/self.proportion
        if cmp_prop > 0.5 and cmp_prop < 2:
            for i in range(len(listToCompare)):
                score+=math.fabs(self.scoreCurve[i]-listToCompare[i])
        else:
            score = 999
        return score

    def inverseY(self,y):
        return (self.image.size[1]-1)-y

    def inverseX(self,x):
        return (self.image.size[0]-1)-x

    def toBooleanScoring(self):
        self.scoreCurveBool = [i > 0 for i in self.scoreCurve]

    def totalScoring(self):
        for i in range(0,len(self.liste_xpixel),10):
            #print(self.liste_xpixel[i:i+10])
            self.scoringPart(self.liste_xpixel[i:i+10])
        for i in range(0, len(self.liste_ypixel), 10):
            self.scoringPart(self.liste_ypixel[i:i + 10])

    def mini(d):
        minimum = -1
        matching_letters = []
        for k, v in d.items():
            if minimum == -1:
                minimum = v
                matching_letters.append(k)
            else:
                if minimum > v:
                    minimum = v
                    matching_letters = []
                    matching_letters.append(k)
                elif minimum == v:
                    matching_letters.append(k)
        return matching_letters


def count_pixel_x_matrice(port_matrice):
    number_pxl = 0
    hx = []
    (width,height) = tools.getWH(port_matrice)
    for i in range(width): #width, height
        for j in range(height):
            if port_matrice[i][j] == 0:
                number_pxl = number_pxl + 1
            elif port_matrice[i][j] < 254:
                number_pxl = (number_pxl + math.fabs(((port_matrice[i][j]/254)-1)))

        hx.append(((i,math.floor(number_pxl))))
        number_pxl = 0
    return hx

def count_pixel_y_matrice(port_matrice):
    number_pxl = 0
    hy = []
    (width,height) = tools.getWH(port_matrice)
    for i in range(width): #width, height
        for j in range(height):
            if port_matrice[j][i] == 0:
                number_pxl = number_pxl + 1
            elif port_matrice[j][i] < 254:
                number_pxl = (number_pxl + math.fabs(((port_matrice[j][i]/254)-1)))

        hy.append(((i,math.floor(number_pxl))))
        number_pxl = 0
    return hy

def count_pixel_y(self):
        number_pxl = 0
        for i in range (self.image.size[1]): #width, height
            for j in range (self.image.size[0]):
                (r,g,b) = self.image.getpixel((i,j))
                if r == 0:
                    number_pxl = number_pxl + 1
                elif r < 254:
                    number_pxl = (number_pxl + math.fabs(((r/254)-1)))
            if number_pxl != 0:
                self.liste_ypixel.append((i,math.floor(number_pxl)))
            number_pxl = 0


def totalScoring_matrice(hx,hy):
	scoreCurve = []
	for i in range(0,len(hx),10):
		scoreCurve = scoringPart_matrice(hx[i:i+10],scoreCurve)
	for i in range(0, len(hy), 10):
		scoreCurve = scoringPart_matrice(hy[i:i + 10],scoreCurve)
	return scoreCurve


def scoringPart_matrice(list, scoreCurve):
        score = 0
        for elt in range(len(list)-1):
            score += (list[elt][1]-list[elt+1][1])
        if scoreCurve == None:
        	scoreCurve = []
        scoreCurve.append(score)
        return scoreCurve

def found_letter(letter):
    results = dict()
    h_letter = Histogramev2.Histogramev2(letter)
    h_letter.count_pixel_x()
    h_letter.count_pixel_y()
    h_letter.totalScoring()


    d = os.listdir("static")
    for path, dirs, files in os.walk("static"):
        for filename in files:
            cur_dir = os.path.basename(path)
            if filename != "." and filename != ".." and filename != ".DS_Store":
                filename_path = cur_dir +"/" + filename
                h_static = Histogramev2.Histogramev2(filename_path)
                h_static.count_pixel_x()
                h_static.count_pixel_y()
                h_static.totalScoring()
                results[filename[0:len(filename)-4]] = h_static.compareScoring(h_letter.scoreCurve)
    print(results)
    #print(results.values())

def found_letter_matrice(port_matrice, proportion):
    results = dict()
    scoreCurve = []
    hx = count_pixel_x_matrice(port_matrice)
    hy = count_pixel_y_matrice(port_matrice)
    scoreCurve = totalScoring_matrice(hx,hy)
    if model_static != []:
	    for model in model_static:
	    	results[model.imageNom] = model.compareScoring(scoreCurve, proportion)
    #res = str([k for k,v in results.items() if min(results.values()) == v])
    res = tools.n_min(results,4,[])
    return res

def load_static_model(profil = ''):
    for path, dirs, files in os.walk("static"):
        for filename in files:
            cur_dir = os.path.basename(path)
            if cur_dir == 'default':
                if filename != "." and filename != ".." and filename != ".DS_Store":
                    filename_path = cur_dir +"/" + filename
                    h_static = Histogram(str(filename))
                    h_static.totalScoring()
                    model_static.append(h_static)
    #print("Modèles statiques chargés.")


