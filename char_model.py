from PIL.Image import *
# Lié à la vielle base de donnée, ne sert plus

class Char_model:
    def __init__(self, model_name, model_path = "", sample_len = 0):
        self.model_name = model_name  # ex : 'a', 'A', '3'
        self.matrice = [[255 for j in range(100)] for i in range(100)]  # matrice.append pour ajouter une ligne de pixel
        self.sample_len = sample_len
        self.model_path = model_path

    
    def get_new_size(open_image):
        haut, bas, gauche, droite = Char_model.premier_pixel_haut(open_image), Char_model.premier_pixel_bas(open_image), Char_model.premier_pixel_gauche(open_image), Char_model.premier_pixel_droite(open_image)
        return (bas[0] - haut[0], droite[0] - gauche[0])

    def add_sample(self, sample_path, model_path, priority=1):
        sample = open(sample_path)
        self.sample_len = self.sample_len + 1  # On ajoute le sample et on modifie le %
        self.model_path = model_path
        for x in range(100):
            for y in range(100):
                (r, g, b) = sample.getpixel((y, x))
                sum = (self.matrice[x][y] / 100) * (self.sample_len - 1)
                if r == 0:
                    self.matrice[x][y] = (sum / self.sample_len) * 100
                else:
                    self.matrice[x][y] = ((sum + 1) / self.sample_len) * 100