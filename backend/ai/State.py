class State:
    def __init__(self):
        self.question = ""
        self.pruned_tables_columns = {}
        self.database_schema = {}
        self.is_relevant = False
        self.sql_issues = []
        self.sql_query = ""
        self.results = []
        self.formatted_data = {}