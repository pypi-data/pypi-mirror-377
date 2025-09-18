class RequisiteCheckResult:
    def __init__(self, satisfied = False, met_condition = None, failed_condition = None):
        self.satisfied = satisfied
        self.met_conditions = []
        self.failed_conditions = []

        if met_condition is not None:
            self.met_conditions = [met_condition]
        
        if failed_condition is not None:
            self.failed_conditions = [failed_condition]

        