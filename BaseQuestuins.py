class GameState:
    def cook(self, array_of_arguments):
        pass

    def print(self):
        pass

    def choise_next_state(self, number):
        pass


class GameStateConditional:
    def __init__(self, condition_func):
        self.condition_func = condition_func


class Variant:
    def __init__(self, text_of_variant, next_state):
        self.text_of_variant = text_of_variant
        self.next_state = next_state


class QuestionStatic(GameState):
    def __init__(self, question=None, variants=None):
        self.question = question
        self.variants = variants

    def print(self):
        if callable(self.question):
            print(self.question())
        else:
            print(self.question)

        for i, variant in enumerate(self.variants, 1):
            print(f"{i}. ", variant.text_of_variant)

    def choise_next_state(self, number):
        return self.variants[number - 1].next_state


# @objects - array of objects with @condition attribute within eath
# @arguments_for_check - objects which will be sended to @condition
# len(@arguments_for_check) must be mutch with parameters count of @condition
# return array of @objects which @objects.condition(*@arguments_for_check) == True
def compute_actual_objects(objects, arguments_for_check):
    actual_objects = []
    for obj in objects:
        if obj.condition_func(*arguments_for_check):
            actual_objects.append(obj)
    return actual_objects


class QuestionDynamicWithVariantsStatic(QuestionStatic):
    def __init__(self, question=None, condition_func=None, variants=None):
        super().__init__(question, variants)
        self.condition_func = condition_func


class ManagerOfDynamicQuestions(GameState):
    def __init__(self, questions=None):
        self.questions = questions
        self.actual_question = None

    def cook(self, array_of_arguments):
        self.actual_question = compute_actual_objects(self.questions, array_of_arguments)[0]

    def print(self):
        self.actual_question.print()

    def choise_next_state(self, number):
        return self.actual_question.choise_next_state(number)


class RhetoricQuestion(GameState):
    def __init__(self, question=None, next_state=None):
        self.question = question
        self.restart = next_state

    def print(self):
        print(self.question)
        print("1. Далее")

    def choise_next_state(self, number):
        if self.restart is not None:
            return self.restart


class RhetoricDynamicQuestion(GameStateConditional, RhetoricQuestion):
    def __init__(self, question=None, condition_func=None, next_state=None):
        GameStateConditional.__init__(self, condition_func)
        RhetoricQuestion.__init__(self, question, next_state)

