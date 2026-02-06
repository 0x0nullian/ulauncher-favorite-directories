import os
import json
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction

class FavoriteDirsExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
    
    def get_directories(self):
        """Read directories from JSON file"""
        try:
            # Get the path to the extension directory
            extension_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(extension_dir, 'directories.json')
            
            with open(json_path, 'r') as f:
                directories = json.load(f)
            
            # Validate structure
            for dir_info in directories:
                if 'keyword' not in dir_info or 'path' not in dir_info:
                    print(f"Warning: Invalid entry in directories.json: {dir_info}")
            
            return directories
        except Exception as e:
            print(f"Error reading directories.json: {e}")
            return []

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query_arg = event.get_argument() or ""
        query_lower = query_arg.lower()
        
        # Get directories from JSON file
        directories = extension.get_directories()
        items = []
        
        for dir_info in directories:
            keyword = dir_info.get('keyword', '')
            path = dir_info.get('path', '')
            description = dir_info.get('description', path)
            
            # Show all if no query, or filter by keyword
            if not query_arg or query_lower in keyword.lower():
                items.append(ExtensionResultItem(
                    icon='images/dir.png',
                    name=keyword,
                    description=description,
                    on_enter=OpenAction(path)
                ))
        
        # If no directories found or no matches
        if not items:
            if directories and query_arg:
                items.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name='No matching directories found',
                    description='Try a different search term',
                    on_enter=OpenAction('')
                ))
            else:
                items.append(ExtensionResultItem(
                    icon='images/dir.png',
                    name='No directories configured',
                    description='Edit directories.json to add your folders',
                    on_enter=OpenAction('')
                ))
        
        return RenderResultListAction(items)

if __name__ == '__main__':
    FavoriteDirsExtension().run()
