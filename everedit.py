from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore
import evernote.edam.type.ttypes as Types
from datetime import date
dev_token = "S=s6:U=dd19a:E=14b2ab1fbc1:C=143d300cfc4:P=1cd:A=en-devtoken:V=2:H=f0e919bdeea319e8e35730eebb9e3ef2"
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
    notes = findNotes("intitle:" + newNote.title)

    #   create the note
    if not notes:
        #   get 'diary' notebook guid
        notebook = getNotebook('diary')
        if not notebook:
            print 'cannot fined notebook "Diary"'
            return
        newNote.notebookGuid = notebook.guid

        #   create the note
        notestore.createNote(newNote)
    else:
        print "There are " + str(len(notes)) + ' notes with the same title: "' + newNote.title + '"'

def findNotes(words):
    noteList = None
    #   it's important to set the time zone
    notefilter = NoteStore.NoteFilter(words=words, timeZone='Malaysia/Kuala_Lumpur')
    noteListObj = notestore.findNotes(notefilter, 0, 100)
    if noteListObj:
        noteList = noteListObj.notes

    return noteList
