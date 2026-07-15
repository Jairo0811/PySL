from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget

DOCS = """
<h1>Referencia rápida de PySL</h1>
<p>PySL utiliza una sintaxis educativa inspirada en SL y traduce cada programa a Python restringido.</p>
<h2>Estructura</h2><pre>inicio
    imprimir("Hola")
fin</pre>
<h2>Entrada y salida</h2><pre>leer(nombre)
imprimir("Hola", nombre)</pre>
<h2>Condiciones</h2><pre>si edad &gt;= 18 entonces
    imprimir("Mayor de edad")
sino
    imprimir("Menor de edad")
finsi</pre>
<h2>Ciclos</h2><pre>para i desde 1 hasta 10
    imprimir(i)
finpara

mientras contador &lt; 5
    contador = contador + 1
finmientras</pre>
<h2>Tipos educativos</h2><p>numerico, entero, real, cadena, logico y caracter. Las declaraciones son opcionales.</p>
<h2>Seguridad</h2><p>El ejecutor solo admite expresiones, asignaciones, condiciones, ciclos y llamadas autorizadas. No permite importar módulos ni acceder al sistema.</p>
"""


class DocsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel("Documentación")
        title.setObjectName("pageTitle")
        browser = QTextBrowser(); browser.setHtml(DOCS)
        root.addWidget(title); root.addWidget(browser, 1)
