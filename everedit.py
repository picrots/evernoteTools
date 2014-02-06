from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore
import evernote.edam.type.ttypes as Types
from datetime import date
from bs4 import BeautifulSoup
import os
import re

dev_token = "your dev token"

# Get dev_token from file
varFileLocation = os.path.join(os.path.dirname(__file__), 'var.py')
if os.path.exists(varFileLocation):
    from evernoteTools import var
    dev_token = var.id

print "Connection to evernote..."
client = EvernoteClient(token=dev_token, sandbox=False)
notestore = client.get_note_store()

#   global variables
notebookCache = {}


def getTodayTitle():
    today = date.today()
    date_string = today.strftime("%a, %d %b %Y")  # 'Sun, 15 Dec 2013'
    return date_string


def getNotebook(notebookName, resetCache=False):
    global notebookCache

    #   lowercase the notebook request
    notebookName = notebookName.lower()

    #   try to get notebook from cache first
    if notebookName in notebookCache and not resetCache:
        return notebookCache[notebookName]

    #   get notebook list from evernote and add them to cache
    requeestedNotebook = None
    notebookList = notestore.listNotebooks()

    for notebook in notebookList:
        #   adding to cache
        notebookCache.setdefault(notebook.name.lower(), notebook)
        if notebook.name.lower() == notebookName:
            requeestedNotebook = notebook
    return requeestedNotebook


def createTodayNote():
    newNote = Types.Note()
    newNote.title = getTodayTitle()

    #   check if note already exist
    #
    notes = findNotes('intitle:"' + newNote.title + '"')

    #   create the note
    if not notes:
        #   get 'diary' notebook guid
        notebook = getNotebook('diary')
        if not notebook:
            print 'cannot fined notebook "Diary"'
            return
        newNote.notebookGuid = notebook.guid

        #   create the note
        print 'Creating note "' + newNote.title + '" ...'
        notestore.createNote(newNote)
    else:
        print ("There are " + str(len(notes)) + ' notes with the same title: "'
               + newNote.title + '"')


def findNotes(words):
    noteList = None
    #   it's important to set the time zone
    notefilter = NoteStore.NoteFilter(
        words=words, timeZone='Malaysia/Kuala_Lumpur')

    noteListObj = notestore.findNotes(notefilter, 0, 100)
    if noteListObj:
        noteList = noteListObj.notes

    return noteList


def getNoteContentByGuid(guid):
    return notestore.getNoteContent(guid, 1, 0, 0, 0)


def styleNote(noteObj):
    #   getting content of the note
    #
    print '\nStyling note "' + noteObj.title + '" with guid ' + noteObj.guid
    print 'Fetching note contents ...'
    content = getNoteContentByGuid(noteObj.guid)

    #   styling
    #
    print 'Styling ...'
    soup = BeautifulSoup(content, "xml")
    #   style headers
    h1_list = soup.findAll('h1')
    h2_list = soup.findAll('h2')
    h3_list = soup.findAll('h3')
    address_list = soup.findAll('address')

    h1_style = "font-family:Calibri;font-size:16.0pt;color:#1E4E79"
    h2_style = "font-family:Calibri;font-size:14.0pt;color:#2E75B5"
    h3_style = "font-family:Calibri;font-size:12.0pt;color:#5B9BD5"
    address_style = "margin-left: 30px;font-family: 'courier new', \
                     courier, monospace;"

    for h1 in h1_list:
        h1['style'] = h1_style
    for h2 in h2_list:
        h2['style'] = h2_style
    for h3 in h3_list:
        h3['style'] = h3_style
    for add in address_list:
        add['style'] = address_style
        add.wrap(soup.new_tag("div"))
        add.append(soup.new_tag('br', clear="none"))
        add.name = 'span'

    #   codes highlighting
    #
    # while(soup.address):
    #     #   find lines of code belongs to same snippet.
    #     done = 0
    #     currentAddressTag = soup.address
    #     backToBackTagList = [soup.address]
    #     while not done:
    #         nextTag = currentAddressTag.nextSibling
    #         if not nextTag or nextTag.name != 'address':
    #             done = 1
    #             continue
    #         currentAddressTag = nextTag
    #         backToBackTagList.append(nextTag)

    #     #   combine lines under one span tag
    #     code = ""
    #     for i, addressTag in enumerate(backToBackTagList):
    #         code += addressTag.string + '\n'
    #         if i > 0:
    #             addressTag.extract()
    #     #   highlight the code
    #     code = highlight(code, PythonLexer(), HtmlFormatter(noclasses=True))
    #     #   add all lines to the first address tag
    #     backToBackTagList[0].clear()
    #     s = BeautifulSoup(code)
    #     backToBackTagList[0].append(s.div)
    #     backToBackTagList[0].name = 'span'

    #   update note
    #
    newContent = soup.renderContents()
    #   remove any class attribute
    noteObj.content = re.sub('class=".*?" ', '', newContent)
    print 'Updating ...'
    if noteObj.content != content:
        notestore.updateNote(noteObj)
    else:
        print "No Changes to the note!"
    print "Done."


def styleRecentNotes(dateTerm="today"):
    print "Search for list of recent notes ..."
    noteList = findNotes("updated:" + str(dateTerm))
    for note in noteList:
        styleNote(note)


def styleTodayNote():
    title = getTodayTitle()
    noteList = findNotes("intitle:" + str(title))
    if noteList:
        note = noteList[0]
        styleNote(note)
