import os
import sys
import itertools
import glob

sys.path.append('.')

import sphc
import commonlib.helpers
import commonlib.readconf
import conf_default

commonlib.helpers.setdefaultencoding()

config = commonlib.readconf.parse_config()

def sitecust(s):
    return config.words.get(s, s)

commonlib.helpers.push_to_builtins('__', sitecust)

import fe
import fe.src.pages
import fe.src.pages as rootpages
import fe.src.pages.invoicing
import fe.src.pages.team
import fe.src.pages.member as memberpages
import fe.src.pages.bizplace as bizplacepages
import fe.src.pages.plan as planpages
import fe.src.pages.resource as resourcepages
import fe.src.pages.booking as bookingpages
import commonlib.shared.static as static
import fe.src.pages.taxes

option_no_themes = '--nothemes' in sys.argv

pathjoin = os.path.join

pubroot = 'pub'
buildroot = 'build'
contribroot = 'fe/contrib'
srcroot = 'fe/src'
contribs = ['js', 'css', 'images']
roles = ['admin', 'director', 'host', 'member', 'new']
themeroot = static.themeroot
themedirs = [os.path.basename(name) for name in glob.glob(themeroot + '/*') if os.path.isdir(name)]
themedirs.remove('base')
compass_bin = os.path.join(os.environ['HOME'], 'gems/bin/compass')
if not os.path.exists(compass_bin):
    try:
        compass_bin = (glob.glob('/var/lib/gems/*/gems/compass-*/bin/compass')[0])
    except:
        sys.exit('Error: compass executable not found')

def exec_cmd(cmd, fail_on_err=True):
    print("Executing :" + cmd)
    ret = os.system(cmd)
    if fail_on_err and not ret == 0:
        sys.exit("Command failed: %s" % cmd)
    return ret

def compile_scss(prjdir):
    opts = "-q -r susy -u susy --relative-assets --sass-dir scss --css-dir css" % locals()
    project_cmd = compass_bin + " create %(prjdir)s %(opts)s" % locals()
    exec_cmd(project_cmd)
    compile_cmd = compass_bin + " compile %(prjdir)s -e production --force " % locals()
    exec_cmd(compile_cmd)

themes = static.themes
theme_map = dict((theme['name'], theme) for theme in themes)
theme_codes = themedirs
languages = [dict(label=label, name=code) for label, code in [ ('English', 'en') ]]
lang_map = dict((lang['name'], lang) for lang in languages)
lang_codes = tuple(lang_map.keys())

class BuilderBase(object):
    def __init__(self, page, path):
        self.page = page
        self.path = path
    def gen_path_combinations(self):
        build_data = dict(role=roles, theme=theme_codes, lang=lang_codes)
        pathvars = [var[2:-2] for var in self.path.split(os.path.sep) if var.startswith('%')]
        combinations = itertools.product(*([{var: v} for v in build_data[var]] for var in pathvars))
        return combinations

    def build(self):
        """
        To be implemented by concrete class
        """

class PageBuilder(BuilderBase):
    def build(self):
        for path_data in self.gen_path_combinations():
            page_data = dict(d.items()[0] for d in path_data)
            path = pathjoin(pubroot, (self.path % page_data))
            print("Building page: %s" % path)
            page = self.page(page_data)
            page_data['rroot'] = os.path.sep.join('..' for p in self.path.split(os.path.sep))
            page.write(path, page_data)

class JSBuilder(BuilderBase):
    """
    """

prefix = '%(lang)s/%(role)s/%(theme)s/'
host_prefix = '%(lang)s/%(role)s/%(theme)s/'

pages = [PageBuilder(rootpages.InvoicingPage, prefix + 'invoices/home'),
         PageBuilder(memberpages.MemberCreate, prefix + 'member/new'),
         PageBuilder(memberpages.ListMember, prefix + 'member/list'),
         PageBuilder(rootpages.Login, 'login'),
         PageBuilder(rootpages.Activation, 'activate'),
         PageBuilder(bizplacepages.Create, prefix + 'bizplace/new'),
         PageBuilder(bizplacepages.List, prefix + 'bizplaces'),
         PageBuilder(planpages.CreateTariff, prefix + 'tariff/new'),
         PageBuilder(planpages.ListTariff, prefix + 'tariffs'),
         PageBuilder(resourcepages.ResourceCreate, prefix + 'resource/new'),
         PageBuilder(resourcepages.ResourceManage, prefix + 'resources'),
         PageBuilder(rootpages.Dashboard, prefix + 'dashboard'),
         PageBuilder(memberpages.EditProfile, prefix + 'member/edit'),
         PageBuilder(fe.src.pages.invoicing.New, prefix + 'invoices/new'),
         PageBuilder(rootpages.LogoutPage, 'logout'),
         PageBuilder(fe.src.pages.invoicing.Preferences, prefix + 'invoices/preferences'),
         PageBuilder(fe.src.pages.invoicing.History, prefix + 'invoices/history'),
         PageBuilder(fe.src.pages.invoicing.Uninvoiced, prefix + 'invoices/uninvoiced'),
         PageBuilder(bookingpages.Booking, prefix + '/booking/new'),
         PageBuilder(bookingpages.WeekAgenda, prefix + '/booking/week'),
         PageBuilder(fe.src.pages.team.List, prefix + 'team'),
         PageBuilder(fe.src.pages.taxes.Taxes, prefix + 'taxes')
        ]

