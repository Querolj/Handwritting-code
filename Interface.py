from PIL import Image, ImageTk as pillow
from tkinter.filedialog import *

class App:
    def __init__(self):
        self.filename = ""
        self.canvas = None
        self.window = None
        self.openfile = None
        self.labelCanvas = None
        self.image = None
        self.textPathImage = None


    def openFile(self):
        self.openfile =  askopenfilename(title = "Selectionner une image",filetypes=(("Image files", "*.png"),("All Files","*.*")))
        if self.openfile != None:
            self.image = pillow.PhotoImage(pillow.Image.open(self.openfile))
            self.labelCanvas = Label(self.canvas,image=self.image)
            self.labelCanvas.pack()
            self.textPathImage = Label(self.canvas,text=self.openfile)
            self.textPathImage.pack(side=BOTTOM)

    def run(self):
        self.window = Tk()

        self.canvas = Canvas(self.window, width=500, height=500, background='white')
        self.canvas.pack(side=LEFT)

        self.menuBar = Menu(self.window)
        self.window.config(menu=self.menuBar)

        self.menuFichier = Menu(self.menuBar, tearoff=0)

        self.menuBar.add_cascade(label="Fichier", menu=self.menuFichier)

        self.menuFichier.add_command(label="Ouvrir", command=lambda: self.openFile())
        self.menuFichier.add_separator()
        self.menuFichier.add_command(label="Quitter", command=self.window.quit)

        self.window.mainloop()


fenetre = App()
fenetre.run()
