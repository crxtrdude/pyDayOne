#!/usr/bin/env python

# pyJournalLer_Editor.py
# Day One Journal editor for Python-supported OSes.
# ----------------------------------------
# Originally Made By - Nitin Khanna (based on pyDayOne)
# Modifications & fixes - Clinton Canalita
#
# requires pyGtk and lxml
# GNU GPL License. Have fun! 

import pygtk
pygtk.require('2.0')
import gtk, gobject
import pango
import os
import getpass
import platform
import datetime
import uuid
import re
import xml.dom.minidom as miDom
import lxml.etree as ET
import sys
import shutil
import pylzma

#os.environ['PATH'] += ";gtk/lib;gtk/bin"

class pyDayOneGTK:
        the_dict = {}
        uuid_dict = {}                  # holds all the UUIDs with timestamps as keys
        the_list = []                   # stores the timestamps as keys to show in the GUI CList
        sorted_dict = {}                # stores the entries with the timestamps as keys
        starred_dict = {}
        found_entry = False
        found_UUID = False
        found_starred = False
        myUUID = ''
        timestamp = ''
        sealedLetter = ''
        
        nofile_flag = False
        is_open = False                 # is the journal file open/initialized?
        
        directory = ''                  # the entries directory
        directory_journal = ''          # the .journal directory
        app_directory = ''              # the directory of THIS application

        #the SAVE FILE to re-open the journal again.
        savefile = open('JournalLer.sav', 'w+')

        is_entry_starred = False        #flag for starring

#---------------------------START OF PROGRAM------------------------------------

        def empty_file_scan(self):
                for root,dirs,files in os.walk(self.directory):
                        for file in files:
                                print file
                                if file.endswith(".doentry") and file == ".doentry":
                                        os.remove(self.directory+'\\'+file)
                                elif file.endswith(".doentry"):
                                        tree = ET.parse(self.directory+'\\'+file)
                                        root = tree.getroot()
                                        for child in root[0]:
                                                #print child.tag, child.text
                                                if child.text == 'Entry Text':
                                                        self.found_entry = True
                                                if child.tag == 'string' and self.found_entry:
                                                        file_content = child.text
                                                        self.found_entry = False
                                                        if file_content == "":
                                                                os.remove(self.directory+'\\'+file)
        
        def close_application(self, widget, data=None):
                if self.is_open == True:
                        print "Performing auto-save"
                        self.label.set_text("Auto-Saving")
                        self.save_journal()
                        "Now scanning for empty files..."
                        self.empty_file_scan()
                        
                print "\n\nGOODBYE! And thanks for using."
                gtk.main_quit()
                return False

        def reset(self):
                self.label.set_text("")

#command for cList row selection

        def selection_made(self, clist, row, column, event, data=None):
                # Get the text that is stored in the selected row and column
                # which was clicked in. We will receive it as a pointer in the
                # argument text.
                self.timestamp = self.entryList.get_pixtext(row, column)
                self.myUUID = self.uuid_dict[self.timestamp]
                self.sealedLetter = self.sorted_dict[self.timestamp]
                #print self.sealedLetter
                if self.sealedLetter == None:
                        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                        message.set_markup("There is nothing to see in this entry.\n\n You can though type in this entry and save it.")
                        response = message.run()
                        message.destroy()
                        self.textbuffer.delete(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter())
                else:
                        self.textbuffer.set_text(self.sealedLetter)
                #print self.sorted_dict[self.timestamp]
                print self.myUUID

                # Just prints some information about the selected row
                print ("You selected row %d and the text is %s\n" % (row, self.timestamp))
        
                print (str(self.starred_dict[self.timestamp]))
                self.checkStarred.set_active(self.starred_dict[self.timestamp])
                return

#command to create a new file

        def selected_new(self):
                now = datetime.datetime.utcnow()
                theUUID = uuid.uuid4()
                modUUID = re.sub('[-]', '', str(theUUID))
                self.myUUID = modUUID.swapcase()
                print self.myUUID
                item = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                print item
                pos = 0
                self.textbuffer.delete(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter())
                self.sorted_dict[item] = ""
                self.uuid_dict[item] = self.myUUID
                self.starred_dict[item] = False
                self.entryList.insert(pos, [item])
                self.entryList.select_row(0,0)
                self.checkStarred.set_active(self.starred_dict[item])
                print "New entry is not starred."

