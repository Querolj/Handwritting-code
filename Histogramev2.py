import math
from PIL import Image as pl
from PIL import ImageDraw as id

class Histogramev2:
    def __init__(self,image):
        self.imageNom = image
        self.image = pl.open(image)
        self.liste_xpixel, self.liste_ypixel = [],[]
        self.scoreCurve = []

        # Pour la fonction principal
        self.changementBool = False
        self.pointsList = []
        self.lastDirection = 'u'
        self.i = 1
        self.change = False
        self.oldchangement = False

    def count_pixel_x(self):
        number_pxl = 0
        for i in range(self.image.size[0]): #width, height
            for j in range(self.image.size[1]):
                #print(str(self.image.size[0]) + " " + str(self.image.size[1]))
                (r,g,b) = self.image.getpixel((j,i))
                if r == 0:
                    number_pxl = number_pxl + 1
                elif r < 254:
                    number_pxl = (number_pxl + math.fabs(((r/254)-1)))
            self.liste_xpixel.append(((i,math.floor(number_pxl))))
            number_pxl = 0
            #print()

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

    def totalScoring(self):
        for i in range(0,len(self.liste_xpixel),10):
            #print(self.liste_xpixel[i:i+10])
            self.scoringPart(self.liste_xpixel[i:i+10])
        for i in range(0, len(self.liste_ypixel), 10):
            self.scoringPart(self.liste_ypixel[i:i + 10])

    def scoringPart(self,list):
        score = 0
        for elt in range(len(list)-1):
            score += (list[elt][1]-list[elt+1][1])
        self.scoreCurve.append(score)

    def compareScoring(self,listToCompare):
        score = 0
        print("___________________")
        print(len(listToCompare))
        for i in range(len(listToCompare)):
                score+=math.fabs(self.scoreCurve[i]-listToCompare[i])
        return score



    def up(self,p1,p2):

        return ((p2-p1) > 0) and ((p1-p2) <= 5)

    def down(self,p1,p2):
        return ((p2-p1) < 0) and ((p1-p2) > -5)

    def straight(self,p1,p2):
        return (p2-p1) < 2 and (p2-p1) > -2

    def changement(self,l,direction,rangecheck):
        if len(l) != 1:
            if rangecheck == 0:
                # print(direction+" "+str(l[0]))
                return True
            if direction == 'd':
                if self.down(l[0][1],l[1][1]):
                    return self.changement(l[1:],'d',rangecheck-1)
                else:
                    self.i = l[0][0]
                    return True
            elif direction == 'u':
                if self.up(l[0][1],l[1][1]):
                    return self.changement(l[1:],'u',rangecheck-1)
                else:
                    self.i = l[0][0]
                    return True
            elif direction == 's':
                if self.straight(l[0][1],l[1][1]):
                    return self.changement(l[1:],'s',(rangecheck-1))
                else:
                    self.i = l[0][0]
                    return True
            else:
                return False

    def setChangement(self,c):
        if self.lastDirection == c:
            self.changementBool = False
        else:
            self.changementBool = True

    def setChangementFilter(self,c):
        if self.change == c:
            self.oldchangement = False
        else:
            self.oldchangement = True


    def analyseHistogram(self):
        self.pointsList.append(self.liste_xpixel[0])
        l = self.liste_xpixel
        while(self.i != len(l)-1):
            if self.changementBool:
                if self.lastDirection == 's' and self.changement(l[self.i-1:],self.lastDirection,5):

                    self.setChangement(self.lastDirection)
                elif self.lastDirection == 'u' and self.changement(l[self.i-1:],self.lastDirection,5):
                    self.pointsList.append(l[self.i - 1])
                    self.setChangement(self.lastDirection)
                else:
                    #print("marquage du point: "+str(l[self.i-1]))
                    self.pointsList.append(l[self.i-1])
                    self.setChangement(self.lastDirection)
            elif self.up(l[self.i][1],l[self.i+1][1]):
                # print("up "+str(self.i))
                self.setChangement('u')
                self.lastDirection = 'u'

            elif self.down(l[self.i][1],l[self.i+1][1]):
                #print("down "+str(self.i))
                self.setChangement('d')
                self.lastDirection = 'd'

            elif self.straight(l[self.i][1],l[self.i+1][1]):
                #print("straight "+str(self.i))
                self.setChangement('s')
                self.lastDirection = 's'
            self.i = self.i+1
        self.pointsList.append(self.liste_xpixel[99])


    def betweenTwoPoints(self,p1,p2):
        b = (((p2[1]-p1[1]) <= 10) and ((p2[1]-p1[1]) >= -10)) #entre 3 et -3
        return b

    def filter(self):
        p = self.pointsList[0]
        tmpList = []
        length = len(self.pointsList)-1
        for i in range(length):
            if self.betweenTwoPoints(p,self.pointsList[i+1]):
                p = self.pointsList[i + 1]
                tmpList.append(i + 1)
            else:
                if i in tmpList:
                    tmpList.remove(i)
                else:
                    p = self.pointsList[i+1]
        index = 0
        for l in tmpList:
            self.pointsList.pop(l-index)
            index = index + 1

    def inverseY(self,y):
        return (self.image.size[1]-1)-y

    def make_graph_x(self):
        image_new = pl.new("RGB",self.image.size,"white")
        draw = id.Draw(image_new)
        line = 0
        '''
        for i in range(len(self.pointsList)):
            draw.line([(line, 0), (line, 100)], (0, 0, 0))
            line += 10
        '''
        for elt in self.pointsList:
            image_new.putpixel((elt[0],self.inverseY(elt[1])),150)
        image_new.save("GraphDroitePointsX-"+self.imageNom)

h = Histogramev2("3.png")
h.count_pixel_x()
h.analyseHistogram()
print(h.pointsList)
h.filter()
print(h.pointsList)
h.make_graph_x()