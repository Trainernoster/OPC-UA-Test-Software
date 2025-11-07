
@staticmethod
def get_choices(_question : str = "Enter your question here", _delete_question : bool = True, _choices: list = ["y","n"]) -> str:
    """ Returns the user choice as a string. """
    answered = False
    answer : str = None
    while answered == False:
        print(_question + " (" + "/".join(_choices) + "):")
        user_input = input().strip().lower()
        if user_input in _choices:
            answered = True
            answer = user_input

        if _delete_question == True:
            _delete_rows()
    return answer

@staticmethod
def get_choices_TureFalse(_question : str = "Enter your question here", _delete_question : bool = True, _choices: list = ["y","n"]) -> str:
    """ Returns if the user accepts one choice. """
    answer = None
    print(_question + " (" + "/".join(_choices) + "):")
    user_input = input().strip().lower()
    if user_input in _choices:
        answer = True
    else:
        answer = False

    if _delete_question == True:
        _delete_rows()
    return answer
    
@staticmethod
def get_choice_YesNo(_question : str = "Enter your question here", _delete_question : bool = True) -> bool:
    """ Returns the user choice as a boolen 'True' or 'False'. """
    answer = None
    while answer == None:
        print(_question + " (y/n):")
        user_input = input().strip().lower()
        if user_input in ['y', 'yes']:
            answer = True
        elif user_input in ['n', 'no']:
            answer = False 
        
        if _delete_question == True:
            _delete_rows()
    
    return answer

def _delete_rows():
    print("\033[F\033[K", end="")
    print("\033[F\033[K", end="")