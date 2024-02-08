import os.path
import apsw
import constants
from deals_section import DealsSection

class Phase1PdfData ():
    def __init__ (self, file_key, file_name, number_of_pages, deals_section_list):
        super ().__init__ ()
        self.file_key = file_key
        self.file_name = file_name
        self.number_of_pages = number_of_pages
        self.deals_section_list = deals_section_list

    def save_main_table (self, connection, table_name):
        query = f"insert into {table_name} values({self.file_key}, '{self.file_name}', {self.number_of_pages})"
        connection.execute (query)

    def save_deals_table (self, connection, table_name):
        for deals_section in self.deals_section_list:
            deals_section.save (connection, table_name, self.file_key)

    def save_pages_table (self, connection, table_name):
        for deals_section in self.deals_section_list:
            deals_section.save_deal_pages_header (connection, table_name, self.file_key)

    def save_blocks_table (self, connection, table_name):
        for deals_section in self.deals_section_list:
            deals_section.save_deal_pages_blocks (connection, table_name, self.file_key)

    def print (self):
        print (f"File Key = {self.file_key}")
        print (f"File Name = {self.file_name}")
        print (f"Number of Pages = {self.number_of_pages}")
        for deals_section in self.deals_section_list:
            deals_section.print ()

    def load (self, connection, file_key):
        # For each of the deal types, get the page-list associated with the deal
        for deal_type in constants.DEALS_LIST:
            deals_section = DealsSection (deal_type)
            deals_section.load (connection, file_key)
            self.deals_section_list.append (deals_section)

class Phase1Db ():
    """A class that processes Sqlite files .. for phase1"""
    """Use SQLite Viewer Web App - https://sqliteviewer.app/ - to quickly view Sqlite files"""

    @classmethod
    def generate_basepath_and_file_key (cls, path):
        '''The file-name contains a date that we need to extract for provenance purposes'''
        '''For example, the path's file name is for the format: "Bentley Biweekly 011222 vF.pdf". We need to extract 011222 in format mmddyy'''
        splitpath = path.rsplit ("/", 1)
        basepath = splitpath[1]
        extracted_date = basepath[17:23]
        yymmdd_date = extracted_date[4:6]+extracted_date[0:2]+extracted_date[2:4]
        return basepath, yymmdd_date

    def __init__ (self):
        super ().__init__ ()

    def save (self, phase1_pdf_data):
        if os.path.isfile (constants.PHASE1DB_PATH):
            connection = apsw.Connection (constants.PHASE1DB_PATH, flags = apsw.SQLITE_OPEN_READWRITE) # This connection simply opens a file
        else:
            connection = apsw.Connection (constants.PHASE1DB_PATH) # This connection creates the file
            query = f"create table {constants.PHASE1_TABLE_MAIN}({constants.FILE_KEY} TEXT NOT NULL PRIMARY KEY, {constants.FILE_NAME} TEXT, {constants.NUMBER_OF_PAGES} INTEGER)"
            connection.execute (query)
            query = f"create table {constants.PHASE1_TABLE_DEALS}({constants.FILE_KEY} TEXT NOT NULL, {constants.DEAL_TYPE} TEXT NOT NULL, {constants.NUMBER_OF_PAGES} INTEGER, {constants.PAGE_LIST} TEXT, primary key ({constants.FILE_KEY}, {constants.DEAL_TYPE}), FOREIGN KEY({constants.FILE_KEY}) REFERENCES {constants.PHASE1_TABLE_MAIN}({constants.FILE_KEY}))"
            connection.execute (query)
            query = f"create table {constants.PHASE1_TABLE_PAGES}({constants.FILE_KEY} TEXT NOT NULL, {constants.PAGE_INDEX} INTEGER, {constants.EXPECTED_FACTOR} INTEGER, {constants.NUMBER_OF_BLOCKS} INTEGER,  primary key ({constants.FILE_KEY}, {constants.PAGE_INDEX}), FOREIGN KEY({constants.FILE_KEY}) REFERENCES {constants.PHASE1_TABLE_MAIN}({constants.FILE_KEY}))"
            connection.execute (query)
            query = f"create table {constants.PHASE1_TABLE_BLOCKS}({constants.FILE_KEY} TEXT NOT NULL, {constants.PAGE_INDEX} INTEGER, {constants.BLOCK_INDEX} INTEGER, {constants.BLOCK_X0} REAL, {constants.BLOCK_Y0} REAL, {constants.BLOCK_X1} REAL, {constants.BLOCK_Y1} REAL, primary key ({constants.FILE_KEY}, {constants.PAGE_INDEX}, {constants.BLOCK_INDEX}), FOREIGN KEY({constants.FILE_KEY}) REFERENCES {constants.PHASE1_TABLE_MAIN}({constants.FILE_KEY}))"
            connection.execute (query)

        phase1_pdf_data.save_main_table (connection, constants.PHASE1_TABLE_MAIN)
        phase1_pdf_data.save_deals_table (connection, constants.PHASE1_TABLE_DEALS)
        phase1_pdf_data.save_pages_table (connection, constants.PHASE1_TABLE_PAGES)
        phase1_pdf_data.save_blocks_table (connection, constants.PHASE1_TABLE_BLOCKS)

        connection.close ()

    def load (self, file_key):
        """Load the data associated with a single PDF file (identified by file_key) in the Phase1 SQLITE file"""
        if os.path.isfile (constants.PHASE1DB_PATH) == False:
            return

        connection = apsw.Connection (constants.PHASE1DB_PATH, flags = apsw.SQLITE_OPEN_READONLY)
        cursor = connection.cursor ()

        # Locate the pdf file entry in PHASE1_TABLE_MAIN
        query = f"SELECT * from {constants.PHASE1_TABLE_MAIN} WHERE {constants.FILE_KEY} = {file_key}"
        cursor.execute (query)
        file_rows = cursor.fetchall ()

        file_count = len (file_rows)
        if file_count == 0:
            return

        # Make sure that we found only one entry for the PDF file.
        assert (file_count == 1)

        file_row = file_rows[0]
        phase1_pdf_data = Phase1PdfData (file_key, file_row[1], file_row[2], deals_section_list=[])
        phase1_pdf_data.load (connection, file_key)

        return phase1_pdf_data

    def dump (self):
        if os.path.isfile (constants.PHASE1DB_PATH) == False:
            return

        connection = apsw.Connection (constants.PHASE1DB_PATH, flags = apsw.SQLITE_OPEN_READONLY)
        cursor = connection.cursor ()

        query = f"SELECT * from {constants.PHASE1_TABLE_MAIN}"
        cursor.execute (query)
        file_rows = cursor.fetchall ()

        file_count = len (file_rows)
        for file_number in range (0, file_count):
            file_row = file_rows[file_number]
            file_key = file_row[0]
            file_name = file_row[1]
            number_of_pages = file_row[2]
            print (f"[{file_number}] Filekey = {file_key}, Filename = {file_name}, Number of Pages = {number_of_pages}")

            query = f"SELECT * from {constants.PHASE1_TABLE_DEALS} where {constants.FILE_KEY}={file_key}"
            cursor.execute (query)
            file_deals = cursor.fetchall ()

            deal_count = len (file_deals)
            if deal_count == 0:
                print ("No Deals found for file")
                continue

            for deal_number in range (0, deal_count):
                deal_row = file_deals[deal_number]
                deal_type = deal_row[1]
                number_of_pages = deal_row[2]
                page_list = deal_row[3]
                print (f"   Deal_type = {deal_type}, Number of Pages = {number_of_pages}, Page List = {page_list}")


