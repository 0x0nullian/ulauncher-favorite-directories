import os
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

class FavoriteDirsExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def get_directories(self):
        """
        Reads directories from extension preferences.
        Returns a LIST to preserve order, with each item as a dict: {'keyword': 'xxx', 'path': '/yyy/zzz'}
        """
        dirs = []
        # 'self.preferences' is a dict of all preferences for this extension
        for key, value in self.preferences.items():
            # Ignore the special 'favdirs_keyword' preference and any empty values
            if key == 'favdirs_keyword' or not value.strip():
                continue
            # Expecting format like: mydocs=/home/user/Documents
            try:
                # Split only on the first '=' to handle paths that might contain '='
                keyword, path = value.split('=', 1)
                dirs.append({'keyword': keyword.strip(), 'path': path.strip()})
            except ValueError:
                # If line doesn't contain '=', treat the whole value as a path, use a default keyword
                dirs.append({'keyword': os.path.basename(value.strip()) or 'Folder', 'path': value.strip()})
        return dirs

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        # Get the user's custom keyword from the extension preferences
        activation_keyword = extension.preferences.get('favdirs_keyword', 'fd')
        # Get the query string after the user's keyword
        query_arg = event.get_argument() or ""

        # Get the ordered list of directories
        directories = extension.get_directories()
        items = []

        for entry in directories:
            dir_keyword = entry['keyword']
            dir_path = entry['path']

            # Perform a case-insensitive match against the user's query
            if query_arg.lower() in dir_keyword.lower():
                items.append(ExtensionResultItem(
                    icon='images/folder.png',
                    name=f"{dir_keyword}",
                    description=dir_path,
                    # Open the directory with the default file manager when selected
                    on_enter=OpenAction(dir_path)
                ))

        # If there's a query but no matches, show a hint
        if query_arg and not items:
            items.append(ExtensionResultItem(
                icon='images/folder.png',
                name='No matching favorite directory found',
                description='Try a different search term.',
                on_enter=OpenAction('')  # Does nothing, but required
            ))

        # If there's no query, show all favorites (already in order)
        if not query_arg:
            if directories:
                for entry in directories:
                    items.append(ExtensionResultItem(
                        icon='images/folder.png',
                        name=f"{entry['keyword']}",
                        description=entry['path'],
                        on_enter=OpenAction(entry['path'])
                    ))
            else:
                # Show a hint if no directories are configured
                items.append(ExtensionResultItem(
                    icon='images/folder.png',
                    name='No favorite directories configured',
                    description=f'Go to Ulauncher Preferences → Extensions → {extension.name} → and add paths like "docs=/home/yourname/Documents"',
                    on_enter=OpenAction('')
                ))

        return RenderResultListAction(items)

if __name__ == '__main__':
    FavoriteDirsExtension().run()
