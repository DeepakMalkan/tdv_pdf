import os.path
import apsw

class DealsSection ():
    """A class that holds data associated with a section of pages - such as Priority Deals, New Deals, Other Deals, etc."""

    def __init__(self, description) -> None:
        self.description = description
        self.first_page = 0
        self.number_of_pages = 0
        self.page_list = []

    def print (self):
        print (f"Number of {self.description} Pages = {self.number_of_pages}")
        print (f"{self.description} Pages = {self.page_list}")

    def check_data (self):
        assert (self.number_of_pages == len (self.page_list))

class Phase1PdfData ():
    def __init__ (self, file_key, file_name, number_of_pages, priority_deals_section, new_deals_section, other_deals_section, activate_potential_section, commercial_partnership_section, pass_track_deals_section):
        super ().__init__ ()
        self.file_key = file_key
        self.file_name = file_name
        self.number_of_pages = number_of_pages
        self.priority_deals_section = priority_deals_section
        self.new_deals_section = new_deals_section
        self.other_deals_section = other_deals_section
        self.activate_potential_section = activate_potential_section
        self.commercial_partnership_section = commercial_partnership_section
        self.pass_track_deals_section = pass_track_deals_section

class Phase1Db ():
    """A class that processes Sqlite files .. for phase1"""
    """Use SQLite Viewer Web App - https://sqliteviewer.app/ - to quickly view Sqlite files"""

    def __init__ (self):
        super ().__init__ ()
        self.PATH ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/sqldb_phase1"
        self.PHASE1_TABLE = "phase1_table"
        self.PRIORITY_DEALS_TABLE = "priority_deals_table"
        self.NEW_DEALS_TABLE = "new_deals_table"
        self.OTHER_DEALS_TABLE = "other_deals_table"
        self.ACTIVATE_POTENTIAL_TABLE = "activate_potential_table"
        self.COMMERCIAL_PARTNERSHIP_TABLE = "commercial_partnership_table"
        self.PASS_TRACK_DEALS_TABLE = "pass_track_deals_table"
        self.FILE_KEY = "file_key"
        self.FILE_NAME = "file_name"
        self.NUMBER_OF_PAGES = "number_of_pages"
        self.PAGE_LIST = "pages"

    def save (self, phase1_row):
        if os.path.isfile (self.PATH):
            connection = apsw.Connection (self.PATH, flags = apsw.SQLITE_OPEN_READWRITE) # This connection simply opens a file
        else:
            connection = apsw.Connection (self.PATH) # This connection creates the file
            query = f"create table {self.PHASE1_TABLE}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.FILE_NAME} TEXT, {self.NUMBER_OF_PAGES} INTEGER)"
            connection.execute (query)
            query = f"create table {self.PRIORITY_DEALS_TABLE}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.NUMBER_OF_PAGES} INTEGER, {self.PAGE_LIST} TEXT)"
            connection.execute (query)
            query = f"create table {self.NEW_DEALS_TABLE}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.NUMBER_OF_PAGES} INTEGER, {self.PAGE_LIST} TEXT)"
            connection.execute (query)
            query = f"create table {self.OTHER_DEALS_TABLE}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.NUMBER_OF_PAGES} INTEGER, {self.PAGE_LIST} TEXT)"
            connection.execute (query)
            query = f"create table {self.ACTIVATE_POTENTIAL_TABLE}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.NUMBER_OF_PAGES} INTEGER, {self.PAGE_LIST} TEXT)"
            connection.execute (query)
            query = f"create table {self.COMMERCIAL_PARTNERSHIP_TABLE}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.NUMBER_OF_PAGES} INTEGER, {self.PAGE_LIST} TEXT)"
            connection.execute (query)
            query = f"create table {self.PASS_TRACK_DEALS_TABLE}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.NUMBER_OF_PAGES} INTEGER, {self.PAGE_LIST} TEXT)"
            connection.execute (query)

        query = f"insert into {self.PHASE1_TABLE} values({phase1_row.file_key}, '{phase1_row.file_name}', {phase1_row.number_of_pages})"
        connection.execute (query)

        if phase1_row.priority_deals_section.number_of_pages > 0:
            query = f"insert into {self.PRIORITY_DEALS_TABLE} values({phase1_row.file_key}, {phase1_row.priority_deals_section.number_of_pages}, '{str(phase1_row.priority_deals_section.page_list)}')"
            connection.execute (query)

        if phase1_row.new_deals_section.number_of_pages > 0:
            query = f"insert into {self.NEW_DEALS_TABLE} values({phase1_row.file_key}, {phase1_row.new_deals_section.number_of_pages}, '{str(phase1_row.new_deals_section.page_list)}')"
            connection.execute (query)

        if phase1_row.other_deals_section.number_of_pages > 0:
            query = f"insert into {self.OTHER_DEALS_TABLE} values({phase1_row.file_key}, {phase1_row.other_deals_section.number_of_pages}, '{str(phase1_row.other_deals_section.page_list)}')"
            connection.execute (query)

        if phase1_row.activate_potential_section.number_of_pages > 0:
            query = f"insert into {self.ACTIVATE_POTENTIAL_TABLE} values({phase1_row.file_key}, {phase1_row.activate_potential_section.number_of_pages}, '{str(phase1_row.activate_potential_section.page_list)}')"
            connection.execute (query)

        if phase1_row.commercial_partnership_section.number_of_pages > 0:
            query = f"insert into {self.COMMERCIAL_PARTNERSHIP_TABLE} values({phase1_row.file_key}, {phase1_row.commercial_partnership_section.number_of_pages}, '{str(phase1_row.commercial_partnership_section.page_list)}')"
            connection.execute (query)

        if phase1_row.pass_track_deals_section.number_of_pages > 0:
            query = f"insert into {self.PASS_TRACK_DEALS_TABLE} values({phase1_row.file_key}, {phase1_row.pass_track_deals_section.number_of_pages}, '{str(phase1_row.pass_track_deals_section.page_list)}')"
            connection.execute (query)

        connection.close ()

    def get_row (self, file_key):
        if os.path.isfile (self.PATH) == False:
            return

        connection = apsw.Connection (self.PATH, flags = apsw.SQLITE_OPEN_READ)

        query = f"SELECT {self.FILE_KEY} as file_key from {self.PHASE1TABLE} WHERE {self.FILE_KEY} = {file_key}"
        for row in connection.execute (query):
            print ("file_key", row.file_key)