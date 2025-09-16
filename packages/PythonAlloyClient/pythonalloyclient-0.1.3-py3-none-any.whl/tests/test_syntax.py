import textwrap
from PythonAlloyClient import AlloyServer

class TestSyntax():
    def check_syntax(self, alloy_code, try_get_diagnostics: bool = False):
        server = AlloyServer()
        server.start()
        try:
            return server.check_syntax(alloy_code, try_get_diagnostics)
        finally:
            server.stop()

    def test_correct_syntax(self):
        alloy_code = """sig A {}"""
        syntax_check = self.check_syntax(alloy_code)

        assert syntax_check.success == True
        assert syntax_check.error_type is None
        assert syntax_check.line_number is None
        assert syntax_check.column_number is None
        assert syntax_check.error_message is None
        assert syntax_check.full_error_message is None

    def test_incorrect_syntax(self):
        alloy_code = textwrap.dedent("""
        sig X {}
        sig A extends X {}
        sig A extends X {}
        """)
        syntax_check = self.check_syntax(alloy_code)
        
        assert syntax_check.success == False
        assert syntax_check.error_type == "Syntax error"
        assert syntax_check.line_number == 4
        assert syntax_check.column_number == 5
        assert syntax_check.error_message == '"A" is already the name of a sig/parameter in this module.'
        assert syntax_check.full_error_message == 'Syntax error at line 4 column 5:\n"A" is already the name of a sig/parameter in this module.'

    def test_diagnostic_error(self):
        alloy_code = textwrap.dedent("""
        sig X {}
        sig A extends X {}
        pred p {
            all x: X, a: A | x > a -- bad operation but valid syntax
        }
        run p
        """)
        syntax_check = self.check_syntax(alloy_code, try_get_diagnostics=True)
    
        assert syntax_check.success == False
        assert syntax_check.error_type == "Diagnostics error"
        assert syntax_check.line_number == 4
        assert syntax_check.column_number == 21
        assert syntax_check.error_message == 'This must be an integer expression.\nInstead, it has the following possible type(s):\n{this/X}'
        assert syntax_check.full_error_message == 'Diagnostics error in range 4,21 to 4,22: This must be an integer expression.\nInstead, it has the following possible type(s):\n{this/X}'
