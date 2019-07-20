import plink
import subprocess

link_dir = '../sample_links/'

LE = plink.LinkEditor(file_name=link_dir+'test.lnk')
LE.style_var.set('smooth')
LE.set_style()
LE.smoother.save_as_eps('test.eps')
LE.smoother.save_as_pdf('test.pdf')
LE.smoother.save_as_svg('test.svg')
LE.smoother.save_as_tikz('test_default.tikz')


LE = plink.LinkEditor(file_name=link_dir+'test.lnk')
LE.style_var.set('smooth')
LE.arrow_params['abs_gap_size'] = 15
LE.arrow_params['rel_gap_size'] = 0.5
LE.set_style()
LE.smoother.save_as_tikz('test_big_gaps.tikz')

subprocess.check_call(['latexmk', '-pvc-', 'main.tex'])

LE = plink.LinkEditor(file_name=link_dir+'bends.lnk')
LE.style_var.set('smooth')
LE.set_style()
LE.smoother.save_as_pdf('bends.pdf')

LE = plink.LinkEditor(file_name=link_dir+'tri.lnk')
LE.style_var.set('smooth')
LE.set_style()
LE.smoother.save_as_pdf('tri.pdf')


