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
        Returns a list of dictionaries in the order defined in the manifest.
        Each dictionary has 'keyword' and 'path'.
        """
        # We have 10 items in the manifest, from item1 to item10
        pref_ids = [f'item{i}' for i in range(1, 11)]
        dirs = []
        for pref_id in pref_ids:
            value = self.preferences.get(pref_id, '').strip()
            if value:
                # Split by the first '=' to get keyword and path
                parts = value.split('=', 1)
                if len(parts) == 2:
                    keyword, path = parts[0].strip(), parts[1].strip()
                else:
                    # If no '=', use the basename of the path as the keyword
                    path = value
                    keyword = os.path.basename(path)
                dirs.append({'keyword': keyword, 'path': path})
        return dirs

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        # Get the query string (what the user typed after the extension keyword)
        query_arg = event.get_argument() or ""
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
                    on_enter=OpenAction(dir_path)
                ))

        # If there's a query but no matches, show a hint
        if query_arg and not items:
            items.append(ExtensionResultItem(
                icon='images/folder.png',
                name='No matching favorite directory found',
                description='Try a different search term.',
                on_enter=OpenAction('')
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
                items.append(ExtensionResultItem(
                    icon='images/folder.png',
                    name='No favorite directories configured',
                    description='Go to Ulauncher Preferences → Extensions → Favorite Directories and set up directories in the format "keyword=path".',
                    on_enter=OpenAction('')
                ))

        return RenderResultListAction(items)

if __name__ == '__main__':
    FavoriteDirsExtension().run()