#commands for the GUI buttons

        def selected_open_journal (self):
                self.nofile_flag = False
                self.open_journal()
                if self.nofile_flag == False:
                        for index, item in enumerate(self.the_list):
                                self.entryList.append([item])

                        self.buttonOpen.destroy()
                        self.main_buttons()
                        self.label.set_text("Journal opened sucessfully.")
                        gobject.timeout_add_seconds(3, self.reset)

        def selected_save_journal (self, widget):
                self.label.set_text("Saving")
                self.save_journal()

        def main_buttons (self):

                image = gtk.Image()
                image.set_from_file("res\\img\\new_entry.png")
                image.show()
                newButton = gtk.Button()
                newButton.add(image)
                newButton.connect("clicked", self.button1_exec)
                self.Holder.attach(newButton, 0, 1, 1, 2)
                newButton.show()

                image = gtk.Image()
                image.set_from_file("res\\img\\save_entry.png")
                image.show()
                saveButton = gtk.Button()
                saveButton.add(image)
                saveButton.connect("clicked", self.selected_save_journal)
                self.Holder.attach(saveButton, 1, 2, 1, 2)
                saveButton.show()

                image = gtk.Image()
                image.set_from_file("res\\img\\delete_entry.png")
                image.show()
                deleteButton = gtk.Button()
                deleteButton.add(image)
                deleteButton.connect("clicked", self.deleteEntry)
                self.Holder.attach(deleteButton, 2, 3, 1, 2)
                deleteButton.show()

                self.checkStarred.show()

        def starred_active (self, widget, checkbox):
                self.is_entry_starred = self.checkStarred.get_active()
                if self.is_entry_starred:
                        self.starred_dict[self.timestamp] = True
                        print "This entry is starred"
                else:
                        self.starred_dict[self.timestamp] = False
                        print "This entry is unstarred"
                return

        def button1_exec (self, widget):
                if self.is_open == True:
                        self.selected_new()
                else:
                        self.selected_open_journal()
                
#command to strip hash tags from text into a python set for tag placement in XML

        def extract_hash_tags(self, text):
                return set(part[1:] for part in text.split() if part.startswith('#'))

#save commands

        def save_journal(self):
                try:
                        with open(self.directory+'\\'+self.myUUID+'.doentry', 'w+') as f:
                                #print "came in with"
                                #f.close()
                                tree = ET.parse(self.directory+'\\'+self.myUUID+'.doentry')
                                #print "tree parse began"
                                root = tree.getroot()
                                if child.text == 'Entry Text':
                                        self.found_entry = True
                                if child.tag == 'string' and self.found_entry:
                                        child.text = self.textbuffer.get_text(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter())
                                        self.found_entry = False
                                tree.write(self.directory+'\\'+self.myUUID+'.doentry')
                except:
                        self.uuid_dict[self.timestamp] = self.myUUID
                        self.sorted_dict[self.timestamp] = self.textbuffer.get_text(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter())
                        #print self.textbuffer.get_text(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter())

                        plist = ET.Element('plist')
                        plist.attrib['version'] = "1.0"
                        b = ET.SubElement(plist, 'dict')
                        
                        c = ET.SubElement(b, 'key')
                        c.text = 'Creation Date'
                        d = ET.SubElement(b, 'date')
                        d.text = str(self.timestamp)
                                
                        e = ET.SubElement(b, 'key')
                        e.text = 'Entry Text'
                        f = ET.SubElement(b, 'string')
                        ftags = self.textbuffer.get_text(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter())
                        f.text = ftags
                                
                        g = ET.SubElement(b, 'key')
                        g.text = 'Starred'
                        if str(self.starred_dict[self.timestamp]) != '':
                                self.is_entry_starred = self.starred_dict[self.timestamp]
                                if self.is_entry_starred:
                                        h = ET.SubElement(b, 'true')
                                else:
                                        h = ET.SubElement(b, 'false')


                        i = ET.SubElement(b, 'key')
                        i.text = "Tags"
                        j = ET.SubElement(b, 'array')
                        pHashtags = self.extract_hash_tags(ftags)
                        print pHashtags
                        for hashNum in pHashtags:
                                string = ET.SubElement(j, 'string')
                                string.text = hashNum
                        
                        k = ET.SubElement(b, 'key')
                        k.text = 'UUID'
                        l = ET.SubElement(b, 'string')
                        l.text = self.myUUID

                        #for evaluation of the XML written
                        #print (ET.tostring(plist, encoding="UTF-8", xml_declaration=True, pretty_print=True, doctype='<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'))
                        file = open(self.directory+'\\'+self.myUUID+'.doentry', 'w')
                        file.write(ET.tostring(plist, encoding="UTF-8", xml_declaration=True, pretty_print=True, doctype='<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'))
                        
                self.label.set_text("Saved")
                gobject.timeout_add_seconds(3, self.reset)

