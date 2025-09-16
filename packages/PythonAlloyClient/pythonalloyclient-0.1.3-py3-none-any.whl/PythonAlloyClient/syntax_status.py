class SyntaxStatus:
    """
    Encapsulates the result of an Alloy syntax check.
    
    **Attributes**
    * `success` (`bool`): True if the syntax check passed, False otherwise    
    * `error_type` (`str`): Type of error, None if `success` is True    
    * `line_number` (`int`): Line number where the error occurred, None if `success` is True    
    * `column_number` (`int`): Column number where the error occurred, None if `success` is True    
    * `error_message` (`str`): Error message, None if `success` is True    
    * `full_error_message` (`str`): Full error message from Alloy, None if `success` is True

    If a syntax check failed due to an unexpected error, the `full_error_message` attribute will contain the error message, `success` will be False, and all other attributes will be None.
    """
    
    def __init__(self, success: bool, error: dict = None):
        """
        Initialize a SyntaxStatus object.
        
        Args:
            success (bool): Whether the syntax check was successful.
            error (dict | str): Dictionary containing error information if success is False. If a string is provided, it is assumed to be the full error message (like in the case of an unexpected error). 
        """
        self.success = success
        
        if error is None:
            error = {
                "full_error_message": None,
                "error_type": None,
                "line_number": None,
                "column_number": None,
                "error_message": None
            }
            
        self.full_error_message = error.get("full_error_message")
        self.error_type = error.get("error_type")
        self.line_number = error.get("line_number")
        self.column_number = error.get("column_number")
        self.error_message = error.get("error_message")
    
    def __bool__(self):
        """
        Allow using the SyntaxStatus object in boolean context.
        
        Returns:
            bool: True if the syntax check was successful, False otherwise
        """
        return self.success
    
    def __str__(self):
        """
        String representation of the SyntaxStatus object.
        
        Returns:
            str: A string representation of the SyntaxStatus object
        """
        if self.success:
            return "Syntax check passed successfully"
        else:
            return f"Syntax error: {self.error_message or self.full_error_message}"
