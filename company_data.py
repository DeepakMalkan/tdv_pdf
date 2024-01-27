
class CompanyData ():

    DETAILS_KEY = "DETAILS"
    DESCRIPTION_KEY = "DESCRIPTION"
    STAGE_FUNDING_KEY = "STAGE_FUNDING"
    TEAM_KEY = "TEAM"
    TECHNOLOGY_KEY = "TECHNOLOGY"
    MARKET_EXECUTION_KEY = "MARKET_EXECUTION"
    STRATEGIC_SYNERGIES = "STRATEGIC_SYNERGIES"

    def __init__(self, company_name, deal_type, file_key) -> None:
        self.company_name = company_name
        self.deal_type = deal_type
        self.file_key = file_key
        self.next_step = ""

        self.attributes_dict = {}

    def print (self):
        print (f"Company Name = {self.company_name}")
        print (f"   Deal Type = {self.deal_type}")
        # print (f"   File Key = {self.file_key}")
        # print (f"   Next Step = {self.next_step}")

        # for key in self.attributes_dict:
        #     print (f"  {key} = {self.attributes_dict[key]}")