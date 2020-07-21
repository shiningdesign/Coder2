'''
template version: utt.Class_1010_20200615
CodeView:
  * code view ui from xDever v7.3
  
v0.1: (2020.06.23)
  * base functions

'''
# ---- python 2,3 unicode ----
try:
    UNICODE_EXISTS = bool(type(unicode))
except NameError:
    unicode = lambda s: str(s)
# ---- qtMode ----
qtMode = 0 # 0: PySide; 1 : PyQt, 2: PySide2, 3: PyQt5
qtModeList = ('PySide', 'PyQt4', 'PySide2', 'PyQt5')
try:
    from PySide import QtGui, QtCore
    import PySide.QtGui as QtWidgets
    qtMode = 0
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        qtMode = 2
    except ImportError:
        try:
            from PyQt4 import QtGui,QtCore
            import PyQt4.QtGui as QtWidgets
            import sip
            qtMode = 1
        except ImportError:
            from PyQt5 import QtGui,QtCore,QtWidgets
            import sip
            qtMode = 3
print('Qt: {0}'.format(qtModeList[qtMode]))
# ---- base lib ----
import os,sys
# ---- user lib ----
from functools import partial # for partial function creation
import re, subprocess
try:
    import LNTextEdit
except ImportError:
    import Coder2_LNTextEdit as LNTextEdit

