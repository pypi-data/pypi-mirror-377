import re
from requisite_processor.requisite_check import RequisiteCheckResult

class RequisiteProcessor:
    def __init__(self, prerequisites: dict):
        self.prerequisite_rules = prerequisites

    @property
    def availabile_academic_periods(self) -> list[str]:
        """Returns a list of all academic periods in the provided prerequiste data.

        Returns:
            list[str]: List of academic period strings. Ex: ['202310', '202380']
        """
        return self.prerequisite_rules.keys()


    @property
    def latest_available_academic_period(self) -> str:
        """Returns the most recent academic period of the periods in the given prerequisite data.

        Returns:
            str: Academic period string. Ex: '202310'
        """
        available = list(map(int, self.availabile_academic_periods))
        available.sort()
        return str(available[-1])


    def check_satisfaction(
            self,
            course_code: str,
            courses_taken: list[dict] = None,
            test_scores = None,
            academic_period = None,
            ignore_tests = False,
            ignore_grades = False
        ) -> RequisiteCheckResult:
        """Determines if a list of courses and test scores meets the prerequisite
        requirements for a given course in a given academic period.

        Args:
            course_code (str): The code of the course to check prerequisite satisfaction for. Ex: 'MATH 1512'

            courses_taken (list[dict], optional): A list of course and grade information. Each entry
             should be a dictionary with a code and grade key. Ex: [{ 'code': 'MATH 1512', 'grade': 'A-'}]. Defaults to [].

            test_scores (dict, optional): A dictionary with test score information. Each key of the dictionary should be a
             test code where the value is the score for the associated test. Ex: { 'A01': 27 }. Defaults to {}.

            academic_period (_type_, optional): The academic period to pull prerequisites from. Defaults to the latest academic period in the
            requirement infomation.

            ignore_tests (bool, optional): Setting to True will ignore test requirements when checking for
            satisfaction. Defaults to False.

            ignore_grades (bool, optional): Setting to true will ingore grade requirements and will consider
            any grade as acceptable. Defaults to False.

        Raises:
            AcademicPeriodNotFound: Raised when the given academic period is not present in the given prerequisite data.
            CourseNotFound: Raised when the given course is not found within in the given academic period.

        Returns:
            RequisiteCheckResult: Object that includes result of the check.
        """

        if courses_taken is None:
            courses_taken = []

        if academic_period is None:
            academic_period = self.latest_available_academic_period

        if academic_period not in self.prerequisite_rules:
            raise self.AcademicPeriodNotFound(f"The academic period '{academic_period}' is not found in the given prerequisite data.")

        if course_code not in self.prerequisite_rules[academic_period]:
            raise self.CourseNotFound(f"Course {course_code} not found in {academic_period}")

        prereq_rule = self.prerequisite_rules[academic_period][course_code]

        if ignore_tests is True:
            prereq_rule = self.__reduce_rule(prereq_rule, lambda x: x['type'] in ['and', 'or', 'course'])

        if prereq_rule is None:
            return RequisiteCheckResult(True)

        return self.__traverse_prereqs(prereq_rule, academic_period, courses_taken, test_scores, ignore_grades)


    def __grade_score(self, grade) -> float:
        grades = {
            'A+': 4.3, 'A': 4, 'A-': 3.7,
            'B+': 3.3, 'B': 3, 'B-': 2.7,
            'C+': 2.3, 'C': 2, 'C-': 2,
            'CR': 2,
            'D+': 1.7, 'D': 1, 'D-': 0.7,
            'F': 0
        }

        processed_grade = re.sub('(T|X|R|\\*)', '', grade)
        return grades.get(processed_grade, 0)


    def __traverse_prereqs(self, prereq_data: dict, academic_period, courses_taken, test_scores, ignore_grades):
        if prereq_data['type'] == 'course':
            selected_course = None
            for course in courses_taken:
                if course['code'] == prereq_data['course']['code'] and (ignore_grades is True or self.__grade_score(course['grade']) >= self.__grade_score(prereq_data['minimum_course_grade'])):
                    selected_course = course
                    break

            if selected_course is not None:
                return RequisiteCheckResult(True, met_condition = { 'type': 'course', 'code': selected_course['code'] })
            else:
                return RequisiteCheckResult(False, failed_condition = { 'type': 'course', 'code': prereq_data['course']['code'] })

        if prereq_data['type'] == 'placement_test':
            test_code = prereq_data['placement_test']['test_code']
            if test_code not in test_scores:
                return RequisiteCheckResult(False, failed_condition = { 'type': 'placement_test', 'code': test_code, 'score': prereq_data['minimum_test_score'] })

            if test_scores[test_code] >= prereq_data['minimum_test_score']:
                return RequisiteCheckResult(True, met_condition = { 'type': 'placement_test', 'score': prereq_data['minimum_test_score'],  'code': test_code })
            else:
                return RequisiteCheckResult(False, failed_condition = { 'type': 'placement_test', 'score': prereq_data['minimum_test_score'], 'code': test_code })


        if prereq_data['type'] == 'and':
            prereq_operands = []
            for sub_prereq_data in prereq_data['operands']:
                if sub_prereq_data['type'] == 'course' and sub_prereq_data['concurrency_ind'] == True:
                    continue
                prereq_operands.append(sub_prereq_data)

            if len(prereq_operands) == 0:
                return RequisiteCheckResult(True)

            results = []
            for sub_prereq_data in prereq_operands:
                results.append(self.__traverse_prereqs(sub_prereq_data, academic_period, courses_taken, test_scores, ignore_grades))

            result = RequisiteCheckResult(True)
            for r in results:
                if r is None:
                    continue

                result.satisfied = r.satisfied and result.satisfied
                if r.satisfied:
                    result.met_conditions = result.met_conditions + r.met_conditions

                result.failed_conditions = result.failed_conditions + r.failed_conditions

            return result

        if prereq_data['type'] == 'or':
            prereq_operands = []

            for sub_prereq_data in prereq_data['operands']:
                if sub_prereq_data['type'] == 'course' and sub_prereq_data['concurrency_ind'] is True:
                    continue

                prereq_operands.append(sub_prereq_data)

            if len(prereq_operands) == 0:
                return RequisiteCheckResult(True)

            results = []
            for sub_prereq_data in prereq_operands:
                results.append(self.__traverse_prereqs(sub_prereq_data, academic_period, courses_taken, test_scores, ignore_grades))

            result = RequisiteCheckResult(False)

            for r in results:
                if r is None:
                    continue

                if result.satisfied is False and r.satisfied is True:
                    result.satisfied = True
                elif r.satisfied is True:
                    result.satisfied = True

                if r.satisfied:
                    result.met_conditions = result.met_conditions + r.met_conditions
                result.failed_conditions = result.failed_conditions + r.failed_conditions

            return result


    def __reduce_rule(self, prereq_data, filter_rule):
        if prereq_data is None:
            return None

        if 'operands' in prereq_data:
            new_operands = []
            for operand in prereq_data['operands']:
                reduced_operand = self.__reduce_rule(operand, filter_rule)
                if reduced_operand is not None:
                    new_operands.append(reduced_operand)

            if len(new_operands) == 1:
                if prereq_data.get('root', False) is True:
                    new_operands[0]['root'] = True

                return new_operands[0]

            elif len(new_operands) == 0:
                return None
            else:
                new_prereq = {
                    'type': prereq_data['type'],
                    'operands': new_operands
                }

                if prereq_data.get('root', False) is True:
                    new_prereq['root'] = True

                return new_prereq
        else:
            return False if filter(prereq_data) is False else prereq_data

    class AcademicPeriodNotFound(Exception):
        """An exception to be raised when an academic period is not found in the
        given prerequisite data.
        """
        def __init__(self, *args):
            super().__init__(*args)

    class CourseNotFound(Exception):
        """An exception to be raised when a course is not found in the
        given prerequisite data.
        """
        def __init__(self, *args):
            super().__init__(*args)