#open commands

        def open_journal (self):
                if platform.system() == 'Windows':
                        #print "system is windows"
                        directory = 'C:\\Users\\'+getpass.getuser()+'\\Dropbox\\Apps\\Day One\\Journal.dayone\\'
                        if os.path.exists(directory):
                                self.directory = directory
                        else:
                                message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                                message.set_markup("Day One Journal not found.\n\n Please select the entries directory of Day One. It should be under Dropbox -> Apps -> Day One -> Journal.dayone -> entries")
                                response = message.run()
                                message.destroy()
                                
                                dialog = gtk.FileChooserDialog("Choose journal directory:", action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
                                response = dialog.run()
                                if response == gtk.RESPONSE_OK:
                                        #print dialog.get_current_folder(), 'selected'
                                        self.directory = dialog.get_current_folder()
                                        
                                elif response == gtk.RESPONSE_CANCEL:
                                        #print 'Closed, no files selected'
                                        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                                        message.set_markup("No folder was selected. I can't work like this!")
                                        response = message.run()
                                        message.destroy()
                                        if self.nofile_flag != True:
                                                self.nofile_flag = True
                                dialog.destroy()
                else:
                        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                        message.set_markup("Day One Journal not found.\n\n Please select the entries directory of Day One. It should be under Dropbox -> Apps -> Day One -> Journal.dayone -> entries")
                        response = message.run()
                        
                        dialog = gtk.FileChooserDialog("Choose journal directory:", action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
                                
                        response = dialog.run()
                        if response == gtk.RESPONSE_OK:
                                #print dialog.get_current_folder(), 'selected'
                                self.directory = dialog.get_current_folder()
                                
                        elif response == gtk.RESPONSE_CANCEL:
                                #print 'Closed, no files selected'
                                message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                                message.set_markup("No folder was selected. I can't work like this!")
                                response = message.run()
                                message.destroy()
                                if self.nofile_flag != True:
                                        self.nofile_flag = True
                        dialog.destroy()
                        
                if self.nofile_flag == False:
                        #makes the main .journal folder (for pictures)
                        self.directory_journal = re.sub(r'\\entries', '', self.directory, flags=re.IGNORECASE)
                        #to make sure that the above re.sub is done!
                        print self.directory_journal
                        dir = ET.Element('directory')
                        dir.text = self.directory_journal
                        ET.ElementTree(dir).write(self.savefile)
                        
                        self.is_open = True
                        self.reset_journal_list()
                        
                return

#command to reset the journal clist

        def reset_journal_list (self):
                for root,dirs,files in os.walk(self.directory):
                        for file in files:
                                print file
                                if file.endswith(".doentry") and file == ".doentry":
                                        os.remove(self.directory+'\\'+file)
                                elif file.endswith(".doentry"):
                                        tree = ET.parse(self.directory+'\\'+file)
                                        root = tree.getroot()
                                        for child in root[0]:
                                                #print child.tag, child.text
                                                
                                                if child.tag == 'date':
                                                        tempdate = child.text
                                                if child.text == 'Entry Text':
                                                        self.found_entry = True
                                                if child.text == 'UUID':
                                                        self.found_UUID = True
                                                if child.text == 'Starred':
                                                        self.found_starred = True
                                                
                                                if child.tag == 'string' and self.found_UUID and tempdate != '':
                                                        self.uuid_dict[tempdate] = child.text
                                                        self.found_UUID = False
                                                if child.tag == 'string' and self.found_entry and tempdate != '':
                                                        self.the_dict[tempdate] = child.text
                                                        self.found_entry = False
                                                if child.tag == 'false' and self.found_starred and tempdate != '':
                                                        self.starred_dict[tempdate] = False
                                                        self.found_starred = False
                                                if child.tag == 'true' and self.found_starred and tempdate != '':
                                                        self.starred_dict[tempdate] = True
                                                        self.found_starred = False
                                        
                keylist = self.the_dict.keys()
                keylist.sort(reverse=True)
                
                for key in keylist:
                        self.sorted_dict[key] = self.the_dict[key]
                        self.the_list.append(key)

        def deleteEntry(self, widget):
                messageDelete = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_YES_NO)
                messageDelete.set_markup("Are you sure you want to delete this journal entry?\n\nThis could not be undone.")
                responseDelete = messageDelete.run()
                if responseDelete == gtk.RESPONSE_YES:
                        sourceCopy = self.directory+'\\'+self.myUUID+'.doentry'
                        destFolder = self.app_directory+'\\backup\\'
                        if not os.path.exists(destFolder): os.makedirs(destFolder)
                        shutil.copy2(sourceCopy, destFolder+self.myUUID+'.dobak')
                        os.remove(sourceCopy)
                        messageDelete.destroy()
                elif responseDelete == gtk.RESPONSE_NO:
                        messageDelete.destroy()
                        return
                self.entryList.clear()
                self.textbuffer.delete(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter())
                for index, item in enumerate(self.the_list):
                        self.entryList.append([item])
                
#begin the program

        def __init__(self):
                #set-up images for GUI here.
                pathStep = os.path.dirname(sys.argv[0])
                self.app_directory = os.path.abspath(pathStep) 
                
                try:
                        tree = ET.parse(self.savefile)
                        root = tree.getroot()
                        self.directory = root.text + "\\entries"
                except:
                        #print "savefile not found"
                        #print platform.system()
                        self.open_journal()

                # for index, item in enumerate(self.the_list):
                #       print index, item

                window = gtk.Window(gtk.WINDOW_TOPLEVEL)
                window.set_resizable(False)
                window.connect("destroy", self.close_application)
                window.set_title("pyJournalLer")
                window.set_border_width(0)
                window.set_default_size(640, 512)
                window.set_icon_from_file('res\\img\\Editor.png')

                box1 = gtk.VBox(False, 0)
                window.add(box1)
                box1.show()

                box2 = gtk.HBox(False, 10)
                box2.set_border_width(10)
                box1.pack_start(box2, True, True, 0)
                box2.show()

                sw1 = gtk.ScrolledWindow()
                sw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                sw1.set_size_request(140,480)
                
                title = ["Entries"]
                self.entryList = gtk.CList( 1, title)
                self.entryList.connect("select_row", self.selection_made)
                self.entryList.set_selection_mode(gtk.SELECTION_SINGLE)
                self.entryList.set_shadow_type(gtk.SHADOW_OUT)
                self.entryList.set_column_width(0, 50)
                
                sw1.add(self.entryList)
                sw1.show()
                self.entryList.show()
                box2.pack_start(sw1)

                sw2 = gtk.ScrolledWindow()
                sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                sw2.set_size_request(470,480)
                
                self.textbuffer = gtk.TextBuffer()
                textview = gtk.TextView(self.textbuffer)
                textview.set_wrap_mode(gtk.WRAP_WORD)
                textview.modify_font(pango.FontDescription("monospace 11"))
                #textbuffer = textview.get_buffer()
                sw2.add(textview)
                sw2.show()
                textview.show()
                box2.pack_start(sw2)
                
                separator = gtk.HSeparator()
                box1.pack_start(separator, False, True, 0)
                separator.show()
                
                self.Holder = gtk.Table(1, 2, True)
                box1.pack_start(self.Holder, False, True, 0)

                self.checkStarred = gtk.CheckButton("Star this entry")
                self.checkStarred.connect("toggled", self.starred_active, self.checkStarred)
                self.Holder.attach(self.checkStarred, 0, 1, 0, 1)

                self.label = gtk.Label('')
                self.label.set_justify(gtk.JUSTIFY_RIGHT)
                self.Holder.attach(self.label, 1, 3, 0, 1)
                self.label.show()

                self.buttonOpen = gtk.Button('Open Journal')
                self.buttonOpen.connect("clicked", self.button1_exec)
                self.Holder.attach(self.buttonOpen, 0, 1, 1, 2)
                
                if self.nofile_flag == False:
                        self.buttonOpen.destroy()
                        self.main_buttons()
                else:
                        self.buttonOpen.show()

                self.Holder.show()
                window.show()

                if self.nofile_flag == True:
                        self.label.set_text("No journal file found.")
                        gobject.timeout_add_seconds(3, self.reset)
                else:
                        self.label.set_text("Journal opened sucessfully.")
                        gobject.timeout_add_seconds(3, self.reset)

                file_name = "res\\img\\star.png"
                pixbuf = gtk.gdk.pixbuf_new_from_file(file_name)
                print file_name
                self.starPixmap = pixbuf.render_pixmap_and_mask()

                file_name = "res\\img\\star_no.png"
                pixbuf2 = gtk.gdk.pixbuf_new_from_file(file_name)
                print file_name
                self.blankPixmap = pixbuf2.render_pixmap_and_mask()
                
                for index, item in enumerate(self.the_list):
                        #print item
                        self.entryList.append(" ")
                        if self.starred_dict[item]:
                                self.entryList.set_pixtext(index, 0, str([item]), 4, self.starPixmap)
                        else:
                                self.entryList.set_pixtext(index, 0, str([item]), 4, self.blankPixmap)
                        #self.entryList.insert(index, item)
                        #print self.entryList.get_pixtext(index, 0)
                        
                self.entryList.select_row(0,0)

def main():
        gtk.main()
        return 0

if __name__ == "__main__":
        pyDayOneGTK()
        main()
