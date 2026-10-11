import unittest

from app.services.security.static_scanner import mask_inert_code, scan_code


class TestScannerAccuracy(unittest.TestCase):
    def test_empty_and_whitespace_code(self):
        self.assertEqual(scan_code(""), [])
        self.assertEqual(scan_code("   \n\n   "), [])

    def test_benign_comments_do_not_trigger_false_positives(self):
        code = """
# In production, never use eval() or exec()
# Avoid pickle.loads() on untrusted data
// Do not use innerHTML or document.write()
// Avoid new Function()
/*
 * Never call system() or popen()
 * Avoid gets() and strcpy()
 */
def safe_function():
    return True
"""
        findings = scan_code(code)
        self.assertEqual(findings, [])

    def test_docstrings_do_not_trigger_false_positives(self):
        code = '''
def process_data():
    """
    This utility avoids exec() and eval() for security reasons.
    Subprocess calls never use shell=True.
    """
    return 42

def another_docstring():
    \'\'\'
    Runtime.getRuntime().exec() and ProcessBuilder() are strictly prohibited.
    \'\'\'
    pass
'''
        findings = scan_code(code)
        self.assertEqual(findings, [])

    def test_url_string_literals_are_not_truncated_as_comments(self):
        code = """
url = "https://example.com/api/v1"
api_path = 'http://127.0.0.1:8000/docs'
"""
        findings = scan_code(code)
        self.assertEqual(findings, [])

    def test_true_positives_python_vulnerabilities(self):
        code = """# Safe header comment
import os, subprocess, pickle

def unsafe_python(payload):
    result = eval(payload)
    exec("print('executed')")
    data = pickle.loads(payload)
    os.system("echo test")
    subprocess.run(["ls"], shell=True)
    return result
"""
        findings = scan_code(code)
        self.assertEqual(len(findings), 5)

        # Verify correct line numbers & messages
        findings_by_line = {f["line_number"]: f for f in findings}
        self.assertIn(5, findings_by_line)
        self.assertEqual(findings_by_line[5]["severity"], "critical")
        self.assertEqual(findings_by_line[5]["comment"], "Use of eval() detected.")

        self.assertIn(6, findings_by_line)
        self.assertEqual(findings_by_line[6]["severity"], "critical")
        self.assertEqual(findings_by_line[6]["comment"], "Use of exec() detected.")

        self.assertIn(7, findings_by_line)
        self.assertEqual(findings_by_line[7]["severity"], "high")

        self.assertIn(8, findings_by_line)
        self.assertEqual(findings_by_line[8]["severity"], "high")

        self.assertIn(9, findings_by_line)
        self.assertEqual(findings_by_line[9]["severity"], "critical")
        self.assertEqual(findings_by_line[9]["comment"], "subprocess shell=True detected.")

    def test_true_positives_javascript_vulnerabilities(self):
        code = """// JavaScript test
function render(userInput) {
    document.getElementById("output").innerHTML = userInput;
    const fn = new Function("a", "b", "return a + b;");
    document.write("<p>Hello</p>");
}
"""
        findings = scan_code(code)
        self.assertEqual(len(findings), 3)

        lines = [f["line_number"] for f in findings]
        self.assertEqual(lines, [3, 4, 5])

    def test_true_positives_native_and_java_vulnerabilities(self):
        code = """/* Native code test */
void handle_input(char *src) {
    char dest[100];
    strcpy(dest, src);
    system("whoami");
    popen("ls", "r");
    gets(dest);
}
"""
        findings = scan_code(code)
        self.assertEqual(len(findings), 4)
        found_comments = [f["comment"] for f in findings]
        self.assertIn("strcpy() may cause buffer overflows.", found_comments)
        self.assertIn("system() call detected.", found_comments)
        self.assertIn("popen() detected.", found_comments)
        self.assertIn("Unsafe gets() usage detected.", found_comments)

    def test_inline_comment_stripped_while_active_code_still_detected(self):
        code = """
x = 10  # Note: do not use eval() here
eval(user_input)  # This is the real exploit
"""
        findings = scan_code(code)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["line_number"], 3)

    def test_substring_words_do_not_trigger_false_positives(self):
        code = """
items = targets()
elements = widgets()
model = retrieval()
fs = filesystem()
"""
        findings = scan_code(code)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
