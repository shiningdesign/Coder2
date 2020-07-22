import os, sys
def auto_load(tPath,tFile,tBackup=''):
    seg = tPath.split('/')
    if len(seg)==0: return 'pass' # case 0: wrong format
    top_path = os.path.dirname(__file__)
    while os.path.basename(top_path)!=seg[0] and top_path != os.path.dirname(top_path): top_path = os.path.dirname(top_path)
    base_path = os.path.normpath(os.path.join(top_path,*seg[1:]))
    if not os.path.isdir(base_path):
        #case 1: not found
        # do backup path
        if tBackup !='':
            if '*' in tBackup:
                return 'from {0} import *'.format(tBackup.replace('*',''))
            else:
                return 'import {0} as {1}'.format(tBackup,tFile)
        else:
            print('Error Path Not Found: {0}'.format(tPath))
            return 'pass'
    else:
        base_path in sys.path or sys.path.append(base_path)
    if '*' in tFile:
        return 'from {0} import *'.format(tFile.replace('*','')) # case 2:load all
    return 'import {0}'.format(tFile) # case 3: just import

exec(auto_load('Pipeline/_template','universal_tool_template_2010*','Coder2_template_2010*'))
exec(auto_load('Pipeline/_template','CodeView','Coder2_CodeView'))
exec(auto_load('Pipeline/_template','LNTextEdit','Coder2_LNTextEdit'))

#from Coder2_template_2010 import *
#############################################
# User Class creation
#############################################
version = '2.3'
date = '2020.07.22'
log = '''
#------------------------------
author: ying
support: https://github.com/shiningdesign
#------------------------------
Coder is designed for Maya coder by Maya coder, 
a true example of combining Maya UI elements with Qt UI elements, and maintain interaction.
v2.3: (2020.07.22):
  * add code auto completion from maya in setting menu
  * add Chinese language
v2.2: (2020.07.21)
  * prepare public release coding
v2.1: (2020.07.17)
  * add mel cmd info tool
v2.0: (2020.07.07)
  * upgrade to template 2010
  * add count select list
  * write mel as well
  * remove file list
v1.7: (2020.06.30)
  * added attribute selection
  * open clip path in mel supported
  * add win btn like node editor
v1.6: (2020.06.23)
  * add utt Maya code and mel panel
v1.5: (2020.06.09)
  * add quick operation button list
  * add mod key File open in 2nd cmd
v1.4: (2020.05.21)
  * option menu to convert unicode to str in selection
v1.3: 
  * (2017.11.07) improve nagivation
  * (2017.10.30) fix open file with import dialog
  * (2017.10.26) add selection based auto maya cmds
v1.2: (2017.10.10):
  * update openFile_action for other app to interact
v1.1: (2017.07.05):
  * add comment shortcut and actions
v0.1: (2016.10.13)
  * PyQtMixMayaUI. a test with Model view and script editor in Qt
  * ShoutMUI. a test of multiple script editor in one customize window 
#------------------------------
'''
help = '''
File Open / Open from Clipboard path: 
  * hold ctrl/alt/shift to open in 2nd cmd box
Check menu for hotkey operations
'''
# --------------------
#  user module list
# --------------------
import maya.mel as mel
import time # for date text