def copydirs(srcs, dst, verbose=False, overwrite=True):
    src = srcs
    if isinstance(srcs, basestring):
        srcs = [srcs]
    else:
        srcs = list(srcs)
    if not srcs:
        raise Exception("No source specified")
    print "%s -> %s" % (srcs, dst)
    v = verbose and 'v' or ''
    dstdir = os.path.dirname(dst)
    if dstdir and not os.path.exists(dstdir):
        os.makedirs(dstdir)
    if overwrite:
        srcs = ' '.join(srcs)
        cmd = "/usr/bin/rsync -r %s --exclude='.git'  %s %s" % (v, srcs, dst)
        exec_cmd(cmd)
    else:
        for root, dirs, files in os.walk(src):
            folder_path = os.path.join(dst, os.path.relpath(root, src))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            for each_file in files:
                dst_file = os.path.join(folder_path, each_file)
                src_file = os.path.join(root, each_file)
                if not os.path.isfile(dst_file) or os.stat(src_file).st_mtime > os.stat(dst_file).st_mtime:
                    cmd = "/bin/cp --remove-destination %s %s" % (src_file, dst_file)
                    exec_cmd(cmd)

def copy_contribs():
    contribdirs = (pathjoin(contribroot, name) for name in contribs)
    copydirs(contribdirs, pubroot)

def build_themes():
    """
    theme dir (built) goes to <pub>/themes/<theme-name>
    """
    copydirs(themeroot, pubroot, overwrite=False)
    base_themedir = pathjoin(themeroot, 'base')
    src_scssdir = pathjoin(base_themedir, 'scss')
    dst_scssdir = pathjoin(pubroot, 'themes/base/scss')
    change_in_base = False
    for each_file in os.listdir(src_scssdir):
        if each_file.endswith(".scss") and (not os.path.isfile(pathjoin(dst_scssdir, each_file)) or os.stat(pathjoin(src_scssdir, each_file)).st_mtime > os.stat(pathjoin(dst_scssdir, each_file)).st_mtime):
            change_in_base = True
            break

    for themedir in themedirs:
        # cp -r fe/src/themes pub
        # cp -r contrib/css/* pub/themes/default/scss/
        # cp -r themes/base/scss pub/themes/default/scss/base
        # cp pub/themes/default/scss/base/main.scss pub/themes/default/scss/
        # compass create . --sass-dir themes/default/scss --css-dir themes/default/css
        # rm pub/themes/default/scss
        src_themedir = pathjoin(themeroot, themedir)
        dst_themedir = pathjoin(pubroot, 'themes', themedir)
        # 1. copy images
        base_imagedir = pathjoin(base_themedir, 'images')
        src_imagedir = pathjoin(src_themedir, 'images')
        dst_imagedir = pathjoin(dst_themedir, 'images')
        copydirs(base_imagedir, dst_imagedir)
        if os.path.exists(src_imagedir) and os.listdir(src_imagedir):
            copydirs(src_imagedir + '/*', dst_imagedir)
        # 2. compile style
        src_scssdir = pathjoin(src_themedir, 'css')
        dst_scssdir = pathjoin(dst_themedir, 'scss')
        dst_cssdir = pathjoin(dst_themedir, 'css')
        change_in_theme = False
        for each_file in os.listdir(pathjoin(src_themedir, 'scss')):
            if not os.path.isfile(pathjoin(dst_scssdir, each_file)) or os.stat(pathjoin(src_themedir, 'scss', each_file)).st_mtime > os.stat(pathjoin(dst_scssdir, each_file)).st_mtime:
                change_in_theme = True
                break
        if change_in_base or change_in_theme:
            copydirs(themeroot, pubroot)
            copydirs(pathjoin(contribroot, 'css/'), pathjoin(dst_scssdir, 'contrib'))
            copydirs(pathjoin(base_themedir, 'scss/'), pathjoin(dst_scssdir, 'base'))
            copydirs(pathjoin(dst_scssdir, 'base', 'main.scss'), dst_scssdir)
            compile_scss(dst_themedir)
        # 3. copy jquery-ui images
        src_jqui_imagedir = pathjoin(contribroot, 'js', 'jquery-ui', 'images')
        copydirs(src_jqui_imagedir, dst_cssdir)

def build_scripts():
    """
    source scripts would need to know context (lang, theme, role) hence goes to go to /<theme>/<lang>/<role>/<path>
    """
    scripts = pathjoin(srcroot, 'js', '*')
    copydirs(scripts, pathjoin(pubroot, 'js'))

def copy_favicon():
    src = pathjoin(srcroot, 'favicon.ico')
    cmd = '/bin/cp %s %s' % (src, pubroot)
    exec_cmd(cmd)

def build_be_template_styles():
    base_dir = 'be/templates'
    src_dir = pathjoin(base_dir, 'scss')
    dst_dir = pathjoin(base_dir, 'css')
    changes_in_template = False
    for each_file in os.listdir(src_dir):
        if not os.path.isdir(dst_dir):
            changes_in_template = True
            break
        elif each_file.startswith('_'):
            continue
        elif not os.path.isfile(pathjoin(dst_dir, each_file.split('.')[0]+'.css')) or os.stat(pathjoin(src_dir, each_file)).st_mtime > os.stat(pathjoin(dst_dir, each_file.split('.')[0]+'.css')).st_mtime:
            changes_in_template = True
            break
    if changes_in_template:
        cmd = "/bin/rm -rf %s" % (dst_dir)
        exec_cmd(cmd)
        compile_scss(base_dir)

def build_all():
    for page in pages:
        page.build()

def build_help(help_format='html'):
    ''' Builds the help files in /help substituting the params from site config. '''
    base_dir = 'help/'
    cmd = "make -C %s %s" % (base_dir, help_format)
    exec_cmd(cmd)

def main():
    if not os.path.exists(pubroot):
        os.makedirs(pubroot)
    copy_contribs()
    copy_favicon()
    build_be_template_styles()
    if not option_no_themes: build_themes()
    build_scripts()
    build_all()
    build_help()
if __name__ == '__main__':
    main()
