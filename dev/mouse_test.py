import Tkinter

def mouse_moved(event):
    print 'Motion', event.x, event.y

def mouse_left(event):
    print 'Leave', event.x, event.y

def mouse_entered(event):
    print 'Enter', event.x, event.y

window = Tkinter.Tk()
canvas = Tkinter.Canvas(window, width=500, height=500)
canvas.pack()
canvas.bind('<Motion>', mouse_moved)
canvas.bind('<Leave>', mouse_left)
canvas.bind('<Enter>', mouse_entered)

window.mainloop()


    
