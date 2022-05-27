#!/usr/bin/env python
# vim:fileencoding=utf-8


__license__ = 'FEMBOY ASS'
__copyright__ = '2022, Bingus <bingusBruh>'

import re
import math
from xml.dom.minidom import Element
from qt.core import QAction, QInputDialog
from css_parser.css import CSSRule

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool

from calibre import force_unicode
from calibre.gui2 import error_dialog
from calibre.ebooks.oeb.polish.container import OEB_DOCS, OEB_STYLES, serialize
from calibre.ebooks.oeb.base import etree


class DemoTool(Tool):

    #: Set this to a unique name it will be used as a key
    name = 'demo-tool'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icons('images/icon.png'), 'Bionic-Reading', self.gui)  # noqa
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'bionic-rading-tool', default_keys=('Ctrl+Shift+Alt+B',))
        ac.triggered.connect(self.ask_user)
        return ac

    def ask_user(self):
        # Ask the user for a factor by which to bionically vibe
        factor, ok = QInputDialog.getDouble(
            self.gui, 'Enter a bionification fraction', 'How much of each word should be boldened',
            value=0.5, min=0.1, max=0.9
        )
        if ok:
            # Ensure any in progress editing the user is doing is present in the container
            self.boss.commit_all_editors_to_container()
            try:
                self.bolden_words(factor)
            except Exception:
                # Something bad happened report the error to the user
                import traceback
                error_dialog(self.gui, _('Failed to bolden words'), _(
                    'Failed to bolden words, click "Show details" for more info'),
                    det_msg=traceback.format_exc(), show=True)
                # Revert to the saved restore point
                self.boss.revert_requested(self.boss.global_undo.previous_container)
            else:
                # Show the user what changes we have made, allowing her to
                # revert them if necessary
                # no this is slow for giant books
                # self.boss.show_current_diff()


                # Update the editor UI to take into account all the changes we
                # have made
                self.boss.apply_container_update_to_gui()



    def bolden_words(self, factor):
        # Magnify all font sizes defined in the book by the specified factor
        # First we create a restore point so that the user can undo all changes
        # we make.
        self.boss.add_savepoint('Before: Magnify fonts')

        container = self.current_container  # The book being edited as a container object

        # Iterate over all HTML docs and process text nodes
        for name, media_type in container.mime_map.items():
            if media_type in OEB_DOCS:
                i = 0
                # A HTML file. Parsed HTML files are lxml elements
                for elem in container.parsed(name).xpath('//text()'):
                    #DEBUG
                    #i=i+1
                    #elem.getparent().set("lmao"+str(i), ""+str(elem.getparent().text))
                    #elem.getparent().set("lol"+str(i), ""+str(elem.getparent().tail))

                    parent = elem.getparent()
                    #parent.set("taggggg", parent.tag)
                    # don't ask me wwhy these are namespaced
                    parentTag = parent.tag.split("}")[1]
                    if (parentTag == "style" 
                    or parentTag == "title" 
                    or parentTag == "meta" 
                    or parentTag == "link"):
                        continue # dont mess with header stuff

                    nodetext = ""
                    if elem.is_text:
                        nodetext = parent.text
                    elif elem.is_tail:
                        nodetext = parent.tail
                    words = re.finditer(r"[\w]+", nodetext)

                    for w in reversed(list(words)):
                        lg = len(w.group(0))
                        boldend = math.ceil( lg * factor );

                        boldtext = nodetext[w.start(0):(w.start(0)+boldend)]
                        boldtail = nodetext[(w.start(0)+boldend):]
                        nodetext = nodetext[:w.start(0)]
                        newElem = etree.Element("b")
                        newElem.text = boldtext
                        newElem.tail = boldtail

                        if elem.is_text:
                            parent.text = nodetext
                            parent.insert(0, newElem)
                        elif elem.is_tail:
                            parent.insert(parent.getparent().index(parent), newElem)
                            parent.tail = nodetext
                    
                # container.parsed(name).xpath("bingusbingusbingus");
                container.dirty(name)
        
        