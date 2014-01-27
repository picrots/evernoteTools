from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore
import evernote.edam.type.ttypes as Types
dev_token = "S=s6:U=dd19a:E=14b2ab1fbc1:C=143d300cfc4:P=1cd:A=en-devtoken:V=2:H=f0e919bdeea319e8e35730eebb9e3ef2"
client = EvernoteClient(token=dev_token, sandbox=False)
notestore = client.get_note_store()

def getTodayTitle():
	return "Mon, 27 Jan 2014"

def createTodayNote():
	newNote = Types.Note()
	newNote.title = getTodayTitle()
	#	check if note already exist
	#
	notes = findNotes("intitle:" + newNote.title)

	#	create the note
	if not notes:
		notestore.createNote(newNote)
	else:
		print "There are " + str(len(notes)) + ' notes with the same title: "' + newNote.title + '"'

def findNotes(words):
	noteList = None
	#	it's important to set the time zone
	notefilter = NoteStore.NoteFilter(words=words, timeZone='Malaysia/Kuala_Lumpur')
	noteListObj = notestore.findNotes(notefilter, 0, 100)
	if noteListObj:
		noteList = noteListObj.notes

	return noteList