class Coder2(UniversalToolUI):
    def __init__(self, parent=None, mode=0):
        UniversalToolUI.__init__(self, parent)
        
        # class variables
        self.version= version
        self.date = date
        self.log = log
        self.help = help
        
        # mode: example for receive extra user input as parameter
        self.mode = 0
        if mode in [0,1]:
            self.mode = mode # mode validator
        # Custom user variable
        #------------------------------
        # initial data
        #------------------------------
        self.memoData['data']=[]
        self.memoData['settingUI']=[]
        self.qui_user_dict = {} # e.g: 'edit': 'LNTextEdit',
        
        if isinstance(self, QtWidgets.QMainWindow):
            self.setupMenu()
        self.setupWin()
        self.setupUI()
        self.Establish_Connections()
        self.loadLang()
        self.loadData()
        
    #------------------------------
    # overwrite functions
    #------------------------------
    def setupMenu(self):
        self.qui_menubar('file_menu;&File | setting_menu;Setting | insert_menu;&Insert | help_menu;&Help')
        
        info_list = ['export', 'import','user']
        info_item_list = ['{0}Config_atn;{1} Config (&{2}),Ctrl+{2}'.format(info,info.title(),info.title()[0]) for info in info_list]+['_']
        self.qui_menu('|'.join(info_item_list), 'setting_menu')
        # toggle on top
        self.qui_menu('toggleTop_atn;Toggle Always-On-Top', 'setting_menu')
        
        # custom menu item
        self.qui_menu('openFile_atn;Open File,F5 | saveFile_atn;Save File,F4','file_menu')
        self.qui_menu('clearHistory_atn;Clear History,Ctrl+Shift+H | saveEdit_atn;Save Edit,Ctrl+Shift+F | showConfig_atn;Show Config Folder,Ctrl+Alt+F | search_atn;Search Text,F2 | searchNext_atn;Search Next,F3 | goLine_atn;Go Line,Ctrl+G | _ ', 'setting_menu')
        for i in range(1,5):
            self.qui_menu('level_{0}_atn;Level {0},Ctrl+{0}'.format(i), 'setting_menu')
        self.qui_menu('updateNavi_atn;Update Navigator,Ctrl+R | _ | edit_autoCompletionToggle_atn;Toggle Code Auto Completion', 'setting_menu')
        self.uiList['edit_autoCompletionToggle_atn'].setCheckable(1)
        self.uiList['edit_autoCompletionToggle_atn'].setChecked(0)
        tmp_item_list = [ 
            ('selection_insert_toggleStr','Toggle unicode selection to str',''),
            ('selection_insert','Insert Selected Item Names','Alt+S'),
            ('selectionAttr_insert','Insert Selected Attr Names','Alt+Shift+S'),
            ('date_insert','Insert Date','Alt+D'),
            ('ls_insert','Insert variable into selection','Ctrl+Shift+S'),
            ('count_insert','Count variable value','Ctrl+Alt+Shift+S'),
        ]
        menu_str = '|'.join(['{0}_atn;{1},{2}'.format(*x) for x in tmp_item_list] + ['_'])
        self.qui_menu(menu_str, 'insert_menu')
        self.uiList['selection_insert_toggleStr_atn'].setCheckable(1)
        self.uiList['selection_insert_toggleStr_atn'].setChecked(0)
        
        # default help menu
        super(self.__class__,self).setupMenu()
    
    def setupWin(self):
        super(self.__class__,self).setupWin()
        # self.setGeometry(500, 300, 250, 110) # self.resize(250,250)
        if hostMode == "desktop":
            QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        self.setStyleSheet("QLineEdit:disabled{background-color: gray;}")
        
    def setupUI(self):
        super(self.__class__,self).setupUI('grid')
        #------------------------------
        # user ui creation part
        #------------------------------
        # script editor need to be initialize for log and cmd to work properly, or cmd and log just not show
        if cmds.window("scriptEditorPanel1Window", exists=1):
            cmds.deleteUI( "scriptEditorPanel1Window", window=1)
        mel.eval("ScriptEditor") 
        #=======================================
        #  ui - maya command box
        #=======================================
        self.uiList['main_1_cmdBox'] = self.CmdBox('main_1_cmdBox')
        self.uiList['main_2_cmdBox'] = self.CmdBox('main_2_cmdBox')
        self.uiList['main_3_cmdBox'] = self.CmdBox('main_3_cmdBox',type='mel')
        self.uiList['main_logBox'] = self.LogBox('main_logBox')
        #=======================================
        #  quick operation buttons
        #=======================================
        self.qui('file_openClipboardPath_btn;Open from Clipboard Path | file_showScenePath_btn;Show Scene Path | win_nodeEditor_btn;Node Editor | selection_count_btn;Count Selection | btn_space', 'quick_layout;hbox')
        #=======================================
        #  ui - browse tabs
        #=======================================
        self.uiList['maya_utt_coder'] = CodeView.CodeView()
        
        self.qui('mel_whatIs_btn;whatIs | mel_space', 'mel_tool_layout;hbox')
        self.qui('mel_tool_layout | main_3_cmdBox', 'mel_layout;vbox')
        self.qui('main_2_cmdBox | mel_layout | navi_tree;(navi,line) | maya_utt_coder', 'side_tab;h', '(Cmd,Mel,Navi,File,utt Maya)')
        self.uiList['side_tab'].setStyleSheet("QTabWidget::tab-bar{alignment:left;}QTabBar::tab { min-width: 100px; }")
        self.uiList['navi_tree'].setColumnWidth(0,300)
        # response
        self.uiList['navi_tree'].itemDoubleClicked.connect( self.navi_action)
        
        #=======================================
        #  ui - main block cmd
        #=======================================
        self.qui('main_1_cmdBox | side_tab','cmdBox_split;h')
        self.qui('main_logBox | cmdBox_split','main_split;v')
        self.qui('quick_layout | main_split','main_layout')
        
        self.memoData['settingUI']=[]
        #------------- end ui creation --------------------
        keep_margin_layout = ['main_layout']
        keep_margin_layout_obj = []
        # add tab layouts
        for each in self.uiList.values():
            if isinstance(each, QtWidgets.QTabWidget):
                for i in range(each.count()):
                    keep_margin_layout_obj.append( each.widget(i).layout() )
        for name, each in self.uiList.items():
            if isinstance(each, QtWidgets.QLayout) and name not in keep_margin_layout and not name.endswith('_grp_layout') and each not in keep_margin_layout_obj:
                each.setContentsMargins(0, 0, 0, 0)
        self.quickInfo('Ready')
        # self.statusBar().hide()
        
    def Establish_Connections(self):
        super(self.__class__,self).Establish_Connections()
        # custom ui response
        # shortcut connection
        self.hotkey = {}
        # self.hotkey['my_key'] = QtWidgets.QShortcut(QtGui.QKeySequence( "Ctrl+1" ), self)
        # self.hotkey['my_key'].activated.connect(self.my_key_func)
        
    def loadData(self):
        print("Load data")
        # load config
        config = {}
        config['user_root'] = os.path.expanduser('~')
        config['template_path'] = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '_template'))
        # overload config file if exists next to it
        # then, save merged config into self.memoData['config']
        prefix, ext = os.path.splitext(self.location)
        config_file = prefix+'_config.json'
        if os.path.isfile(config_file):
            external_config = self.readDataFile(config_file)
            print('info: External config file found.')
            if isinstance( external_config, dict ):
                self.memoData['config'] = self.dict_merge(config, external_config, addKey=1)
                print('info: External config merged.')
            else:
                self.memoData['config'] = config
                print('info: External config is not a dict and ignored.')
        else:
            self.memoData['config'] = config
        
        # load user setting
        user_setting = {}
        if self.mode == 0:
            # for standalone mode only
            user_dirPath = os.path.join(os.path.expanduser('~'), 'Tool_Config', self.__class__.__name__)
            user_setting_filePath = os.path.join(user_dirPath, 'setting.json')
            if os.path.isfile(user_setting_filePath):
                user_setting = self.readDataFile(user_setting_filePath)
                if 'sizeInfo' in user_setting:
                    self.setGeometry(*user_setting['sizeInfo'])
        # custome setting loading here
        preset = {}
        for ui in self.memoData['settingUI']:
            if ui in user_setting:
                preset[ui]=user_setting[ui]
        
        self.updateUI(preset)
        self.updateCMD()
        self.updateCodeView()
        
    def closeEvent(self, event):
        if self.mode == 0:
            # for standalone mode only
            user_dirPath = os.path.join(os.path.expanduser('~'), 'Tool_Config', self.__class__.__name__)
            if not os.path.isdir(user_dirPath):
                try: 
                    os.makedirs(user_dirPath)
                except OSError:
                    print('Error on creation user data folder')
            if not os.path.isdir(user_dirPath):
                print('Fail to create user dir.')
                return
            # save setting
            user_setting = {}
            geoInfo = self.geometry()
            user_setting['sizeInfo'] = [geoInfo.x(), geoInfo.y(), geoInfo.width(), geoInfo.height()]
            # custome setting saving here
            for ui in self.memoData['settingUI']:
                if ui.endswith('_choice'):
                    user_setting[ui] = unicode(self.uiList[ui].currentText())
                elif ui.endswith('_check'):
                    user_setting[ui] = self.uiList[ui].isChecked()
                elif ui.endswith('_input'):
                    user_setting[ui] = unicode(self.uiList[ui].text())
                elif ui.endswith('_tab'):
                    user_setting[ui] = self.uiList[ui].currentIndex()
            user_setting_filePath = os.path.join(user_dirPath, 'setting.json')
            self.writeDataFile(user_setting, user_setting_filePath)
    

    #------------------------------
    #  default overwrite functions
    #------------------------------
    def default_action(self, ui_name):
        # override for more custom handling
        if ui_name.startswith('level_'):
            self.header_action(int(ui_name.split('level_')[1][0]))
        elif ui_name.endswith('_insert_atn'):
            self.insert_action(ui_name.rsplit('_insert_atn',1)[0])
        else:
            print("No action defined for this button: "+ui_name)
    # - example button functions
    
    #=======================================
    #  functions: update UIs
    #=======================================
    def updateUI(self, preset):
        for ui_name in preset:
            if ui_name.endswith('_choice'):
                if preset[ui_name] != '':
                    the_idx = self.uiList[ui_name].findText(preset[ui_name])
                    if the_idx != -1:
                        self.uiList[ui_name].setCurrentIndex(the_idx)
            elif ui_name.endswith('_check'):
                self.uiList[ui_name].setChecked(preset[ui_name])
            elif ui_name.endswith('_input'):
                if preset[ui_name] != '':
                    self.uiList[ui_name].setText(preset[ui_name])
            elif ui_name.endswith('_tab'):
                self.uiList[ui_name].setCurrentIndex(preset[ui_name])
    def updateCMD(self):
        config = self.memoData['config']
        # load user data
        user_dirPath = os.path.join(config['user_root'], 'Tool_Config', self.__class__.__name__)
        # user script
        for i in [1,2]:
            user_script_filePath = os.path.join(user_dirPath, 'main_{0}_cmdBox.py'.format(i))
            if os.path.isfile(user_script_filePath):
                script_text = self.readTextFile(user_script_filePath)
                cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_{0}_cmdBox'.format(i)]), e=1, t=script_text)
        for i in [3]:
            user_script_filePath = os.path.join(user_dirPath, 'main_{0}_cmdBox.mel'.format(i))
            if os.path.isfile(user_script_filePath):
                script_text = self.readTextFile(user_script_filePath)
                cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_{0}_cmdBox'.format(i)]), e=1, t=script_text)
    def updateCodeView(self):
        file_path = os.path.join(self.memoData['config']['template_path'],'utt_code_maya.py')
        if not os.path.isfile(file_path):
            file_path = os.path.join(os.path.dirname(self.location), 'template_code_maya.py')
        self.uiList['maya_utt_coder'].setCodePath(file_path)
    
    #=======================================
    #  functions : file
    #=======================================
    def saveEdit_action(self):
        user_dirPath = os.path.join(self.memoData['config']['user_root'], 'Tool_Config', self.__class__.__name__)
        if not os.path.isdir(user_dirPath):
            try: 
                os.makedirs(user_dirPath)
            except OSError:
                print('Error on creation user data folder')
        if not os.path.isdir(user_dirPath):
            print('Fail to create user dir.')
            return
        # user script
        for i in [1,2]:
            script_text = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_{0}_cmdBox'.format(i)]), q=1, t=1)
            user_script_filePath = os.path.join(user_dirPath, 'main_{0}_cmdBox.py'.format(i))
            self.writeTextFile(script_text, user_script_filePath)
        for i in [3]:
            script_text = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_{0}_cmdBox'.format(i)]), q=1, t=1)
            user_script_filePath = os.path.join(user_dirPath, 'main_{0}_cmdBox.mel'.format(i))
            self.writeTextFile(script_text, user_script_filePath)
        cur_time = QtCore.QTime.currentTime()
        text = str(cur_time.toString("hh:mm"))
        self.quickInfo('File Saved in user "Tool_Config" folder. {0}'.format(text) )
    def showConfig_action(self):
        user_dirPath = os.path.join(self.memoData['config']['user_root'], 'Tool_Config', self.__class__.__name__)
        if not os.path.isdir(user_dirPath):
            print('Not yet create user dir.')
        else:
            self.openFolder(user_dirPath)
    def openFile_action(self, file='', alt=0):
        filePath = cmds.file(q=1, sn=1)
        if filePath == '':
            filePath = None
        else:
            filePath = os.path.dirname(filePath)
        if file == "":
            file= self.quickFileAsk('import', {'py':'Python File','mel':'Mel File'}, dir=filePath)
        if file == "":
            return
        txt_data = self.readTextFile(file)
        if alt== 1:
            cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_2_cmdBox']), e=1, t=txt_data)
        elif alt == 2:
            cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_3_cmdBox']), e=1, t=txt_data)
        else:
            # default handling
            # check if user has modifier on
            if file.endswith('.mel'):
                cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_3_cmdBox']), e=1, t=txt_data)
            else:
                mod = self.quickModKeyAsk()
                if mod == 0:
                    cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), e=1, t=txt_data)
                else:
                    cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_2_cmdBox']), e=1, t=txt_data)
    def saveFile_action(self):
        filePath = cmds.file(q=1, sn=1)
        if filePath == '':
            filePath = None
        else:
            filePath = os.path.dirname(filePath)
        file= self.quickFileAsk('export', {'py':'Python File'}, dir=filePath)
        if file == "":
            return
        script_text = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), q=1, t=1)
        self.writeTextFile(script_text, file)
        self.quickInfo('File saved: '+ file)
    #=======================================
    #  functions : code navigation
    #=======================================
    def clearHistory_action(self):
        cmds.cmdScrollFieldReporter(self.qt_to_mui(self.uiList['main_logBox']), e=1, clr=1)
    def search_action(self):
        text,ok=self.quickMsgAsk('Please Enter Search Text:')
        if ok and text!='':
            cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), e=1, searchDown=1, searchWraps=1, searchMatchCase=0, searchString=text)
            self.searchNext_action()
    def searchNext_action(self):
        res = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), q=1, searchAndSelect=1)
        print(res)
    def goLine_action(self):
        line,ok=self.quickMsgAsk('Please Enter Search Text:')
        if ok and line!='':
            cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), e=1, currentLine=int(line) )
    def header_action(self, level):
        ui_name = 'main_1_cmdBox'
        if QtWidgets.QApplication.focusWidget().parentWidget().metaObject().className() != 'QSplitter':
            ui_name = 'main_2_cmdBox'
        txt_dict ={}
        txt_dict[1]='======'
        txt_dict[2]='===='
        txt_dict[3]='----'
        txt_dict[4]='-'
        a = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), q=1, selectedText=1)
        if a != '':
            cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), e=1, insertText='{0} {1} {0}'.format(txt_dict[level], a))
        else:
            cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), e=1, insertText='{0}{0}'.format(txt_dict[level]))
    # - navi tree
    def updateNavi_action(self):
        all_text = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), q=1, t=1)
        lines = all_text.split('\n')
        cur_tree = self.uiList['navi_tree']
        cur_tree.clear()
        parentNode = cur_tree.invisibleRootItem()
        seg_pattern = re.compile('#[ ]*[=]+[a-zA-Z ]*[ ]*')
        sub_pattern = re.compile('#[ ]*-[a-zA-Z ]*-[ ]*')
        for i in range(len(lines)):
            if seg_pattern.match(lines[i]):
                name = lines[i].replace('#','').replace('=','').replace('-','').strip()
                cur_node = QtWidgets.QTreeWidgetItem([name,str(i+1)])
                '''
                name = lines[i+1].replace('#','').replace('=','').replace('-','').strip()
                cur_node = QtWidgets.QTreeWidgetItem([name,str(i+1)])
                '''
                cur_tree.invisibleRootItem().addChild(cur_node)
                cur_node.setExpanded(1)
                parentNode = cur_node
            elif sub_pattern.match(lines[i]):
                cur_node = QtWidgets.QTreeWidgetItem([lines[i].strip(),str(i+1)])
                #cur_node = QtWidgets.QTreeWidgetItem([lines[i].strip(),str(i+1)])
                parentNode.addChild(cur_node)
    def navi_action(self, item):
        cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), e=1, currentLine=int(item.text(1)) )
    #=======================================
    #  functions : core
    #=======================================
    def file_openClipboardPath_action(self):
        clipboard = QtWidgets.QApplication.clipboard()
        copy_path = unicode(clipboard.text())
        mod= self.quickModKeyAsk()
        if os.path.isfile(copy_path):
            if copy_path.endswith('.py'):
                if mod == 0:
                    self.openFile_action(copy_path)
                else:
                    self.openFile_action(copy_path, alt=1)
            elif copy_path.endswith('.mel'):
                self.openFile_action(copy_path, alt=2)
    def file_showScenePath_action(self):
        filePath = cmds.file(q=1, sn=1) # filepath
        print(filePath)
        mod= self.quickModKeyAsk()
        if mod !=0:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(filePath)
        else:
            self.openFolder(filePath)
    def win_nodeEditor_action(self):
        cmds.NodeEditorWindow()
    # - insert macro text
    def insert_action(self, data):
        selection_toStr_check = self.uiList['selection_insert_toggleStr_atn'].isChecked()
        ui_name = 'main_1_cmdBox'
        if QtWidgets.QApplication.focusWidget().parentWidget().metaObject().className() != 'QSplitter':
            ui_name = 'main_2_cmdBox'
        txt = ''
        if data == 'selection':
            selected = cmds.ls(sl=1)
            # toStr conversion
            if selection_toStr_check:
                selected = [str(x) for x in selected]
                
            if len(selected) == 1:
                txt = selected[0]
            elif len(selected)>1:
                txt = str(selected)
        if data == 'selectionAttr':
            sel_obj_list = cmds.ls(sl=1)
            sel_attr_list = cmds.channelBox("mainChannelBox", q=1, sma=1)
            if selection_toStr_check:
                sel_obj_list = [str(x) for x in sel_obj_list]
                sel_attr_list = [str(x) for x in sel_attr_list]
            if len(sel_obj_list)==1:
                # single obj, then obj.attr
                if len(sel_attr_list)==1:
                    txt = sel_obj_list[0]+'.'+sel_attr_list[0]
                else:
                    txt = str([sel_obj_list[0]+'.'+attr for attr in sel_attr_list])
            else:
                # mult obj
                if len(sel_attr_list)==1:
                    txt = str([obj+'.'+sel_attr_list[0] for obj in sel_obj_list])
                else:
                    txt = str([sel_obj_list, sel_attr_list])
        elif data == 'date':
            txt = time.strftime( '%Y.%m.%d' )
        elif data == 'ls':
            cur_text = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), q=1, selectedText=1)
            cur_text=cur_text.strip()
            cmds.python('cmds.select({0})'.format(cur_text))
        elif data == 'count':
            cur_text = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), q=1, selectedText=1)
            cur_text=cur_text.strip()
            cmds.python('print(len({0}))'.format(cur_text))
        # insert
        if txt != '':
            cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), e=1, insertText=txt)
    def selection_count_action(self):
        selection = cmds.ls(sl=1)
        if selection:
            print(len(selection))
        else:
            print(0)
    def mel_whatIs_action(self):
        cur_text = cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_3_cmdBox']), q=1, selectedText=1)
        cur_text = cur_text.strip()
        if cur_text != '':
            result = mel.eval('whatIs '+cur_text)
            print(result)
            if result == 'Run Time Command':
                result = mel.eval('runTimeCommand -q -c "{0}";'.format(cur_text))
                print(result)
    def edit_autoCompletionToggle_action(self):
        autoCompletion_check = int(self.uiList['edit_autoCompletionToggle_atn'].isChecked())
        for i in [1,2,3]:
            ui_name = 'main_{0}_cmdBox'.format(i)
            if autoCompletion_check:
                cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), e=1, showTooltipHelp=1, objectPathCompletion=1, commandCompletion=1, autoCloseBraces=1)
            else:
                cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList[ui_name]), e=1, showTooltipHelp=0, objectPathCompletion=0, commandCompletion=0, autoCloseBraces=0)
    #=======================================
    #  functions : core for CodeView
    #=======================================
    def code_action(self, item, col):
        cur_tree = self.uiList['file_tree']
        clickMode = self.quickModKeyAsk()
        currentNode = cur_tree.currentItem()
        
        if currentNode:
            # code lib view response
            if clickMode==0:
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(unicode(currentNode.text(1)))
                print('In clipboard')
            elif clickMode==2: # shift
                cmds.cmdScrollFieldExecuter(self.qt_to_mui(self.uiList['main_1_cmdBox']), e=1, insertText=unicode(currentNode.text(1)))
            elif clickMode==3: # alt
                self.uiList['note_edit'].setText(unicode(currentNode.text(1)))
            else:
                self.quickMsg(unicode(currentNode.text(1)))
    #=======================================
    #  functions : core for CmdBox
    #=======================================
    def mui_to_qt(self, mui_name):
        if hostMode != "maya":
            return
        ptr = mui.MQtUtil.findControl(mui_name)
        if ptr is None:
            ptr = mui.MQtUtil.findLayout(mui_name)
        if ptr is None:
            ptr = mui.MQtUtil.findMenuItem(mui_name)
        if ptr is not None:
            if qtMode in (0,2):
                # ==== for pyside ====
                return shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)
            elif qtMode in (1,3):
                # ==== for PyQt====
                return sip.wrapinstance(long(ptr), QtCore.QObject)
    def qt_to_mui(self, qt_obj):
        if hostMode != "maya":
            return
        ref = None
        if qtMode in (0,2):
            # ==== for pyside ====
            ref = long(shiboken.getCppPointer(qt_obj)[0])
        elif qtMode in (1,3):
            # ==== for PyQt====
            ref = long(sip.unwrapinstance(qt_obj))
        if ref is not None:
            return mui.MQtUtil.fullName(ref)
    def CmdBox(self, ui_name, type='python'):
        if cmds.cmdScrollFieldExecuter(ui_name, q=1, ex=1):
            cmds.deleteUI(ui_name)
        mui = cmds.cmdScrollFieldExecuter(ui_name, st=type, sln=1, tabsForIndent=0, showTooltipHelp=0, objectPathCompletion=0, commandCompletion=0, autoCloseBraces=0)
        if type=='python':
            cmds.cmdScrollFieldExecuter(mui, e=1, t="# Code Here")
        elif type=='mel':
            cmds.cmdScrollFieldExecuter(mui, e=1, t="// Code Here")
        return self.mui_to_qt(mui)
    def LogBox(self, ui_name):
        if cmds.cmdScrollFieldReporter(ui_name, q=1, ex=1):
            cmds.deleteUI(ui_name)
        mui = cmds.cmdScrollFieldReporter(ui_name)#, width=200, height=100)
        return self.mui_to_qt(mui)
    #=======================================
    #  functions: config
    #=======================================
    # - example file io function
    def exportConfig_action(self):
        file= self.quickFileAsk('export', {'json':'JSON data file', 'xdat':'Pickle binary file'})
        if file == "":
            return
        # export process
        ui_data = self.memoData['config']
        # file process
        if file.endswith('.xdat'):
            self.writeDataFile(ui_data, file, binary=1)
        else:
            self.writeDataFile(ui_data, file)
        self.quickInfo("File: '"+file+"' creation finished.")
    def importConfig_action(self):
        file= self.quickFileAsk('import',{'json':'JSON data file', 'xdat':'Pickle binary file'})
        if file == "":
            return
        # import process
        ui_data = ""
        if file.endswith('.xdat'):
            ui_data = self.readDataFile(file, binary=1)
        else:
            ui_data = self.readDataFile(file)
        self.memoData['config'] = ui_data
        self.quickInfo("File: '"+file+"' loading finished.")
    def userConfig_action(self):
        user_dirPath = os.path.join(os.path.expanduser('~'), 'Tool_Config', self.__class__.__name__)
        self.openFolder(user_dirPath)
        
