from tkinter import *
from tkinter import colorchooser

x, y = 0, 0  # coordinates
color = 'black'
bgColor = 'white'


def draw(event):
  x, y = event.x, event.y
  x1, y1 = (x - 1), (y - 1)
  x2, y2 = (x + 1), (y + 1)
  canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color,
                          width=getScaleValue())


def eraseLine():
  global color
  color = "white"


def getColor():
  global color
  hex = colorchooser.askcolor(title="Edit colors")
  color = hex[1]  # hexadecimal
  return color


def showColor(newColor):
  global color
  color = newColor


def getScaleValue():
  brushSize = str(var.get())
  return brushSize


def deleteCanvas(event):
  canvas.delete('all')
  showPalette()


def createCanvas():
  canvas.delete('all')
  showPalette()


window = Tk()

window.title('Sketch')

window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

menubar = Menu(window)
window.config(menu=menubar)
submenu = Menu(menubar, tearoff=0)

menubar.add_cascade(label='File', menu=submenu)
submenu.add_command(label='New Canvas', command=createCanvas)

canvas = Canvas(window, background=bgColor, width=700, height=600)
canvas.grid(row=0, column=0, sticky='nsew')

var = IntVar()
scale = Scale(window, from_=0, to=50, orient=HORIZONTAL, variable=var)
scale.place(x=10, y=320)
scale.set(10)

paletteButton = Button(window, text="Edit colors", command=getColor)
paletteButton.place(x=10, y=380)

sendButton = Button(window, text="Send image")
sendButton.place(x=620, y=10)

canvas.bind('<B1-Motion>', draw)
canvas.bind('<B3-Motion>', deleteCanvas)

photoEraser = PhotoImage(file=r"eraser.png")
eraserImage = photoEraser.subsample(7, 7)
eraser = Button(window, image=eraserImage, command=eraseLine)
eraser.place(x=10, y=420)

photoBucket = PhotoImage(file=r"bucket.png")
bucketImage = photoBucket.subsample(30, 30)
fill = Button(window, image=bucketImage,
              command=lambda: canvas.configure(bg=color))
fill.place(x=10, y=470)


def showPalette():
  blackRectangle = canvas.create_rectangle((10, 10, 30, 30), fill='black')
  canvas.tag_bind(blackRectangle, '<Button-1>', lambda x: showColor('black'))

  grayRectangle = canvas.create_rectangle((10, 40, 30, 60), fill='gray')
  canvas.tag_bind(grayRectangle, '<Button-1>', lambda x: showColor('gray'))

  brownRectangle = canvas.create_rectangle((10, 70, 30, 90), fill='brown4')
  canvas.tag_bind(brownRectangle, '<Button-1>', lambda x: showColor('brown4'))

  redRectangle = canvas.create_rectangle((10, 100, 30, 120), fill='red')
  canvas.tag_bind(redRectangle, '<Button-1>', lambda x: showColor('red'))

  orangeRectangle = canvas.create_recButtangle((10, 130, 30, 150),
                                               fill='orange')
  canvas.tag_bind(orangeRectangle, '<ton-1>', lambda x: showColor('orange'))

  yellowRectangle = canvas.create_rectangle((10, 160, 30, 180), fill='yellow')
  canvas.tag_bind(yellowRectangle, '<Button-1>', lambda x: showColor('yellow'))

  greenRectangle = canvas.create_rectangle((10, 190, 30, 210), fill='green')
  canvas.tag_bind(greenRectangle, '<Button-1>', lambda x: showColor('green'))

  blueRectangle = canvas.create_rectangle((10, 220, 30, 240), fill='blue')
  canvas.tag_bind(blueRectangle, '<Button-1>', lambda x: showColor('blue'))

  purpleRectangle = canvas.create_rectangle((10, 250, 30, 270), fill='purple')
  canvas.tag_bind(purpleRectangle, '<Button-1>', lambda x: showColor('purple'))

  whiteRectangle = canvas.create_rectangle((10, 280, 30, 300), fill='white')
  canvas.tag_bind(whiteRectangle, '<Button-1>', lambda x: showColor('white'))


showPalette()

window.mainloop()
