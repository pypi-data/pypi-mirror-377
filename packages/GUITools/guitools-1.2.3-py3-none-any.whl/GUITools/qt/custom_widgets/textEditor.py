# coding: utf-8
from PySide6.QtWidgets import QApplication, QTextBrowser, QSizePolicy
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextOption, QWheelEvent, QGuiApplication, QMouseEvent
from PySide6.QtCore import QRegularExpression, Qt, QUrl
from enum import Enum
from ..style.utils import TypeTheme, Global
import re, tempfile, os
from ..style.widgets.theme import WidgetsTheme
import markdown

class TerminalSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        self.highlighting()

    def highlighting(self):
        self.highlighting_rules.clear()
        dark = Global.theme == TypeTheme.dark

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8" if Global.theme == TypeTheme.dark else "#006400"))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+[lL]?\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?0[xX][0-9A-Fa-f]+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b[+-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?\b"), number_format))

        # Opções (ex: -h, --help)
        option_format = QTextCharFormat()
        option_format.setForeground(QColor("#C586C0" if dark else "#7B68EE"))  # roxo
        self.highlighting_rules.append((QRegularExpression(r"\s--?[a-zA-Z0-9-]+"), option_format))

        # Variáveis (ex: $HOME, $(pwd))
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor("#4EC9B0" if dark else "#008B8B"))  # verde água
        self.highlighting_rules.append((QRegularExpression(r"\$\w+"), variable_format))
        self.highlighting_rules.append((QRegularExpression(r"\$\([^)]+\)"), variable_format))

        # Comando (primeira palavra da linha)
        command_format = QTextCharFormat()
        command_format.setForeground(QColor("#569CD6" if dark else "#00008B"))  # azul
        self.highlighting_rules.append((QRegularExpression(r"^\s*[+-]?[0-9]+"), command_format))

        
    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class TextEditor(QTextBrowser):

    class Type(Enum):
        Nothing = 'Nothing'
        Markdown = 'Markdown'
        Terminal = 'Terminal'
  
    def __init__(self, type : Type = Type.Markdown, adjust_height = False, content : str = None, readOnly = False, wrap_paragraphs = False, mouse_press_parent = False):
        super().__init__()
        self.adjust_height = adjust_height
        self.wrap_paragraphs = wrap_paragraphs
        self.type = type
        self.mouse_press_parent = mouse_press_parent

        if mouse_press_parent:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))  # Set tab width
        if type == self.Type.Terminal:
            self.highlighter = TerminalSyntaxHighlighter(self.document())
            WidgetsTheme.set_code_editor_widget(self)
        else:
            self.highlighter = None

        self.setOpenExternalLinks(True)

        self.setReadOnly(readOnly)

        self.current_font_size = self.font().pointSize()  # Guarda o tamanho atual da fonte
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        if adjust_height:
            self.textChanged.connect(self.autoResize)
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            self.document().setTextWidth(self.viewport().width())
            self.autoResize()

        if content:
            if self.type == self.Type.Markdown:
                self.setMarkdown(content)
            else:
                self.setPlainText(content)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.document().setTextWidth(self.viewport().width())
        self.autoResize()

    def autoResize(self):
        if self.adjust_height:
            self.document().setTextWidth(self.viewport().width())
            margins = self.contentsMargins()
            height = int(self.document().size().height() + margins.top() + margins.bottom())

            scrollbar_height = self.horizontalScrollBar().sizeHint().height()
            height += scrollbar_height
            self.setFixedHeight(height)

    def toggle_adjust_height(self, adjust_height : bool):
        self.adjust_height = adjust_height
        try:
            self.textChanged.disconnect(self.autoResize)
        except TypeError:
            pass
        if adjust_height:
            self.textChanged.connect(self.autoResize)
            self.autoResize()
    
    def wrap_text(self, text : str, max_length : int):
        wrapped_lines = []
        markdown_pattern = re.compile(r"(\*\*.*?\*\*|`.*?`|\*.*?\*)")  # Captura texto com formatação Markdown

        for paragraph in text.strip().split("\n\n"):  # Quebra em parágrafos
            
            tokens = markdown_pattern.split(paragraph)  # Divide entre texto e tags Markdown
            line = ""
            
            for token in tokens:
                if markdown_pattern.match(token):  # Se é uma tag Markdown, trata como um bloco único
                    if len(line) + len(token) + 1 > max_length:
                        wrapped_lines.append(line)
                        line = token
                    else:
                        line += " " + token if line else token
                else:  # Se é texto normal, processa palavra por palavra
                    for word in token.split():
                        if len(line) + len(word) + 1 > max_length:
                            wrapped_lines.append(line)
                            line = word
                        else:
                            line += " " + word if line else word

            if line:
                wrapped_lines.append(line)
          
        return "\n\n".join(wrapped_lines)
    
    def setSourceWhitContent(self, content : str):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as tf:
            tf.write(content)
            tf_path = tf.name
        super().setSource(QUrl.fromLocalFile(tf_path))
        os.remove(tf_path)

    def setHtml(self, content: str):
        content = re.sub(r'(?<!\n)\n([ \t]*[*\-])', r'\n\n\1', content)
        html_body = markdown.markdown(
            content,
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "sane_lists",
                "smarty",
                "admonition",
                "attr_list",
                "def_list",
                "footnotes",
                "abbr",
            ],
            output_format="html5"
        )

        css = """
            <style>
            body {
                margin: 0;
                padding: 0;
            }

            h1, h2, h3, h4, h5, h6 {
                font-weight: 600;
                margin-top: 1em;
                margin-bottom: 0.5em;
            }

            a {
                color: #1E88E5;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }

            code {
                font-family: 'Courier New', monospace;
                background-color: rgba(128, 128, 128, 0.15);
                padding: 2px 4px;
                border-radius: 4px;
            }

            pre {
                background-color: rgba(128, 128, 128, 0.1);
                padding: 10px;
                overflow: auto;
                border-radius: 6px;
                margin: 1em 0;
            }

            pre code {
                background: none;
                padding: 0;
                display: block;
            }

            ul, ol {
                margin-left: 1.2em;
                padding-left: 0.8em;
            }

            blockquote {
                margin: 1em 0;
                padding-left: 1em;
                border-left: 3px solid rgba(128, 128, 128, 0.3);
            }

            table {
                border-collapse: collapse;
                width: 100%;
            }

            table, th, td {
                border: 1px solid rgba(128, 128, 128, 0.3);
            }

            th, td {
                padding: 6px;
                text-align: left;
            }
            </style>
        """

        full_html = f"<html><head>{css}</head><body>{html_body}</body></html>"
        super().setHtml(full_html)

    def setMarkdown(self, markdown : str):
        return self.setHtml(markdown)
    
    def setPlainText(self, text):
        return self.setHtml(text)
   
    def copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.toPlainText())

    def autoResize(self):
        if self.adjust_height:
            self.document().setTextWidth(self.viewport().width())
            margins = self.contentsMargins()
            height = int(self.document().size().height() + margins.top() + margins.bottom())

            scrollbar_height = self.horizontalScrollBar().sizeHint().height()
            height += scrollbar_height
            
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


    def mousePressEvent(self, event: QMouseEvent):
        if not self.mouse_press_parent:
            return super().mousePressEvent(event)
       
        parent = self.parentWidget()
        if parent:
            new_event = QMouseEvent(event.type(), event.position(), event.scenePosition(), event.globalPosition(),
                                    Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, event.modifiers())
            QApplication.postEvent(parent, new_event)  
        else:
            super().mousePressEvent(event)

