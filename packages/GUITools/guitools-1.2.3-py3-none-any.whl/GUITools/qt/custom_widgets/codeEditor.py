# coding: utf-8
from PySide6.QtWidgets import QApplication, QPlainTextEdit , QWidget, QTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextOption, QWheelEvent, QTextCursor, QKeyEvent, QPainter, QTextDocument
from PySide6.QtCore import QRegularExpression, Qt, QRect, QSize, Slot
from enum import Enum
from ..style.utils import TypeTheme, Global
import os, json
from ..style.widgets.theme import WidgetsTheme, BaseColor

class BaseQSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document : QTextDocument, single_patterns : list[QRegularExpression], triple_single : str, triple_double : str, comment_pattern : str):
        super().__init__(document)
        self.highlighting_rules = []
        self.single_patterns = single_patterns
        self.triple_single = triple_single
        self.triple_double = triple_double
        
        # Comments
        self.comment_pattern = QRegularExpression(comment_pattern) 
        
        self.highlighting()

    def highlighting(self):
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#CE9178" if Global.theme == TypeTheme.dark else "#8B0000"))
        self.multi_format = QTextCharFormat(self.string_format) 
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6A9955" if Global.theme == TypeTheme.dark else "#228B22"))

    def highlightBlock(self, text : str):
        for pattern, fmt in self.highlighting_rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # stripped = text.lstrip()
        # if stripped.startswith('#'):
        #     indent = len(text) - len(stripped)
        #     self.setFormat(indent, len(stripped), self.comment_format)
        #     self.setCurrentBlockState(0)
        #     return
                
        # 1) Identificar strings simples, mas não partes de triplas
        single_ranges = []
        mask = list(text)
        for pat in self.single_patterns:
            it = pat.globalMatch(text)
            while it.hasNext():
                m = it.next()
                start, length = m.capturedStart(), m.capturedLength()
                quote = text[start]
                # verificar contexto para evitar triplas
                if text[start:start+3] in (self.triple_single, self.triple_double):
                    continue
                if start>0 and text[start-1]==quote:
                    continue
                end_pos = start+length
                if end_pos < len(text) and text[end_pos]==quote:
                    continue
                # marca string simples
                self.setFormat(start, length, self.string_format)
                single_ranges.append((start, end_pos))
                for i in range(start, end_pos): mask[i] = ' '
        masked = ''.join(mask)

        # 2) Encontrar todas aspas triplas
        trips = []  # (pos, delim)
        for delim in (self.triple_single, self.triple_double):
            idx = masked.find(delim)
            start = 0
            while idx!=-1:
                trips.append((idx, delim))
                start = idx+3
                idx = masked.find(delim, start)
        trips.sort(key=lambda x: x[0])

        # 3) Lidar com estado anterior
        prev = self.previousBlockState()
        pending = self.triple_single if prev==1 else self.triple_double if prev==2 else None
        state = 0
        i=0
        # se pendente, buscar fechamento
        if pending:
            while i<len(trips) and trips[i][1]!=pending: i+=1
            if i<len(trips):
                # fechar
                self.setFormat(0, trips[i][0]+3, self.multi_format)
                i+=1
            else:
                self.setFormat(0, len(text), self.multi_format)
                self.setCurrentBlockState(1 if pending==self.triple_single else 2)
                return

        # 4) Parear demais
        while i+1 < len(trips):
            pos1, d1 = trips[i]
            # achar par
            j=i+1
            while j<len(trips) and trips[j][1]!=d1: j+=1
            if j<len(trips):
                length = trips[j][0]-pos1+3
                self.setFormat(pos1, length, self.multi_format)
                i=j+1
            else:
                break

        # 5) abertura sem fechamento
        if i<len(trips):
            pos1,d1=trips[i]
            self.setFormat(pos1, len(text)-pos1, self.multi_format)
            state = 1 if d1==self.triple_single else 2
        else:
            state=0
        self.setCurrentBlockState(state)

        match_iter = self.comment_pattern.globalMatch(text)
        while match_iter.hasNext():
            match = match_iter.next()
            start, length = match.capturedStart(), match.capturedLength()
            # só aplicar se não estiver dentro de string
            in_string = any(start >= s and start < e for s, e in single_ranges)
            if not in_string and self.format(start).foreground() != self.multi_format.foreground():
                self.setFormat(start, length, self.comment_format)

