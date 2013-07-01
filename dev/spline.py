from Tkinter import *
W = Tk()
C = Canvas(W, width=500, height=500, background='white')
C.pack()
PCCP = (100,350,200,200,300,400,400,350,)
PCCP2 = (100,200,200,50,300,50,400,200,)
C.create_line(*PCCP, width=1, fill='black')
C.create_line(*PCCP, smooth='raw', width=6, fill='#ffb0b0', splinesteps=100)
C.create_line(*PCCP, smooth='raw', width=5, fill='#ff6060', splinesteps=100)
C.create_line(*PCCP, smooth='raw', width=4, fill='#ff0000', splinesteps=100)
C.create_line(*PCCP2, width=1, fill='black')
C.create_line(*PCCP2, smooth='raw', width=6, fill='#ffb0b0', splinesteps=100)
C.create_line(*PCCP2, smooth='raw', width=5, fill='#ff6060', splinesteps=100)
C.create_line(*PCCP2, smooth='raw', width=4, fill='#ff0000', splinesteps=100)


#C.create_line(*PCCP, smooth=True, width=5, fill='blue', splinesteps=60)
W.mainloop()
