from tkinter import *
from tkinter import ttk


def callback(event):
    print(tree.item(tree.selection()))


root = Tk()

tree= ttk.Treeview(root)
tree.grid(row=4)
tree.insert('', 'end', 'parent', text='parent')
tree.insert('parent','end', 'child', text='child')


root.mainloop()

try:
    root.mainloop()
    root.destroy()
    root.close()
    exit()
except:
    pass