import os
import sublime
import sublime_plugin
import glob

from ..lib import helpers
from ..lib import omnisharp

class OmniSharpNewFile(sublime_plugin.TextCommand):
    
    PACKAGE_NAME = 'omnisharpsublime'
    TMLP_DIR = 'templates'

    def run(self, edit, tmpltype='class', paths=[]):
        print(paths)
        if (len(paths) == 0):
            if sublime.active_window().active_view().file_name() is not None:
                print(sublime.active_window().active_view().file_name())
                paths = [sublime.active_window().active_view().file_name()]
            else:
                paths = [sublime.active_window().folders()[0]]

        incomingpath = paths[0]
        if not os.path.isdir(incomingpath):
            incomingpath = os.path.dirname(incomingpath)
        print(incomingpath)

        self.incomingpath = incomingpath
        self.tmpltype = tmpltype
        self.view.window().show_input_panel("New File:", incomingpath + "/new" + tmpltype + ".cs", self._on_done, None, None)

      

    def _on_done(self,filename):
        well = self.solution_folder(self.incomingpath)
        originalfilename = filename
        print(well)

        indexpos = self.incomingpath.index(well)

        namespace = self.incomingpath[indexpos:]
        namespace = namespace.replace("/",".")
        print(namespace)

        filename =  os.path.basename(filename)
        filename = os.path.splitext(filename)[0]
        print('noext')
        print(filename)
        tmpl = self.get_code(self.tmpltype, namespace, filename)
        # self.tab = self.creat_tab(self.view)

        # self.set_syntax()
        # self.set_code(tmpl)
        
        with open(originalfilename, 'w') as f:
            f.write(tmpl)

        sublime.active_window().open_file(originalfilename)

    def solution_folder(self, start_path):
        last_root    = start_path
        current_root = start_path
        found_path   = None
        while found_path is None and current_root:
            pruned = False
            for root, dirs, files in os.walk(current_root):
                if not pruned:
                   try:
                      # Remove the part of the tree we already searched
                      del dirs[dirs.index(os.path.basename(last_root))]
                      pruned = True
                   except ValueError:
                      pass
                results = glob.glob(current_root + "/*.sln")
                if(len(results) > 0):
                   # if searching_for in files:
                   # found the file, stop
                   # found_path = os.path.join(root, searching_for)
                   # break
                   return os.path.basename(root)
            # Otherwise, pop up a level, search again
            last_root    = current_root
            current_root = os.path.dirname(last_root)


    def get_code(self, type, namespace, filename):
        code = ''
        file_name = "%s.tmpl" % type
        isIOError = False

        tmpl_dir = 'Packages/' + self.PACKAGE_NAME + '/' + self.TMLP_DIR + '/'
        user_tmpl_dir = 'Packages/User/' + \
            self.PACKAGE_NAME + '/' + self.TMLP_DIR + '/'


        self.user_tmpl_path = os.path.join(user_tmpl_dir, file_name)
        self.tmpl_path = os.path.join(tmpl_dir, file_name)

        try:
            code = sublime.load_resource(self.user_tmpl_path)
        except IOError:
            try:
                code = sublime.load_resource(self.tmpl_path)
            except IOError:
                isIOError = True

        if isIOError:
            sublime.message_dialog('[Warning] No such file: ' + self.tmpl_path
                                   + ' or ' + self.user_tmpl_path)

        code = code.replace('${namespace}', namespace)
        code = code.replace('${classname}', filename)

        return code

    def creat_tab(self, view):
        win = view.window()
        tab = win.new_file()
        return tab

    def set_code(self, code):
        tab = self.tab
        tab.run_command('insert_snippet', {'contents': code})

    def set_syntax(self):
        v = self.tab

        v.set_syntax_file('Packages/C#/C#.tmLanguage')