#=======================================
#  window instance creation
#=======================================

import ctypes # for windows instance detection
single_Coder2 = None
app_Coder2 = None
def main(mode=0):
    # get parent window in Maya
    parentWin = None
    if hostMode == "maya":
        if qtMode in (0,2): # pyside
            parentWin = shiboken.wrapInstance(long(mui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        elif qtMode in (1,3): # PyQt
            parentWin = sip.wrapinstance(long(mui.MQtUtil.mainWindow()), QtCore.QObject)
    # create app object for certain host
    global app_Coder2
    if hostMode in ('desktop', 'blender', 'npp', 'fusion'):
        # single instance app mode on windows
        if osMode == 'win':
            # check if already open for single desktop instance
            from ctypes import wintypes
            order_list = []
            result_list = []
            top = ctypes.windll.user32.GetTopWindow(None)
            if top: 
                length = ctypes.windll.user32.GetWindowTextLengthW(top)
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(top, buff, length + 1)
                class_name = ctypes.create_string_buffer(200)
                ctypes.windll.user32.GetClassNameA(top, ctypes.byref(class_name), 200)
                result_list.append( [buff.value, class_name.value, top ])
                order_list.append(top)
                while True:
                    next = ctypes.windll.user32.GetWindow(order_list[-1], 2) # win32con.GW_HWNDNEXT
                    if not next:
                        break
                    length = ctypes.windll.user32.GetWindowTextLengthW(next)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(next, buff, length + 1)
                    class_name = ctypes.create_string_buffer(200)
                    ctypes.windll.user32.GetClassNameA(next, ctypes.byref(class_name), 200)
                    result_list.append( [buff.value, class_name.value, next] )
                    order_list.append(next)
            # result_list: [(title, class, hwnd int)]
            winTitle = 'Coder2' # os.path.basename(os.path.dirname(__file__))
            is_opened = 0
            for each in result_list:
                if re.match(winTitle+' - v[0-9.]* - host: desktop',each[0]) and each[1] == 'QWidget':
                    is_opened += 1
                    if is_opened == 1:
                        ctypes.windll.user32.SetForegroundWindow(each[2])
                        sys.exit(0) # 0: success, 1-127: bad error
                        return
        if hostMode in ('npp','fusion'):
            app_Coder2 = QtWidgets.QApplication([])
        elif hostMode in ('houdini'):
            pass
        else:
            app_Coder2 = QtWidgets.QApplication(sys.argv)
    
    #--------------------------
    # ui instance
    #--------------------------
    # Keep only one copy of windows ui in Maya
    global single_Coder2
    if single_Coder2 is None:
        if hostMode == 'maya':
            single_Coder2 = Coder2(parentWin, mode)
        elif hostMode == 'nuke':
            single_Coder2 = Coder2(QtWidgets.QApplication.activeWindow(), mode)
        elif hostMode == 'houdini':
            hou.session.mainWindow = hou.qt.mainWindow()
            single_Coder2 = Coder2(hou.session.mainWindow, mode)
        else:
            single_Coder2 = Coder2()
    single_Coder2.show()
    ui = single_Coder2
    if hostMode != 'desktop':
        ui.activateWindow()
    
    # loop app object for certain host
    if hostMode in ('desktop'):
        sys.exit(app_Coder2.exec_())
    elif hostMode in ('npp','fusion'):
        app_Coder2.exec_()
    return ui

if __name__ == "__main__":
    main()