# coding: utf-8
from PySide6.QtWidgets import QFileDialog, QWidget
from PySide6.QtCore import QStandardPaths
import pathlib, os

class Dialog(object):

        class Extensions(object):

            PY_FILE = "Arquivos python (*.py)"

            VB_FILE = "Arquivos vb.net (*.vb)"

            CS_FILE = "Arquivos c# (*.cs)"

            PDF_FILE = "Arquivos PDF (*.pdf)"

            ALL_FILE = "Todos os arquivos (*)"

            PY_PROJ = "Projetos python (*.pyproj)"

            VB_PROJ = "Projetos python (*.vbproj)"

            CS_PROJ = "Projetos python (*.csproj)"

            SLN = "Solutions (*.sln)"

            @classmethod
            def get(cls, _file : str):
                if _file.endswith(".cs"):
                    return cls.CS_FILE
                elif _file.endswith(".vb"):
                    return cls.VB_FILE
                elif _file.endswith(".py"):
                    return cls.PY_FILE

        
        def saveFileName(parent : QWidget, title : str, extensao : str, name = "", initial_dir: str = None):
            FileDialog = QFileDialog()
            if not initial_dir:
                initial_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            FileDialog.setDirectory(initial_dir)

            options = FileDialog.options()
            return FileDialog.getSaveFileName(parent, title, name, extensao, options=options)


        def openFileName(parent: QWidget, title: str, extensions: list[str] = [Extensions.ALL_FILE] , use_filter = False, multiple_selection = False, initial_dir: str = None):
            FileDialog = QFileDialog()
            if not initial_dir:
                initial_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            FileDialog.setDirectory(initial_dir)

            options = FileDialog.options()
            FileDialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        
            func_get_open_file = FileDialog.getOpenFileNames if multiple_selection else FileDialog.getOpenFileName

            if use_filter:
                # Define o filtro para aceitar v�rias extens�es
                _filter = "Arquivos ("
                for ext in extensions:
                    ext = ext.split("(")[1].replace(")", "")
                    _filter += f"{ext};"
                _filter += ')'
        
                return func_get_open_file(parent, title, "", _filter, options=options)
            else:
                return func_get_open_file(parent, title, "", ";;".join(extensions), options=options)

        def openDirectory(parent: QWidget, title: str, initial_dir: str = None, name=""):
            FileDialog = QFileDialog()
            FileDialog.setFileMode(QFileDialog.FileMode.Directory)

            if not initial_dir:
                initial_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)

            FileDialog.setDirectory(initial_dir)
            options = FileDialog.options()
            
            return FileDialog.getExistingDirectory(parent, title, name, options=options)

        def extensions(types : list[dict[str, str]]):
            ''' 
                types: ex [{'title' : 'Arquivos python', 'extension' : 'py'} , ...]
            '''
    
            return [f"{extension['title']} (*.{extension['extension']})" for extension in types]

        def extension(title : str, extension : str):
            return f"{title} (*.{extension})"

        def is_forbidden_folder(folder: str) -> bool:
            folder_path = os.path.normpath(folder)
            
            # Bloquear unidades raiz (C:\, D:\ etc.)
            if pathlib.Path(folder_path).parent == pathlib.Path(folder_path):
                return True

            # Bloquear pastas padrão do sistema
            forbidden_locations = [
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation),
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation),
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation),
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation),
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation),
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MoviesLocation),
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
            ]

            folder_path_lower = folder_path.lower()
            for system_path in forbidden_locations:
                if os.path.normpath(system_path).lower() == folder_path_lower:
                    return True

            return False




