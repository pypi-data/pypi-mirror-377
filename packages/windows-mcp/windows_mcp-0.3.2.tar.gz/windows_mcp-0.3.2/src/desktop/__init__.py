from uiautomation import Control, GetRootControl, ControlType, GetFocusedControl, ShowWindow, IsTopLevelWindow, IsZoomed, IsIconic, IsWindowVisible, ControlFromHandle
from src.desktop.config import EXCLUDED_CLASSNAMES,BROWSER_NAMES
from src.desktop.views import DesktopState,App,Size
from fuzzywuzzy import process
from psutil import Process
from src.tree import Tree
from time import sleep
import pyautogui as pg
from io import BytesIO
from PIL import Image
import subprocess
import ctypes
import csv
import os
import io

class Desktop:
    def __init__(self):
        ctypes.windll.user32.SetProcessDPIAware()
        self.desktop_state=None
        
    def get_state(self,use_vision:bool=False)->DesktopState:
        tree=Tree(self)
        tree_state=tree.get_state()
        if use_vision:
            nodes=tree_state.interactive_nodes
            annotated_screenshot=tree.annotated_screenshot(nodes=nodes,scale=0.5)
            screenshot=self.screenshot_in_bytes(screenshot=annotated_screenshot)
        else:
            screenshot=None
        active_app,apps=self.get_apps()
        self.desktop_state=DesktopState(apps=apps,active_app=active_app,screenshot=screenshot,tree_state=tree_state)
        return self.desktop_state
    
    def get_active_app(self,apps:list[App])->App|None:
        if len(apps)>0 and apps[0].status != "Minimized":
            return apps[0]
        return None
    
    def get_app_status(self,control:Control)->str:
        if IsIconic(control.NativeWindowHandle):
            return 'Minimized'
        elif IsZoomed(control.NativeWindowHandle):
            return 'Maximized'
        elif IsWindowVisible(control.NativeWindowHandle):
            return 'Normal'
        else:
            return 'Hidden'
    
    def get_window_element_from_element(self,element:Control)->Control|None:
        while element is not None:
            if IsTopLevelWindow(element.NativeWindowHandle):
                return element
            element = element.GetParentControl()
        return None

    def get_element_under_cursor(self)->Control:
        return GetFocusedControl()
    
    def get_default_browser(self):
        mapping = {
            "ChromeHTML": "Google Chrome",
            "FirefoxURL": "Mozilla Firefox",
            "MSEdgeHTM": "Microsoft Edge",
            "IE.HTTP": "Internet Explorer",
            "OperaStable": "Opera",
            "BraveHTML": "Brave",
            "SafariHTML": "Safari"
        }
        command= "(Get-ItemProperty HKCU:\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice).ProgId"
        browser,_=self.execute_command(command)
        return mapping.get(browser.strip())
        
    def get_default_language(self)->str:
        command="Get-Culture | Select-Object Name,DisplayName | ConvertTo-Csv -NoTypeInformation"
        response,_=self.execute_command(command)
        reader=csv.DictReader(io.StringIO(response))
        return "".join([row.get('DisplayName') for row in reader])
    
    def get_apps_from_start_menu(self)->dict[str,str]:
        command='Get-StartApps | ConvertTo-Csv -NoTypeInformation'
        apps_info,_=self.execute_command(command)
        reader=csv.DictReader(io.StringIO(apps_info))
        return {row.get('Name').lower():row.get('AppID') for row in reader}
    
    def execute_command(self,command:str)->tuple[str,int]:
        try:
            # Use UTF-8 encoding for better Chinese character support
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', 
                 '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; ' + command], 
                capture_output=True, check=True, text=True, encoding='utf-8',cwd=os.path.expanduser(path='~\\Desktop')
            )
            return (result.stdout, result.returncode)
        except subprocess.CalledProcessError as e:
            try:
                # Try UTF-8 first
                error_output = e.stdout if hasattr(e, 'stdout') and e.stdout else ''
                return (error_output, e.returncode)
            except Exception:
                # Fallback to GBK for Chinese Windows systems
                try:
                    result = subprocess.run(
                        ['powershell', '-NoProfile', '-Command', command], 
                        capture_output=True, check=False
                    )
                    return (result.stdout.decode('gbk', errors='ignore'), result.returncode)
                except Exception:
                    return ('Command execution failed with encoding issues', 1)
        
    def is_app_browser(self,node:Control):
        process=Process(node.ProcessId)
        return process.name() in BROWSER_NAMES
    
    def get_windows_version(self)->str:
        response,status=self.execute_command("(Get-CimInstance Win32_OperatingSystem).Caption")
        if status==0:
            return response.strip()
        return "Windows"
    
    def resize_app(self,size:tuple[int,int]=None,loc:tuple[int,int]=None)->tuple[str,int]:
        active_app=self.desktop_state.active_app
        if active_app is None:
            return ('No active app found',1)
        app_control=ControlFromHandle(active_app.handle)
        if loc is None:
            x=app_control.BoundingRectangle.left
            y=app_control.BoundingRectangle.top
            loc=(x,y)
        if size is None:
            width=app_control.BoundingRectangle.width()
            height=app_control.BoundingRectangle.height()
            size=(width,height)
        x,y=loc
        width,height=size
        app_control.MoveWindow(x,y,width,height)
        return (f'Application {active_app.name.title()} resized to {width}x{height} at {x},{y}.',0)
        
    def launch_app(self,name:str)->tuple[str,int]:
        apps_map=self.get_apps_from_start_menu()
        
        # Improved fuzzy matching for Chinese and English app names
        # First try exact match (case insensitive)
        exact_matches = {k: v for k, v in apps_map.items() if name.lower() in k.lower() or k.lower() in name.lower()}
        if exact_matches:
            # Use the first exact match
            app_name = list(exact_matches.keys())[0]
            app_id = exact_matches[app_name]
            if app_id.endswith('.exe'):
                _,status=self.execute_command(f'Start-Process "{app_id}"')
            else:
                _,status=self.execute_command(f'Start-Process "shell:AppsFolder\\{app_id}"')
            response=f'Launched {name.title()}. Wait for the app to launch...'
            return response,status
        
        # If no exact match, use fuzzy matching with lower threshold for Chinese
        matched_app=process.extractOne(name,apps_map,score_cutoff=60)
        if matched_app is not None:
            app_id,_,app_name=matched_app
            if app_id.endswith('.exe'):
                _,status=self.execute_command(f'Start-Process "{app_id}"')
            else:
                _,status=self.execute_command(f'Start-Process "shell:AppsFolder\\{app_id}"')
            response=f'Launched {name.title()}. Wait for the app to launch...'
            return response,status
        
        # Try partial matching for Chinese characters
        for app_name, app_id in apps_map.items():
            if any(char in app_name for char in name) or any(char in name for char in app_name):
                if app_id.endswith('.exe'):
                    _,status=self.execute_command(f'Start-Process "{app_id}"')
                else:
                    _,status=self.execute_command(f'Start-Process "shell:AppsFolder\\{app_id}"')
                response=f'Launched {name.title()}. Wait for the app to launch...'
                return response,status
        
        return (f'Application {name.title()} not found in start menu. Available apps with similar names: {list(apps_map.keys())[:5]}',1)
    
    def switch_app(self,name:str)->tuple[str,int]:
        apps={app.name:app for app in [self.desktop_state.active_app]+self.desktop_state.apps if app is not None}
        matched_app:tuple[str,float]=process.extractOne(name,list(apps.keys()))
        if matched_app is None:
            return (f'Application {name.title()} not found.',1)
        app_name,_=matched_app
        app=apps.get(app_name)
        if IsIconic(app.handle):
            ShowWindow(app.handle, cmdShow=9)
            return (f'{app_name.title()} restored from minimized state.',0)
        else:
            shortcut=['alt','tab']
            for app in apps.values():
                if app.name==app_name:
                    break
                pg.hotkey(*shortcut)
                pg.sleep(0.1)
            return (f'Switched to {app_name.title()} window.',0)

    def get_app_size(self,control:Control):
        window=control.BoundingRectangle
        if window.isempty():
            return Size(width=0,height=0)
        return Size(width=window.width(),height=window.height())
    
    def is_app_visible(self,app)->bool:
        is_minimized=self.get_app_status(app)!='Minimized'
        size=self.get_app_size(app)
        area=size.width*size.height
        is_overlay=self.is_overlay_app(app)
        return not is_overlay and is_minimized and area>10
    
    def is_overlay_app(self,element:Control) -> bool:
        no_children = len(element.GetChildren()) == 0
        is_name = "Overlay" in element.Name.strip()
        return no_children or is_name
        
    def get_apps(self) -> tuple[App|None,list[App]]:
        try:
            sleep(0.5)
            desktop = GetRootControl()  # Get the desktop control
            elements = desktop.GetChildren()
            apps = []
            for depth, element in enumerate(elements):
                if element.ClassName in EXCLUDED_CLASSNAMES or self.is_overlay_app(element):
                    continue
                if element.ControlType in [ControlType.WindowControl, ControlType.PaneControl]:
                    status = self.get_app_status(element)
                    size=self.get_app_size(element)
                    apps.append(App(name=element.Name, depth=depth, status=status, size=size, process_id=element.ProcessId, handle=element.NativeWindowHandle))
        except Exception as ex:
            print(f"Error: {ex}")
            apps = []

        active_app=self.get_active_app(apps)
        apps=apps[1:] if len(apps)>1 else []
        return (active_app,apps)
    
    def screenshot_in_bytes(self,screenshot:Image.Image)->bytes:
        io=BytesIO()
        screenshot.save(io,format='PNG')
        bytes=io.getvalue()
        return bytes

    def get_screenshot(self,scale:float=0.7)->Image.Image:
        screenshot=pg.screenshot()
        size=(screenshot.width*scale, screenshot.height*scale)
        screenshot.thumbnail(size=size, resample=Image.Resampling.LANCZOS)
        return screenshot