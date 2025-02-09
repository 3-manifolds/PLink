import plink
import subprocess

link_dir = '../sample_links/'

# Scale factor is usually 1 except on high-res linux.

def save_each_filetype(link_editor, base_name):
    LE = link_editor
    LE.save_as_eps(base_name + '.eps')
    subprocess.check_call(['epstopdf', base_name + '.eps', base_name + '_from_eps.pdf'])
    LE.save_as_pdf(base_name + '.pdf')
    LE.save_as_svg(base_name + '.svg')
    LE.save_as_tikz(base_name + '.tikz')

                       
def save_many(link_name, window_width, scale_factor=1, outdir='output'):
    plink.scaling.set_scale_factor(scale_factor)
    LE = plink.LinkEditor()
    LE.window.geometry(f'{window_width}x{window_width}')
    LE.load(link_dir + link_name + '.lnk')

    base_name = outdir + f'/{link_name}_PL_{window_width}_{scale_factor}'
    save_each_filetype(LE, base_name)
    LE.style_var.set('smooth')
    LE.set_style()
    base_name = outdir + f'/{link_name}_smooth_{window_width}_{scale_factor}'
    save_each_filetype(LE.smoother, base_name)


def main_test():
    save_many('fourteen', 500, 1, 'output')
    save_many('fourteen', 1000, 2, 'output')
    



