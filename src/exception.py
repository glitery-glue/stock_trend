import sys

def get_error_details(error,error_details:sys):
    _,_,exc_tb=error_details.exc_info()
    script_name=exc_tb.tb_frame.f_code.co_filename
    error_line=exc_tb.tb_lineno
    error_message="Error is in python script name [{0}], in line numer [{1}] with error message [{2}] ".format(
        script_name,error_line,str(error))
    return error_message

class CustomException(Exception):
    def __init__(self, error_message, error_details:sys):
        super().__init__(error_message)
        self.error_message = get_error_details(error_message,error_details=error_details)
    def __str__(self):
        return self.error_message
    
if __name__=="__main__":
    try:
        a=1/0
    except Exception as e:
        raise CustomException(e,sys)
        