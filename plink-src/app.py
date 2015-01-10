"""
Here is what I know about py2app so far.  

First, I started with PLink because it's simpler.  After
easy_installing py2app, I created the plink-app directory contain a
three line file "PLink.py" which imports plink and invokes the editor.
The quickest thing to do is then just type

py2applet PLink.py

which builds PLink.app which is truly stand-alone, containing a copy
of Python and Tk.  If you don't want to do this, just specify the flag
"--semi-standalone".

Or one can go the setup.py route with 

py2applet --make-setup PLink.py

and then 

python setup.py py2app

builds dist/PLink.app.  

Of course, one can also add an icon, and I did that too, with a final py2applet command of:

py2applet --make-setup --semi-standalone --iconfile=plink.icns PLink.py

One annoyance is that py2app adds a "console window".  I suppressed
this by adding a forth line to PLink.py

MC 2009-05-6 This is now handled by plink.  Fourth line commented out.
"""


from . import LinkEditor
import sys

def main():
    if len(sys.argv) > 1:
        for file_name in sys.argv[1:]:
            LE = LinkEditor(file_name=file_name)
    else:
        LE = LinkEditor()
    LE.window.mainloop()

if __name__ == "__main__":
    main()

