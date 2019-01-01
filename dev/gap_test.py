import sys
import plink
import tkinter

class LinkEditor(plink.LinkEditor):
    def __init__(self, **kwargs):
        plink.LinkEditor.__init__(self, **kwargs)
        self.abs_gap_scale = abs_scale = tkinter.Scale(self.window,
                                                       length=400,
                                                       orient=tkinter.HORIZONTAL,
                                                       resolution=0.5,
                                                       tickinterval=2,
                                                       from_=0, to=20,
                                                       command=self.update_gaps)
        abs_scale.set(9)
        abs_scale.pack()
        
        self.rel_gap_scale = rel_scale = tkinter.Scale(self.window,
                                                       length=400,
                                                       orient=tkinter.HORIZONTAL,
                                                       resolution=0.01,
                                                       tickinterval=0.1,
                                                       from_=0, to=1.0,
                                                       command=self.update_gaps)
        rel_scale.set(0.2)
        rel_scale.pack()

        self.no_arrow_scale = rel_scale = tkinter.Scale(self.window,
                                                       length=400,
                                                       orient=tkinter.HORIZONTAL,
                                                       resolution=0.5,
                                                       tickinterval=5,
                                                       from_=0, to=30,
                                                       command=self.update_gaps)
        rel_scale.set(0)
        rel_scale.pack()

        rel_scale.bind("<ButtonRelease-1>", self.update_gaps)

    def update_gaps(self, event):
        params = self.arrow_params
        params['abs_gap_size'] = float(self.abs_gap_scale.get())
        params['rel_gap_size'] = float(self.rel_gap_scale.get())
        params['no_arrow_size'] = float(self.no_arrow_scale.get())
        self.update_crosspoints()
        self.set_style()
        

        
        
def main():
    if len(sys.argv) > 1:
        for file_name in sys.argv[1:]:
            LE = LinkEditor(file_name=file_name)
    else:
        LE = LinkEditor()
    LE.window.mainloop()

if __name__ == "__main__":
    main()
