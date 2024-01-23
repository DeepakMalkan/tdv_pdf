import os.path
import apsw

class DealsSection ():
    """A class that holds data associated with a section of pages - such as Priority Deals, New Deals, Other Deals, etc."""

    def __init__(self, deal_type) -> None:
        self.deal_type = deal_type
        self.first_page = 0
        self.number_of_pages = 0
        self.page_list = []

    def save (self, connection, table_name, file_key):
        if self.number_of_pages > 0:
            query = f"insert into {table_name} values({file_key}, '{self.deal_type}', {self.number_of_pages}, '{str(self.page_list)}')"
            connection.execute (query)

    def print (self):
        print (f"Number of {self.deal_type} Pages = {self.number_of_pages}")
        print (f"{self.deal_type} Pages = {self.page_list}")

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
        self.PHASE1_TABLE_MAIN = "phase1_table_main"
        self.PHASE1_TABLE_DEALS = "phase1_table_deals"
        self.FILE_KEY = "file_key"
        self.FILE_NAME = "file_name"
        self.DEAL_TYPE = "deal_type"
        self.NUMBER_OF_PAGES = "number_of_pages"
        self.PAGE_LIST = "pages"

    def save (self, phase1_pdf_data):
        if os.path.isfile (self.PATH):
            connection = apsw.Connection (self.PATH, flags = apsw.SQLITE_OPEN_READWRITE) # This connection simply opens a file
        else:
            connection = apsw.Connection (self.PATH) # This connection creates the file
            query = f"create table {self.PHASE1_TABLE_MAIN}({self.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {self.FILE_NAME} TEXT, {self.NUMBER_OF_PAGES} INTEGER)"
            connection.execute (query)
            query = f"create table {self.PHASE1_TABLE_DEALS}({self.FILE_KEY} TEXT NOT NULL, {self.DEAL_TYPE} TEXT NOT NULL, {self.NUMBER_OF_PAGES} INTEGER, {self.PAGE_LIST} TEXT, primary key ({self.FILE_KEY}, {self.DEAL_TYPE}), FOREIGN KEY({self.FILE_KEY}) REFERENCES {self.PHASE1_TABLE_MAIN}({self.FILE_KEY}))"
            connection.execute (query)

        query = f"insert into {self.PHASE1_TABLE_MAIN} values({phase1_pdf_data.file_key}, '{phase1_pdf_data.file_name}', {phase1_pdf_data.number_of_pages})"
        connection.execute (query)

        phase1_pdf_data.priority_deals_section.save (connection, self.PHASE1_TABLE_DEALS, phase1_pdf_data.file_key)
        phase1_pdf_data.new_deals_section.save (connection, self.PHASE1_TABLE_DEALS, phase1_pdf_data.file_key)
        phase1_pdf_data.other_deals_section.save (connection, self.PHASE1_TABLE_DEALS, phase1_pdf_data.file_key)
        phase1_pdf_data.activate_potential_section.save (connection, self.PHASE1_TABLE_DEALS, phase1_pdf_data.file_key)
        phase1_pdf_data.commercial_partnership_section.save (connection, self.PHASE1_TABLE_DEALS, phase1_pdf_data.file_key)
        phase1_pdf_data.pass_track_deals_section.save (connection, self.PHASE1_TABLE_DEALS, phase1_pdf_data.file_key)

        connection.close ()

    def get_row (self, file_key):
        if os.path.isfile (self.PATH) == False:
            return

        connection = apsw.Connection (self.PATH, flags = apsw.SQLITE_OPEN_READ)

        query = f"SELECT {self.FILE_KEY} as file_key from {self.PHASE1TABLE} WHERE {self.FILE_KEY} = {file_key}"
        for row in connection.execute (query):
            print ("file_key", row.file_key)