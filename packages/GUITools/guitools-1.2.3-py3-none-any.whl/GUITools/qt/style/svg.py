# -*- coding: latin -*-
from PySide6.QtGui import QImage, QPainter, QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer, QSvgGenerator
from PySide6.QtCore import QSize, QByteArray, Qt
from os import path

class Icon(QIcon):

    def toPixmap(self, size : int = None):
        if size:
            return self.pixmap(size)
        original_size = (32, 32)
        if self.availableSizes():
            original_size = self.availableSizes()[0]
        return self.pixmap(original_size)
    
class SVG(object):

     def string_to_icon(svg_string : str, size : QSize) -> Icon:
          byte_array = QByteArray(svg_string.encode('utf-8'))
          svg_renderer = QSvgRenderer(byte_array)
          pixmap = QPixmap(size)
          pixmap.fill(Qt.GlobalColor.transparent) 
          painter = QPainter(pixmap)
          svg_renderer.render(painter)
          painter.end()
          return Icon(pixmap)

     def image_to_string_svg(image_path: str, output_svg : str, title : str = None, ddescription : str = None):
        
          if path.exists(image_path):
               # Carregar a imagem
               image = QImage(image_path)
               if image.isNull():
                    raise ValueError(f"Erro ao carregar a imagem PNG: {image_path}")

               # Configurar o gerador SVG
               svg_gen = QSvgGenerator()
               svg_gen.setFileName(output_svg)
               svg_gen.setSize(image.size())
               svg_gen.setViewBox(image.rect())
               svg_gen.setTitle(title)
               svg_gen.setDescription(ddescription)

               # Renderizar a imagem no SVG usando QPainter
               painter = QPainter(svg_gen)
               painter.drawImage(0, 0, image)
               painter.end()
               
               # Salvar o SVG em um arquivo, se necessário
               with open(output_svg, "r", encoding="utf-8") as file:
                    svg_content = file.read()

               # Retornar o conteúdo do SVG como string
               return svg_content