class CodeView(QtWidgets.QWidget):
    def __init__(self, parent=None,mode=0):
        QtWidgets.QWidget.__init__(self,parent)
        # memo
        self.parent=parent
        
        self.memoData={}
        self.memoData['last_import']=''
        self.memoData['last_export']=''
        self.memoData['last_browse']=''
        # UI
        self.memoData['config']={}
        self.memoData['config']['code_path']=''
        self.memoData['config']['appPath'] = {}
        self.memoData['config']['appPath']['npp'] = [r'D:\z_sys\App\npp\notepad++.exe',r'D:\App\npp\notepad++.exe']
        
        self.uiList={}
        self.uiList['main_layout']=QtWidgets.QVBoxLayout();
        self.uiList['main_layout'].setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.uiList['main_layout'])
        
        self.qui('main_label;Example | main_input', 'test_layout')
        self.qui_policy('main_input',5,3)
        
        # ======= code layout ======
        self.uiList['code_edit'] = LNTextEdit.LNTextEdit()
        self.qui('code_tree;(name) | code_edit','code_split;v')
        self.uiList['code_edit'].monoFont(1)
        self.qui(' code_tree_update_btn;Refresh List | code_tree_edit_btn;Edit | code_tree_removeSelf_btn;Remove "self" in Code', 'code_action_layout;hbox')
        self.qui('code_tree_search_input | code_split | code_action_layout','main_layout')
        # ======= code layout ENDS ======
        
        
        # hide ui
        
        # connect UI
        self.Establish_Connections()
    def Establish_Connections(self):
        for ui_name in self.uiList.keys():
            prefix = ui_name.rsplit('_', 1)[0]
            if ui_name.endswith('_btn'):
                if hasattr(self, prefix+"_action"):
                    self.uiList[ui_name].clicked.connect(getattr(self, prefix+"_action"))
        # drop support
        self.uiList['main_input'].installEventFilter(self)
        
        self.uiList['code_tree_search_input'].textChanged.connect(partial(self.tree_task_search_action,'code_tree'))
        self.uiList['code_tree'].itemClicked[QtWidgets.QTreeWidgetItem,int].connect(self.code_tree_select_action)
    
    def eventFilter(self, object, event):
        # the main window event filter function
        if event.type() == QtCore.QEvent.DragEnter:
            data = event.mimeData()
            urls = data.urls()
            if object is self.uiList['main_input'] and (urls and urls[0].scheme() == 'file'):
                event.acceptProposedAction()
            return 1
        elif event.type() == QtCore.QEvent.Drop:
            data = event.mimeData()
            urls = data.urls()
            if object is self.uiList['main_input'] and (urls and urls[0].scheme() == 'file'):
                filePath = unicode(urls[0].path())[1:]
                self.uiList['main_input'].setText(os.path.normpath(filePath))
                
            return 1
        return 0
        
    # ---- user functions ----
    def ___code_functions___():
        pass
    def setCodePath(self, code_path):
        self.memoData['config']['code_path'] = code_path
        self.updateUI_code()
    def code_tree_update_action(self):
        # remember current tree node 
        cur_tree =self.uiList['code_tree']
        open=[]
        currentNode = cur_tree.currentItem()
        if currentNode:
            pathInfo = unicode(currentNode.text(1))
            open = pathInfo.split(':')
        
        # update
        self.updateUI_code()
    
        # re-open tree
        if len(open)>0:
            if isinstance(open[0], (str, unicode)):
                parentNode = cur_tree.invisibleRootItem()
                for seg in open:
                    index = [ unicode(parentNode.child(i).text(0)) for i in range(parentNode.childCount()) ].index(seg)
                    parentNode.child(index).setExpanded(1)
                    parentNode = parentNode.child(index)
    def code_tree_edit_action(self):
        config = self.memoData['config']
        # edit
        pyPath = config['code_path']
        app = self.getOptionPath(config['appPath'], 'npp')
        if os.path.isfile(app):
            subprocess.Popen([app, os.path.normpath(pyPath)])
                
    def code_tree_removeSelf_action(self):
        edit_ui = self.uiList['code_edit']
        cur_text = edit_ui.text()
        cur_text = cur_text.replace('self, ','').replace('self,', '')
        cur_text = cur_text.replace('self.', '')
        edit_ui.setText(cur_text)
    def updateUI_code(self):
        # load code tree
        config = self.memoData['config']
        cur_tree =self.uiList['code_tree']
        cur_tree.clear()
        if os.path.isfile(config['code_path']):
            code_raw = self.readTextFile(config['code_path'])
        else:
            return
        line_list = code_raw.splitlines()
        skip=0
        rootNode = cur_tree.invisibleRootItem()
        parentNode = rootNode
        
        codeNode = None
        code_text = []
        parentTag = []
        if config['code_path'].endswith('.py'):
            # python code
            for line in line_list:
                if line.startswith("'''"):
                    skip=1-skip # toggle skip
                else:
                    if skip == 1:
                        pass
                    else:
                        # process line
                        if line.startswith('###'):
                            name = line.replace('#','').strip()
                            new_item = QtWidgets.QTreeWidgetItem([name,name])
                            rootNode.addChild(new_item)
                            parentNode = new_item
                            parentTag = [name]
                        elif line.startswith('#~~'):
                            # close previous node
                            if codeNode is not None:
                                codeNode.setText(2, '\n'.join(code_text))
                                code_text = [] # reset
                            # prepare current note
                            name = line.replace('#','').replace('~','').strip()
                            codeNode = QtWidgets.QTreeWidgetItem([name, ':'.join(parentTag+[name])])
                            parentNode.addChild(codeNode)
                        else:
                            if codeNode is not None:
                                code_text.append(line)
        elif config['code_path'].endswith('.js'):
            # js code
            for line in line_list:
                if line.startswith("//'''"):
                    skip=1-skip # toggle skip
                else:
                    if skip == 1:
                        pass
                    else:
                        # process line
                        if line.startswith('//###'):
                            name = line.replace('//','').replace('#','').strip()
                            new_item = QtWidgets.QTreeWidgetItem([name,name])
                            rootNode.addChild(new_item)
                            parentNode = new_item
                            parentTag = [name]
                        elif line.startswith('//~~'):
                            # close previous node
                            if codeNode is not None:
                                codeNode.setText(2, '\n'.join(code_text))
                                code_text = [] # reset
                            # prepare current note
                            name = line.replace('//','').replace('~','').strip()
                            codeNode = QtWidgets.QTreeWidgetItem([name, ':'.join(parentTag+[name])])
                            parentNode.addChild(codeNode)
                        else:
                            if codeNode is not None:
                                code_text.append(line)

            
        # cache
        self.cacheTreeData('code_tree',force=1)
    def code_tree_select_action(self, item, col=0):
        self.uiList['code_edit'].setText(unicode(item.text(2)))
    
    
    #=======================================
    #  tree task functions
    #=======================================

    def ___tree_task_functions___():
        pass
    
    def tree_resize(self, tree_name, extra=10):
        cur_tree = self.uiList[tree_name]
        for i in range(cur_tree.columnCount()):
            cur_tree.resizeColumnToContents(i)
            w = cur_tree.columnWidth(i)
            cur_tree.setColumnWidth(i,w+extra)
    def tree_expand(self, node, level=0, expand=1):
        if isinstance(node, (str, unicode)):
            node = self.uiList[node].invisibleRootItem()
        # expand top node
        for i in range(node.childCount()):
            node.child(i).setExpanded(expand)
            # sub node
            if level == -1:
                self.tree_expand(node.child(i), level)
            elif level > 0:
                level -=1
                self.tree_expand(node.child(i), level)
                
    def tree_task_copyData_action(self, tree_name, item=None, col=0):
        cur_tree = self.uiList[tree_name]
        cur_node = cur_tree.currentItem()
        if cur_node:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(unicode(cur_node.text(2)))
    def tree_task_search_action(self, tree_name, word):
        cur_tree = self.uiList[tree_name]
        #word = unicode(self.uiList[tree_name+'_search_input'].text())
        cur_tree.clear()
        self.setTreeData(cur_tree, cur_tree.invisibleRootItem(), self.memoData['cache'][tree_name], filter=unicode(word))
    def clearSearch_action(self, input_name):
        if input_name == 'folder_tree_search_input':
            tab_index = self.uiList['main_tab'].currentIndex()
            if tab_index == 1:
                # code tree
                input_name = 'code_tree_search_input'
        self.uiList[input_name].setText('')
    #=======================================
    #  tree functions
    #=======================================
    def cacheTreeData(self, tree, force=1):
        cur_tree = self.uiList[tree]
        if 'cache' not in self.memoData:
            self.memoData['cache'] = {}
        if force == 1:
            self.memoData['cache'][tree] = self.getTreeData(cur_tree, cur_tree.invisibleRootItem())
        else:
            if tree not in self.memoData['cache']:
                self.memoData['cache'][tree] = self.getTreeData(cur_tree, cur_tree.invisibleRootItem())
    def getTreeData(self, tree, cur_node):
        child_count = cur_node.childCount()
        node_info = [ unicode( cur_node.text(i) ) for i in range(cur_node.columnCount()) ]
        node_info_child = []
        for i in range(child_count):
            node_info_child.append( self.getTreeData(tree, cur_node.child(i) ) )
        return (node_info, node_info_child)
    def setTreeData(self, tree, cur_node, data, filter='', col=0):
        # correct node format [ [info list], [ child list] ]
        node_info = []
        node_info_child = []
        
        # format [ [info list], [child list] ]
        # possible input
        # 1. data [ a, b, c, d, e]; ==> set cur_node row info
        # 2. data a; ==> set cur_node row info
        # 3. data [a, [child list]]; ==> set cur_node and add child list
        # 4. data [ [a], [child list]]; ==> set cur_node and add child list
        # 5. child list only [ a, [], b, [c]]
        # ------------ 
        # situation 2: a
        # print('---------------------')
        # print(data)
        # print('---------------------')
        if isinstance(data, (str,unicode)):
            node_info = [data]
        elif isinstance(data,(tuple,list)):
            is_info_only = True
            for x in data:
                if not isinstance(x, (str,unicode)):
                    is_info_only = False
            if is_info_only:
                # situation 1: [ a,b,c ]
                node_info = data
            else:
                # situation 3: 
                if len(data) == 2:
                    # check info
                    if isinstance(data[0], (str,unicode)):
                        data_info = [ data[0] ]
                    elif isinstance(data[0],(tuple,list)):
                        node_info = data[0]
                    else:
                        print('bad format node: {0}'.format(unicode(data)))
                        return
                    # check child
                    if isinstance(data[1],(tuple,list)):
                        node_info_child = data[1]
                    else:
                        print('bad format node: {0}'.format(unicode(data)))
                        return
                else:
                    node_info_child = data
        # ------------ 
        
        [cur_node.setText(i, unicode(node_info[i])) for i in range(len(node_info))]
        # re filter
        if filter != '' and isinstance(filter, (str, unicode)):
            filter = re.compile(filter, re.IGNORECASE)
        for sub_data in node_info_child:
            if filter == '':
                new_node = QtWidgets.QTreeWidgetItem()
                cur_node.addChild(new_node)
                self.setTreeData(tree, new_node, sub_data)
            else:
                if not filter.search(sub_data[0][col]) and not self.checkChildData(sub_data[1], filter, col):
                    pass
                else:
                    new_node = QtWidgets.QTreeWidgetItem()
                    cur_node.addChild(new_node)
                    new_node.setExpanded(1)
                    self.setTreeData(tree, new_node, sub_data, filter, col)
    def checkChildData(self, DataChild, filter, col):
        ok_cnt = 0
        if isinstance(filter, (str, unicode)):
            filter = re.compile(filter, re.IGNORECASE)
        for sub_data in DataChild:
            if filter.search(sub_data[0][col]) or self.checkChildData(sub_data[1], filter, col):
                ok_cnt +=1
        return ok_cnt
    #=======================================
    #  support functions
    #=======================================
    # ======= path functions =======
    def ____path_functions____():
        pass
        '''
        config['appPath']['djv'] = [r'C:\Program Files\djv-*-Windows-64\bin\djv_view.exe', r'R:\Pipeline\App\djv_win64\bin\djv_view.exe']
        # ('subFolder1', 'subFolder2', 'appName.ext')
        config['appPath']['ffmpeg'] = [ ('bin','ffmpeg.exe'), r'D:\z_sys\App\ffmpeg\ffmpeg.exe', r'R:\Pipeline\App_VHQ\ffmpeg\bin\ffmpeg.exe']
        config['appPath']['ffprobe'] = [  ('bin','ffprobe.exe'), r'D:\z_sys\App\ffmpeg\ffprobe.exe', r'R:\Pipeline\App_VHQ\ffmpeg\bin\ffprobe.exe']
        
        app = self.getOptionPath(config['appPath'], 'djv')
        nuke_app_list = self.getOptionPath(config['appPath'], 'nuke', all=1)
        if os.path.isfile(app):
           subprocess.Popen([app, os.path.normpath(pyPath)])
        if os.path.isfile(batch_appPath) and mod == 2:
           subprocess.Popen(batch_appPath,creationflags=subprocess.CREATE_NEW_CONSOLE)
        info=subprocess.Popen('tasklist.exe /FO CSV /FI "IMAGENAME eq {0}"'.format(appName),stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = info.communicate()
        result = [ x for x in out.replace('"','').splitlines() if x !='' ]
        '''

        
    def getOptionPath(self, dict, name, all=0):
        # updated: 2020.05.05 get self location sub path option
        # updated: 2019.01.09
        if name not in dict.keys():
            print('Dict has no key: {0}'.format(name))
            return
        option_list = []
        if not isinstance(dict[name], (list,tuple)):
            option_list = [ dict[name] ]
        else:
            option_list = dict[name]
        if all == 0:
            found = None
            for option in option_list:
                if isinstance(option,(tuple, list)):
                    # self path
                    self_option_info = [os.path.dirname(self.location)]+[x for x in option]
                    self_option = os.path.normpath( os.path.join(*self_option_info) )
                    if os.path.exists(self_option):
                        found = self_option
                        break
                else:
                    if '*' in option:
                        # wildchar search
                        import glob
                        sub_option_list = glob.glob(option)
                        if len(sub_option_list) > 0:
                            found = sorted(sub_option_list)[-1]
                            break
                    else:
                        if os.path.exists(option):
                            found = option
                            break
            if found is not None:
                found = found.replace('\\','/')
            print('found: {0}'.format(found))
            return found
        else:
            all_option = []
            for option in option_list:
                if '*' in option:
                    # wildchar search
                    import glob
                    sub_option_list = glob.glob(option)
                    all_option.extend(sorted(sub_option_list, reverse=1))
                else:
                    if os.path.exists(option):
                        all_option.append(option)
            standard_path_option = []
            for each_path in all_option:
                standard_path = each_path.replace('\\','/')
                if standard_path not in standard_path_option:
                    standard_path_option.append(standard_path)
            print(standard_path_option)
            return standard_path_option
    # getPathChild for non utt widget
    def getPathChild(self, scanPath, pattern='', isfile=0):
        resultList =[]
        scanPath = unicode(scanPath)
        if not os.path.isdir(scanPath):
            return resultList
        if isfile == 0:
            resultList = [x for x in os.listdir(scanPath) if os.path.isdir(os.path.join(scanPath,x))]
        elif isfile == 1:
            resultList = [x for x in os.listdir(scanPath) if os.path.isfile(os.path.join(scanPath,x))]
        else:
            resultList = os.listdir(scanPath)
        if pattern != '':
            cur_pattern = re.compile(pattern)
            resultList = [x for x in resultList if cur_pattern.match(x)]
        resultList.sort()
        return resultList
    def readTextFile(self, file):
        with open(file) as f:
            txt = f.read()
        return txt
    def writeTextFile(self, txt, file, b=0):
        b = '' if b==0 else 'b'
        with open(file, 'w'+b) as f:
            f.write(txt)
    # ---- core functions ----
    def ___core_functions___(self):
        pass
    def qui_menu(self, action_list_str, menu_str):
        # qui menu creation
        # syntax: self.qui_menu('right_menu_createFolder_atn;Create Folder,Ctrl+D | right_menu_openFolder_atn;Open Folder', 'right_menu')
        if menu_str not in self.uiList.keys():
            self.uiList[menu_str] = QtWidgets.QMenu()
        create_opt_list = [ x.strip() for x in action_list_str.split('|') ]
        for each_creation in create_opt_list:
            ui_info = [ x.strip() for x in each_creation.split(';') ]
            atn_name = ui_info[0]
            atn_title = ''
            atn_hotkey = ''
            if len(ui_info) > 1:
                options = ui_info[1].split(',')
                atn_title = '' if len(options) < 1 else options[0]
                atn_hotkey = '' if len(options) < 2 else options[1]
            if atn_name != '':
                if atn_name == '_':
                    self.uiList[menu_str].addSeparator()
                else:
                    if atn_name not in self.uiList.keys():
                        self.uiList[atn_name] = QtWidgets.QAction(atn_title, self)
                        if atn_hotkey != '':
                            self.uiList[atn_name].setShortcut(QtGui.QKeySequence(atn_hotkey))
                    self.uiList[menu_str].addAction(self.uiList[atn_name])
    def default_menu_call(self, ui_name, point):
        if ui_name in self.uiList.keys() and ui_name+'_menu' in self.uiList.keys():
            self.uiList[ui_name+'_menu'].exec_(self.uiList[ui_name].mapToGlobal(point))
    def qui(self, ui_str, layout_str):
        ui_str_list = [x.strip() for x in ui_str.split('|') if x.strip()]
        ui_list = []
        for ui in ui_str_list:
            ui_option = ''
            if ';' in ui:
                ui,ui_option = ui.split(';',1)
            if ui not in self.uiList.keys():
                # creation process
                if ui.endswith('_choice'):
                    self.uiList[ui]= QtWidgets.QComboBox()
                elif ui.endswith('_input'):
                    self.uiList[ui]= QtWidgets.QLineEdit()
                elif ui.endswith('_txt'):
                    self.uiList[ui]= QtWidgets.QTextEdit()
                elif ui.endswith('_label'):
                    self.uiList[ui]= QtWidgets.QLabel(ui_option)
                elif ui.endswith('_btn'):
                    self.uiList[ui]= QtWidgets.QPushButton(ui_option)
                elif ui.endswith('_check'):
                    self.uiList[ui]= QtWidgets.QCheckBox(ui_option)
                elif ui.endswith('_spin'):
                    self.uiList[ui]= QtWidgets.QSpinBox()
                    if len(ui_option)>0:
                        int_list = ui_option.replace('(','').replace(')','').split(',')
                        self.uiList[ui].setMaximum(10000) # override default 99
                        if len(int_list)>0 and int_list[0].isdigit():
                            self.uiList[ui].setValue(int(int_list[0]))
                        if len(int_list)>1 and int_list[1].isdigit():
                            self.uiList[ui].setMinimum(int(int_list[1]))
                        if len(int_list)>2 and int_list[2].isdigit():
                            self.uiList[ui].setMaximum(int(int_list[2]))
                elif ui.endswith('_tree'):
                    self.uiList[ui] = QtWidgets.QTreeWidget()
                    if len(ui_option)>0:
                        label_list = ui_option.replace('(','').replace(')','').split(',')
                        self.uiList[ui].setHeaderLabels(label_list)
                elif ui.endswith('_space'):
                    self.uiList[ui] = QtWidgets.QSpacerItem(5,5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred )
                else:
                    # creation fail
                    continue
            # collect existing ui and created ui
            ui_list.append(ui)
        layout_option = ''
        if ';' in layout_str:
            layout_str, layout_option = layout_str.split(';',1)
        if layout_str not in self.uiList.keys():
            # try create layout
            if layout_str.endswith('_grp'):
                # grp option
                grp_option = layout_option.split(';',1)
                grp_title = layout_str
                if len(grp_option)>0:
                    if grp_option[0]=='vbox':
                        self.uiList[layout_str+'_layout'] = QtWidgets.QVBoxLayout()
                    elif grp_option[0]=='hbox':
                        self.uiList[layout_str+'_layout'] = QtWidgets.QHBoxLayout()
                if len(grp_option) == 2:
                    grp_title = grp_option[1]
                self.uiList[layout_str] = QtWidgets.QGroupBox(grp_title)
                self.uiList[layout_str].setLayout(self.uiList[layout_str+'_layout'])
                # pass grp layout
                layout_str = layout_str+'_layout'
            elif layout_str.endswith('_split'):
                split_type = QtCore.Qt.Horizontal
                if 'v' in layout_option:
                    split_type = QtCore.Qt.Vertical
                self.uiList[layout_str]=QtWidgets.QSplitter(split_type)
            else:
                if layout_option == 'vbox':
                    self.uiList[layout_str] = QtWidgets.QVBoxLayout()
                elif layout_option == 'hbox':
                    self.uiList[layout_str] = QtWidgets.QHBoxLayout()
                else:
                    return
        cur_layout = self.uiList[layout_str]
        if isinstance(cur_layout, QtWidgets.QBoxLayout):
            # box
            for ui in ui_list:
                ui_option = ''
                if ';' in ui:
                    ui,ui_option = ui.split(';',1)
                if isinstance(self.uiList[ui], QtWidgets.QWidget):
                    cur_layout.addWidget(self.uiList[ui])
                elif isinstance(self.uiList[ui], QtWidgets.QSpacerItem):
                    cur_layout.addItem(self.uiList[ui])
                elif isinstance(self.uiList[ui], QtWidgets.QLayout):
                    cur_layout.addLayout(self.uiList[ui])
        elif isinstance(cur_layout, QtWidgets.QSplitter):
            # split
            for ui in ui_list:
                if isinstance(self.uiList[ui], QtWidgets.QWidget):
                    cur_layout.addWidget(self.uiList[ui])
                else:
                    tmp_holder = QtWidgets.QWidget()
                    tmp_holder.setLayout(self.uiList[ui])
                    cur_layout.addWidget(tmp_holder)
        else:
            return
    def quickMsg(self, msg, block=1, ask=0):
        tmpMsg = QtWidgets.QMessageBox(self) # for simple msg that no need for translation
        tmpMsg.setWindowTitle("Info")
        lineCnt = len(msg.split('\n'))
        if lineCnt > 25:
            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(1)
            content = QtWidgets.QWidget()
            scroll.setWidget(content)
            layout = QtWidgets.QVBoxLayout(content)
            tmpLabel = QtWidgets.QLabel(msg)
            tmpLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            layout.addWidget(tmpLabel)
            tmpMsg.layout().addWidget(scroll, 0, 0, 1, tmpMsg.layout().columnCount())
            tmpMsg.setStyleSheet("QScrollArea{min-width:600 px; min-height: 400px}")
        else:
            tmpMsg.setText(msg)
        if block == 0:
            tmpMsg.setWindowModality( QtCore.Qt.NonModal )
        if ask==0:
            tmpMsg.addButton("OK",QtWidgets.QMessageBox.YesRole)
        else:
            tmpMsg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if block:
            value = tmpMsg.exec_()
            if value == QtWidgets.QMessageBox.Ok:
                return 1
            else:
                return 0
        else:
            tmpMsg.show()
            return 0
    def quickInfo(self, info, force=0):
        if hasattr( self.window(), "quickInfo") and force == 0:
            self.window().statusBar().showMessage(info)
    def qui_policy(self, ui_list, w, h):
        # reference value
        policyList = ( 
            QtWidgets.QSizePolicy.Fixed, 
            QtWidgets.QSizePolicy.Minimum, 
            QtWidgets.QSizePolicy.Maximum, 
            QtWidgets.QSizePolicy.Preferred, 
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.MinimumExpanding, 
            QtWidgets.QSizePolicy.Ignored,
        )
        # 0 = fixed; 1 > min; 2 < max; 3 = prefered; 4 = <expanding>; 5 = expanding> Aggresive; 6=4 ignored size input
        if not isinstance(ui_list, (list, tuple)):
            ui_list = [ui_list]
        for each_ui in ui_list:
            if isinstance(each_ui, str):
                each_ui = self.uiList[each_ui]
            each_ui.setSizePolicy(policyList[w],policyList[h])
    def quickModKeyAsk(self):
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        clickMode = 0 # basic mode
        if modifiers == QtCore.Qt.ControlModifier:
            clickMode = 1 # ctrl
        elif modifiers == QtCore.Qt.ShiftModifier:
            clickMode = 2 # shift
        elif modifiers == QtCore.Qt.AltModifier:
            clickMode = 3 # alt
        elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.AltModifier:
            clickMode = 4 # ctrl+shift+alt
        elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier:
            clickMode = 5 # ctrl+alt
        elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier:
            clickMode = 6 # ctrl+shift
        elif modifiers == QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier:
            clickMode = 7 # alt+shift
        return clickMode
class TestWin(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(main_layout)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_win = CodeView()
    main_win.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()

