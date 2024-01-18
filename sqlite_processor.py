import os.path
import apsw

class SqliteProcessor ():
    """A class that processes Sqlite files .. for different phases"""
    """Use SQLite Viewer Web App - https://sqliteviewer.app/ - to quickly view Sqlite files"""

    def __init__ (self):
        super ().__init__ ()

    def savePhase1 (self, file_key, file_name, number_of_pages, priority_deals_number_of_pages, priority_deals_page_list, new_deals_number_of_pages, new_deals_page_list):
        path ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/sqldb"
        phase1table = "phase1table"

        if os.path.isfile (path):
            connection = apsw.Connection (path, flags = apsw.SQLITE_OPEN_READWRITE)
        else:
            connection = apsw.Connection (path)
            query = f"create table {phase1table}(file_key TEXT NOT NULL PRIMARY KEY, file_name TEXT, number_of_pages INTEGER, priority_deals_number_of_pages INTEGER, priority_deals_pages TEXT, new_deals_number_of_pages INTEGER, new_deals_pages TEXT)"
            connection.execute (query)

        query = f"insert into {phase1table} values({file_key}, '{file_name}', {number_of_pages}, {priority_deals_number_of_pages}, '{str(priority_deals_page_list)}', {new_deals_number_of_pages}, '{str(new_deals_page_list)}')"
        connection.execute (query)
