"""
Differs from plink/app.py because py2app can't handle
the relative import statement.
"""

from plink import LinkEditor

def main():
    LE = LinkEditor()
    LE.window.mainloop()

if __name__ == "__main__":
    main()