class Phase2Db ():
    """A class that processes Sqlite files .. for phase2"""
    """Use SQLite Viewer Web App - https://sqliteviewer.app/ - to quickly view Sqlite files"""

    def __init__ (self):
        super ().__init__ ()

    def save (self, company_data):
        if os.path.isfile (constants.PHASE2DB_PATH):
            connection = apsw.Connection (constants.PHASE2DB_PATH, flags = apsw.SQLITE_OPEN_READWRITE) # This connection simply opens a file
        else:
            connection = apsw.Connection (constants.PHASE2DB_PATH) # This connection creates the file
            query = f"create table {constants.PHASE2_TABLE_COMPANY_MAIN}({constants.COMPANY_NAME} TEXT NOT NULL PRIMARY KEY)"
            connection.execute (query)
            query = f"create table {constants.PHASE2_TABLE_COMPANY_ATTRIBUTES}({constants.COMPANY_NAME} TEXT NOT NULL, {constants.ATTRIBUTE_NAME} TEXT NOT NULL, {constants.ATTRIBUTE_VALUE} TEXT, primary key ({constants.COMPANY_NAME}, {constants.ATTRIBUTE_NAME}), FOREIGN KEY({constants.COMPANY_NAME}) REFERENCES {constants.PHASE2_TABLE_COMPANY_MAIN}({constants.COMPANY_NAME}))"
            connection.execute (query)

        # First check if company entry exists
        cursor = connection.cursor ()
        query = f"SELECT * from {constants.PHASE2_TABLE_COMPANY_MAIN} where {constants.COMPANY_NAME}='{company_data.company_name}'"
        cursor.execute (query)
        company_rows = cursor.fetchall ()

        company_count = len (company_rows)

        # insert only if company entry does not exist
        if company_count == 0:
            query = f"insert into {constants.PHASE2_TABLE_COMPANY_MAIN} values('{company_data.company_name}')"
            connection.execute (query)

            for key in company_data.attributes_dict:
                query = f"insert into {constants.PHASE2_TABLE_COMPANY_ATTRIBUTES} values('{company_data.company_name}', '{key}', '{company_data.attributes_dict[key]}')"
                connection.execute (query)
        else:
            assert (company_count == 1)

        connection.close ()

"""Main entry point to test sqlite db data ."""
if __name__ == '__main__':
    phase1_db = Phase1Db ()
    phase1_db.dump ()