class PythonSyntaxHighlighter(BaseQSyntaxHighlighter):
    def __init__(self, document : QTextDocument):
        single_patterns = [
            QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'),
            QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'")
        ]
        super().__init__(document, single_patterns, "'''", '"""', r"#.*")

    def highlighting(self):
        self.highlighting_rules.clear()
        super().highlighting()
       
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6" if Global.theme == TypeTheme.dark else "#00008B"))

        # Decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#DCDCAA" if Global.theme == TypeTheme.dark else "#8B8000"))
        self.highlighting_rules.append((QRegularExpression(r"@\w+"), decorator_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8" if Global.theme == TypeTheme.dark else "#006400"))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+[lL]?\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?0[xX][0-9A-Fa-f]+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?\b"), number_format))

        # Functions 
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA" if Global.theme == TypeTheme.dark else "#FF0000" ))
        self.highlighting_rules.append((QRegularExpression(r"\bdef\s+\w+\b"), function_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+(?=\()"), function_format))
        
        # Decorators
        self.highlighting_rules.append((QRegularExpression(r'@\w+'), function_format))

        # Class
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0" if Global.theme == TypeTheme.dark else "#008B8B"))
        self.highlighting_rules.append((QRegularExpression(r"class\s+\w+\s*\(([^)]+)\)"), class_format))

        # Tipos de parâmetros após ":"
        self.highlighting_rules.append((QRegularExpression(r":\s*([A-Za-z_][A-Za-z0-9_]*)(?=\s*[,)|=])"), class_format))

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4" if Global.theme == TypeTheme.dark else "#808080"))
        operators = [
            r"\+", r"-", r"\*", r"/", r"//", r"%", r"\*\*", r"=", r"\+=", r"-=", r"\*=", r"/=", r"%=", r"&=", r"\|=", r"\^=",
            r">>", r"<<", r"==", r"!=", r"<", r">", r"<=", r">=", r"\(", r"\)", r"\[", r"\]", r"\{", r"\}", r"\.", r",", r":", 
            r";", r"\?", r"@", r"&", r"\|", r"~", r"^", r"<<", r">>", r"\\"
        ]
        self.highlighting_rules += [(QRegularExpression(op), operator_format) for op in operators]

        keywords = [
            'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or', 'pass',
            'raise', 'return', 'True', 'try', 'while', 'with', 'yield', 'self', 'cls'
        ]

        self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b"), keyword_format) for keyword in keywords]

        # Built-in functions
        builtin_format = QTextCharFormat() 
        builtin_format.setForeground(QColor("#C586C0" if Global.theme == TypeTheme.dark else "#7B68EE"))
        builtins = [
            'abs', 'dict', 'help', 'min', 'setattr', 'all', 'dir', 'hex', 'next', 'slice',
            'any', 'divmod', 'id', 'object', 'sorted', 'ascii', 'enumerate', 'input', 'oct',
            'staticmethod', 'bin', 'eval', 'int', 'open', 'str', 'bool', 'exec', 'isinstance',
            'ord', 'sum', 'bytearray', 'filter', 'issubclass', 'pow', 'super', 'bytes', 'float',
            'iter', 'print', 'tuple', 'callable', 'format', 'len', 'property', 'type', 'chr',
            'frozenset', 'list', 'range', 'vars', 'classmethod', 'getattr', 'locals', 'repr',
            'zip', 'compile', 'globals', 'map', 'reversed', '__import__', 'complex', 'hasattr',
            'max', 'round', 'delattr', 'hash', 'memoryview', 'set'
        ]
        self.highlighting_rules += [(QRegularExpression(f"\\b{builtin}\\b"), builtin_format) for builtin in builtins]

class VbNetSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        self.highlighting_rules = []
        self.highlighting()

    def highlighting(self):
        self.highlighting_rules.clear()

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6" if Global.theme == TypeTheme.dark else "#00008B"))

        # Decorators or Attributes
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor("#DCDCAA" if Global.theme == TypeTheme.dark else "#8B8000"))
        self.highlighting_rules.append((QRegularExpression(r"<\w+>"), attribute_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8" if Global.theme == TypeTheme.dark else "#006400"))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+(\.[0-9]+)?\b"), number_format))

        # Functions and Subroutines
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA" if Global.theme == TypeTheme.dark else "#FF0000"))
        self.highlighting_rules.append((QRegularExpression(r"\b(Sub|Function)\s+\w+\b"), function_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+(?=\()"), function_format))

        # Classes and Structures
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0" if Global.theme == TypeTheme.dark else "#008B8B"))
        self.highlighting_rules.append((QRegularExpression(r"\b(Class|Structure|Enum|Module)\s+\w+\b"), class_format))

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4" if Global.theme == TypeTheme.dark else "#808080"))
        operators = [
            r"\+", r"-", r"\*", r"/", r"\\", r"Mod", r"^", r"=", r"<", r">", r"<=", r">=", r"<>", r"Not", r"And", r"Or",
            r"Xor", r"Is", r"Like", r"&", r"\(", r"\)", r"\[", r"\]", r"\{", r"\}", r"\.", r",", r":", r";"
        ]
        self.highlighting_rules += [(QRegularExpression(op), operator_format) for op in operators]

        # VB.NET Keywords
        keywords = [
            "Dim", "As", "Public", "Private", "Protected", "Friend", "Static", "Shared", "ReadOnly", "WriteOnly", "Const",
            "Option", "Strict", "Infer", "Explicit", "On", "Off", "If", "Then", "Else", "ElseIf", "End", "Select", "Case",
            "For", "Each", "To", "Next", "Do", "While", "Loop", "Until", "With", "Try", "Catch", "Finally", "Throw",
            "Return", "Exit", "Continue", "Goto", "True", "False", "Nothing", "New", "Set", "Get", "Property", "Inherits",
            "Implements", "Overrides", "Overloads", "MustOverride", "NotInheritable", "NotOverridable", "Partial", "Imports"
        ]
        self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b"), keyword_format) for keyword in keywords]

        # Built-in functions
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#C586C0" if Global.theme == TypeTheme.dark else "#7B68EE"))
        builtin_format = QTextCharFormat()

        builtins = [
            "MsgBox", "InputBox", "IsNothing", "IsDBNull", "Len", "UCase", "LCase", "Mid", "Replace", "Trim", "Split",
            "Join", "InStr", "Format", "Val", "Chr", "Asc", "DateAdd", "DateDiff", "DatePart", "DateSerial", "DateValue",
            "TimeSerial", "TimeValue", "Now", "Today", "CDate", "CInt", "CLng", "CStr", "CType", "CDbl", "CDec", "CSng"
        ]
        self.highlighting_rules += [(QRegularExpression(f"\\b{builtin}\\b"), builtin_format) for builtin in builtins]

         # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178" if Global.theme == TypeTheme.dark else "#8B0000"))
        self.highlighting_rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955" if Global.theme == TypeTheme.dark else "#228B22"))
        #comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r"'.*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = pattern.globalMatch(text)
            while expression.hasNext():
                match = expression.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class CSyntaxHighlighter(BaseQSyntaxHighlighter):
    def __init__(self, document):
        single_patterns = [
            QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'),
            QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'")  # C# permite char com aspas simples
        ]
        super().__init__(document, single_patterns, "/*", '*/', r"//.*")

    def highlighting(self):
        self.highlighting_rules.clear()
        super().highlighting()

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6" if Global.theme == TypeTheme.dark else "#00008B"))
        keywords = [
            "abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char", "checked", "class", "const", "continue",
            "decimal", "default", "delegate", "do", "double", "else", "enum", "event", "explicit", "extern", "false", "finally",
            "fixed", "float", "for", "foreach", "goto", "if", "implicit", "in", "int", "interface", "internal", "is", "lock",
            "long", "namespace", "new", "null", "object", "operator", "out", "override", "params", "private", "protected",
            "public", "readonly", "ref", "return", "sbyte", "sealed", "short", "sizeof", "stackalloc", "static", "string", 
            "struct", "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong", "unchecked", "unsafe", "ushort", 
            "using", "virtual", "void", "volatile", "while"
        ]
        self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b"), keyword_format) for keyword in keywords]

        # Types (int, float, etc.)
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0" if Global.theme == TypeTheme.dark else "#008B8B"))
        types = ["int", "float", "double", "string", "char", "bool", "object", "void", "var"]
        self.highlighting_rules += [(QRegularExpression(f"\\b{t}\\b"), type_format) for t in types]

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8" if Global.theme == TypeTheme.dark else "#006400"))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+(\.[0-9]+)?\b"), number_format))

        # Functions and Methods
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA" if Global.theme == TypeTheme.dark else "#FF0000"))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+(?=\()"), function_format))

        # Class and Struct definitions
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0" if Global.theme == TypeTheme.dark else "#008B8B"))
        self.highlighting_rules.append((QRegularExpression(r"\bclass\s+\w+\b"), class_format))
        self.highlighting_rules.append((QRegularExpression(r"\bstruct\s+\w+\b"), class_format))

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4" if Global.theme == TypeTheme.dark else "#808080"))
        operators = [
            r"\+", r"-", r"\*", r"/", r"//", r"%", r"\*\*", r"=", r"\+=", r"-=", r"\*=", r"/=", r"%=", r"&=", r"\|=", r"\^=",
            r">>", r"<<", r"==", r"!=", r"<", r">", r"<=", r">=", r"\(", r"\)", r"\[", r"\]", r"\{", r"\}", r"\.", r",", r":", 
            r";", r"\?", r"@", r"&", r"\|", r"~", r"^", r"<<", r">>", r"\\"
        ]
        self.highlighting_rules += [(QRegularExpression(op), operator_format) for op in operators]

class JsonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        self.highlighting_rules = []
        self.highlighting()

    def highlighting(self):
        self.highlighting_rules.clear()
 
        # Numbers (green)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8" if Global.theme == TypeTheme.dark else "#006400"))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+(\.[0-9]+)?\b"), number_format))

        # Format for JSON keys (blue)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#9CDCFE" if Global.theme == TypeTheme.dark else "#4682B4"))  # Azul mais claro para chaves
        self.highlighting_rules.append((QRegularExpression(r'\".*?\"(?=\s*:)'), key_format))  # Keys

        # Format for JSON values (red)
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#CE9178" if Global.theme == TypeTheme.dark else "#8B0000"))  # Vermelho para valores
        # Ajuste para capturar valores diretamente
        self.highlighting_rules.append((QRegularExpression(r'(?<=:\s)\".*?\"'), value_format))
       
        # Booleans and Nulls (blue)
        bool_null_format = QTextCharFormat()
        bool_null_format.setForeground(QColor("#569CD6" if Global.theme == TypeTheme.dark else "#00008B"))
        self.highlighting_rules.append((QRegularExpression(r"\b(true|false|null)\b"), bool_null_format))

        # Curly braces `{}` (darker blue)
        brace_format = QTextCharFormat()
        brace_format.setForeground(QColor("#569CD6" if Global.theme == TypeTheme.dark else "#00008B"))  # Azul mais forte
        self.highlighting_rules.append((QRegularExpression(r"[\{\}]"), brace_format))

        # Square brackets `[]` (lilac)
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor("#C586C0" if Global.theme == TypeTheme.dark else "#7B68EE"))  # Lilás
        self.highlighting_rules.append((QRegularExpression(r"[\[\]]"), bracket_format))


    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = pattern.globalMatch(text)
            while expression.hasNext():
                match = expression.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class XmlHtmlSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        self.highlighting()

    def highlighting(self):
        self.highlighting_rules.clear()

        # Tags (azul)
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#569CD6" if Global.theme == TypeTheme.dark else "#00008B"))  # Azul
        self.highlighting_rules.append((QRegularExpression(r"</?\b\w+"), tag_format))  # Captura tags de abertura e fechamento

        # Atributos (verde)
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor("#B5CEA8" if Global.theme == TypeTheme.dark else "#006400"))  # Verde
        self.highlighting_rules.append((QRegularExpression(r'\b\w+(?=\=)'), attribute_format))  # Atributos antes do `=`

        # Valores dos atributos (vermelho)
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#CE9178" if Global.theme == TypeTheme.dark else "#8B0000"))  # Vermelho
        self.highlighting_rules.append((QRegularExpression(r'\".*?\"'), value_format))  # Valores de atributos entre aspas

        # Símbolos de pontuação (cinza)
        punctuation_format = QTextCharFormat()
        punctuation_format.setForeground(QColor("#D4D4D4" if Global.theme == TypeTheme.dark else "#808080"))  # Cinza
        self.highlighting_rules.append((QRegularExpression(r"[<>/=]"), punctuation_format))  # Símbolos especiais do XML/HTML (<, >, =, /)

        # Comentários (cinza escuro)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955" if Global.theme == TypeTheme.dark else "#808080"))  # Cinza escuro
        self.highlighting_rules.append((QRegularExpression(r'<!--[\s\S]*?-->'), comment_format))  # Comentários XML/HTML

        # Entidades HTML (laranja)
        entity_format = QTextCharFormat()
        entity_format.setForeground(QColor("#D7BA7D" if Global.theme == TypeTheme.dark else "#FF4500"))  # Laranja
        self.highlighting_rules.append((QRegularExpression(r"&\w+;"), entity_format))  # Entidades HTML (&nbsp;, &amp;, etc.)

        # HTML Doctype (púrpura)
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(QColor("#C586C0" if Global.theme == TypeTheme.dark else "#800080"))  # Púrpura
        self.highlighting_rules.append((QRegularExpression(r"<!DOCTYPE.*?>"), doctype_format))  # Doctype em HTML

    def highlightBlock(self, text):
        # Aplica as regras de realce de sintaxe para cada bloco de texto
        for pattern, fmt in self.highlighting_rules:
            expression = pattern.globalMatch(text)
            while expression.hasNext():
                match = expression.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class GenericSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        """
        Initializes the highlighter with generic highlighting rules suitable for many programming languages.

        :param document: QTextDocument associated with the QTextEdit.
        """
        super().__init__(document)
        
        self.multi_line_string_format = QTextCharFormat()
        self.highlighting_rules = []
        self.highlighting()

    def highlighting(self):
        """
        Sets up generic highlighting rules that can match common syntax across many programming languages.
        """
        self.highlighting_rules.clear()
        self.multi_line_string_format.setForeground(QColor("#CE9178" if Global.theme == TypeTheme.dark else "#8B0000"))

        # Generic keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6" if Global.theme == TypeTheme.dark else "#00008B"))
        
        # Generic function and class format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA" if Global.theme == TypeTheme.dark else "#8B8000"))

        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0" if Global.theme == TypeTheme.dark else "#008B8B"))

        # String format (single, double, multiline)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178" if Global.theme == TypeTheme.dark else "#8B0000"))

        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8" if Global.theme == TypeTheme.dark else "#006400"))

        # Comment format with theme support
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955" if Global.theme == TypeTheme.dark else "#228B22"))
        #comment_format.setFontItalic(True)

        # Operator format
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4" if Global.theme == TypeTheme.dark else "#808080"))

        # Adding generic regex rules for common elements
        keywords = [
            # Common keywords across multiple languages (only lowercase needed due to case-insensitive regex)
            "using", "from", "if", "else", "for", "while", "return", "class", "def", "function", "import", 
            "export", "try", "catch", "finally", "switch", "case", "break", "continue", "true", 
            "false", "null", "undefined", "new", "delete", "this", "super", "public", "private", 
            "protected", "static", "void", "var", "let", "const", "async", "await", "yield", 
            "throw", "lambda"
        ]

        # Numbers: integers, floats, hexadecimal
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+[lL]?\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?0[xX][0-9A-Fa-f]+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?\b"), number_format))

        # Functions and classes
        self.highlighting_rules.append((QRegularExpression(r"\b\w+\s*(?=\()", QRegularExpression.PatternOption.CaseInsensitiveOption), function_format))
        self.highlighting_rules.append((QRegularExpression(r"\bclass\s+\w+\b", QRegularExpression.PatternOption.CaseInsensitiveOption), class_format))
        self.highlighting_rules.append((QRegularExpression(r"\bdef\s+\w+\b", QRegularExpression.PatternOption.CaseInsensitiveOption), function_format))

        
        # Operators: common across languages
        operators = [
            r"\+", r"-", r"\*", r"/", r"//", r"%", r"\*\*", r"=", r"\+=", r"-=", r"\*=", r"/=", r"%=",
            r"&=", r"\|=", r"\^=", r">>", r"<<", r"==", r"!=", r"<", r">", r"<=", r">=", r"\(", r"\)", r"\[", r"\]",
            r"\{", r"\}", r"\.", r",", r":", r";", r"\?", r"@", r"&", r"\|", r"~", r"^", r"\\", r"->"
        ]
        self.highlighting_rules += [(QRegularExpression(op), operator_format) for op in operators]

        # Use case-insensitive regex pattern for keywords
        self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b", QRegularExpression.PatternOption.CaseInsensitiveOption), keyword_format) for keyword in keywords]

        # Strings: single, double, triple quotes
        self.highlighting_rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"', QRegularExpression.PatternOption.CaseInsensitiveOption), string_format))
        self.highlighting_rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'", QRegularExpression.PatternOption.CaseInsensitiveOption), string_format))

        # Comments: single line (//, #) and multi-line (/* */)
        self.highlighting_rules.append((QRegularExpression(r"//.*", QRegularExpression.PatternOption.CaseInsensitiveOption), comment_format))
        self.highlighting_rules.append((QRegularExpression(r"#.*", QRegularExpression.PatternOption.CaseInsensitiveOption), comment_format))
        self.highlighting_rules.append((QRegularExpression(r"/\*[\s\S]*?\*/", QRegularExpression.PatternOption.CaseInsensitiveOption), comment_format))

    def highlightBlock(self, text):
        """
        Applies the defined highlighting rules to the given text block.

        :param text: The text block to highlight.
        """

        # Apply generic highlighting rules
        for pattern, fmt in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class CodeEditor(QPlainTextEdit):

    class Language(Enum):
        txt = 0
        generic = 1
        python = 2
        vb = 3
        csharp = 4
        json = 5
        XmlHtml = 6
  
    def __init__(self, language : Language = Language.txt, adjust_height = False, content : str = None, readOnly = False, indent_width=5, use_spaces=True):
        super().__init__()
        self.adjust_height = adjust_height
        self.language = language

        self.indent_width = indent_width
        self.use_spaces = use_spaces  # número de espaços por indentação
        self.indent_guide_color = BaseColor.division
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)

        self.setTabStopDistance(indent_width * self.fontMetrics().horizontalAdvance(' '))

        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        
        self.set_language(language)
        self.setReadOnly(readOnly)
        if not readOnly:
            self.highlightCurrentLine()

        self.current_font_size = self.font().pointSize()  # Guarda o tamanho atual da fonte
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if adjust_height:
            self.textChanged.connect(self.autoResize)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        if content:
            self.setPlainText(content)

        WidgetsTheme.set_code_editor_widget(self)

    def set_language(self, language: Language):
        self.language = language

        if language == self.Language.txt:
            self.highlighter = None
        elif language == self.Language.python:
            self.highlighter = PythonSyntaxHighlighter(self.document())
        elif language == self.Language.vb:
            self.highlighter = VbNetSyntaxHighlighter(self.document())
        elif language == self.Language.csharp:
            self.highlighter = CSyntaxHighlighter(self.document())
        elif language == self.Language.json:
            self.highlighter = JsonSyntaxHighlighter(self.document())
        elif language == self.Language.XmlHtml:
            self.highlighter = XmlHtmlSyntaxHighlighter(self.document())
        elif language == self.Language.generic:
            self.highlighter = GenericSyntaxHighlighter(self.document())
        else:
            self.highlighter = None

    @classmethod
    def detect_language_from_filename(cls, filename: str, default: 'CodeEditor.Language' = None) -> 'CodeEditor.Language':
        """
        Detect the programming language based on the file extension.

        Args:
            filename (str): The name of the file.
            default (CodeEditor.Language, optional): The language to return if no match is found.
                Defaults to Language.generic.

        Returns:
            CodeEditor.Language: The detected language enum value, or the default if unknown.
        """
        
        ext = os.path.basename(filename).lower()  
        
        if ext.endswith('.py'):
            return cls.Language.python
        elif ext.endswith('.vb'):
            return cls.Language.vb
        elif ext.endswith('.cs'):
            return cls.Language.csharp
        elif ext.endswith('.json'):
            return cls.Language.json
        elif ext.endswith(('.xml', '.html', '.htm')):
            return cls.Language.XmlHtml
        elif ext.endswith('.txt'):
            return cls.Language.txt
        
        if default is None:
            default = cls.Language.generic
        return default

    def toggle_adjust_height(self, adjust_height : bool):
        self.adjust_height = adjust_height
        try:
            self.textChanged.disconnect(self.autoResize)
        except:
            pass

        if adjust_height:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.textChanged.connect(self.autoResize)
            self.autoResize()
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setFixedHeight(self.sizeHint().height())
            self.setMaximumHeight(16777215)
            self.setMinimumHeight(0)

    def appendText(self, text: str):
        if not text:
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Força quebra de linha correta
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Evita quebra de indentação causada por cursor incorreto
        cursor.insertText(text)

        self.setTextCursor(cursor)

    def remove_blank_lines_at_end(self):
        doc = self.document()
        cursor = QTextCursor(doc)

        cursor.movePosition(QTextCursor.MoveOperation.End)

        while cursor.block().position() > 0:
            block_text = cursor.block().text()

            if block_text.strip() == '':
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  
                cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
            else:
                break
        
    def setPlainText(self, text: str | None) -> None:
        super().setPlainText(text)
        self.setExtraSelections([])

    def copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.toPlainText())

    def autoResize(self):
        if not self.adjust_height:
            return

        doc = self.document()
        layout = doc.documentLayout()

        height = 0
        block = doc.firstBlock()
        if block.isValid():
            height += layout.blockBoundingRect(block).height()
        while block.isValid():
            height += layout.blockBoundingRect(block).height()
            block = block.next()

        margins = self.contentsMargins()
        height += margins.top() + margins.bottom()

        self.setFixedHeight(height)

    def highlighting(self):
        if self.highlighter:
            vscroll_position = self.verticalScrollBar().value()
            hscroll_position = self.horizontalScrollBar().value()

            code = self.toPlainText()
            self.clear()
            self.highlighter.highlighting()
            self.setPlainText(code)

            self.verticalScrollBar().setValue(vscroll_position)
            self.horizontalScrollBar().setValue(hscroll_position)

    def wheelEvent(self, event: QWheelEvent):
        # Verifica se a tecla Ctrl está pressionada
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Aumenta ou diminui o tamanho da fonte dependendo da direção do scroll
            if event.angleDelta().y() > 0:
                self.current_font_size += 1
            else:
                self.current_font_size -= 1

            # Define o novo tamanho da fonte, garantindo que não fique muito pequeno
            if self.current_font_size < 1:
                self.current_font_size = 1

            # Atualiza a fonte do QTextEdit com o novo tamanho
            self.setStyleSheet(f'font: {self.current_font_size}pt "Segoe UI"')

            # Ignora o evento padrão de rolagem para evitar a rolagem do conteúdo
            event.accept()
        else:
            # Se Ctrl não está pressionado, continua com o comportamento normal do scroll
            super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        cursor = self.textCursor()
        indent_str = ' ' * self.indent_width if self.use_spaces else '\t'

        if event.key() == Qt.Key.Key_Tab:
            if cursor.hasSelection():
                self.indent_selected_lines(cursor, indent_str, include_last_line=True)
            else:
                super().keyPressEvent(event)

        elif event.key() == Qt.Key.Key_Backtab:  # Shift+Tab
            if cursor.hasSelection():
                self.unindent_selected_lines(cursor, include_last_line=True)

        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            block_text = cursor.block().text()
            leading_spaces = len(block_text) - len(block_text.lstrip(' '))
            current_indent = block_text[:leading_spaces]
                            
            super().keyPressEvent(event)
            cursor.insertText(current_indent)

        else:
            super().keyPressEvent(event)

    def indent_selected_lines(self, cursor: QTextCursor, indent_str: str, include_last_line=False):
        cursor.beginEditBlock()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        start_block = cursor.block()

        cursor.setPosition(end)
        if include_last_line or not cursor.atBlockStart():
            end_block = cursor.block()
        else:
            end_block = cursor.block().previous()

        block = start_block
        while block.isValid():
            block_cursor = QTextCursor(block)
            block_cursor.insertText(indent_str)
            if block == end_block:
                break
            block = block.next()

        cursor.endEditBlock()

    def unindent_selected_lines(self, cursor : QTextCursor, include_last_line=False):
        cursor.beginEditBlock()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        start_block = cursor.block()

        cursor.setPosition(end)
        if include_last_line and cursor.atBlockStart() and end != start:
            cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
        end_block = cursor.block()

        block = start_block
        while True:
            block_cursor = QTextCursor(block)
            text = block.text()
            if text.startswith('\t'):
                block_cursor.deleteChar()
            elif text.startswith(' ' * self.indent_width):
                for _ in range(self.indent_width):
                    block_cursor.deleteChar()
            elif text.startswith(' '):
                block_cursor.deleteChar()
            if block == end_block:
                break
            block = block.next()

        cursor.endEditBlock()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setPen(self.indent_guide_color.QColor)

        font_metrics = self.fontMetrics()
        space_width = font_metrics.horizontalAdvance(' ')
        indent_pixel = space_width * self.indent_width

        block = self.firstVisibleBlock()
        content_offset = self.contentOffset()
        viewport_rect = self.viewport().rect()

        guide_offset = 3
        scroll_x = self.horizontalScrollBar().value()  # ← ajuste para scroll horizontal

        while block.isValid():
            block_geometry = self.blockBoundingGeometry(block).translated(content_offset)
            top = round(block_geometry.top())
            bottom = round(block_geometry.bottom())

            if bottom < 0:
                block = block.next()
                continue
            if top > viewport_rect.bottom():
                break

            text = block.text()
            is_blank_line = not text.strip()
            current_indent_px = 0

            if is_blank_line:
                # Procurar próxima linha não vazia
                lookahead = block.next()
                while lookahead.isValid() and not lookahead.text().strip():
                    lookahead = lookahead.next()
                if lookahead.isValid():
                    next_text = lookahead.text()
                    leading_spaces = len(next_text) - len(next_text.lstrip(' '))
                    current_indent_px = leading_spaces * space_width if leading_spaces else 0
                else:
                    current_indent_px = 0
            else:
                leading_spaces = len(text) - len(text.lstrip(' '))
                current_indent_px = leading_spaces * space_width

            if not is_blank_line or current_indent_px > 0:
                level = 0
                while level * indent_pixel < current_indent_px:
                    x = level * indent_pixel + guide_offset - scroll_x  # ← aplica o scroll
                    if 0 <= x <= viewport_rect.width():  # ← desenha apenas se visível
                        painter.drawLine(x, top, x, bottom)
                    level += 1

            block = block.next()

        painter.end()

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = self.fontMetrics().horizontalAdvance('9') * digits + 10
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @Slot(QRect, int)
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def currentLineNumber(self):
        return self.textCursor().blockNumber()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.adjust_height:
            self.autoResize()
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        if not self.isReadOnly():
            if self.document().isEmpty():
                self.setExtraSelections([]) 
                return
            extraSelections = []
            selection = QTextEdit.ExtraSelection()
            base_color = self.palette().color(self.backgroundRole())
            brightness = 0.299 * base_color.red() + 0.587 * base_color.green() + 0.114 * base_color.blue()
            factor = 102 if brightness > 128 else 110
            darker_color = base_color.darker(factor)
            selection.format.setBackground(darker_color)
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
            self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(0, 0, 0, 0))  

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        current_line = self.currentLineNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                if block_number == current_line:
                    color = BaseColor.Reverse.primary.fromQColor(230)
                else:
                    color = BaseColor.Reverse.primary.fromQColor(130) 

                painter.setPen(color)

                margin = 10
                painter.drawText(0, top, self.lineNumberArea.width() - margin,
                                self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

class LineNumberArea(QWidget):
    def __init__(self, editor : CodeEditor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

    