from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget

DOCS = """
<h1>Referencia rápida de SL</h1>
<p><strong>PySL</strong> es la plataforma educativa. <strong>SL</strong> es el lenguaje
imperativo y estructurado que se ejecuta de forma restringida y puede convertirse a Python.</p>
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
<h2>Operadores</h2><p>Aritméticos: <code>+ - * / // % **</code>. Comparación:
<code>== &lt;&gt; &lt; &lt;= &gt; &gt;=</code>. Lógicos: <code>y</code>, <code>o</code>, <code>no</code>,
<code>verdadero</code>, <code>falso</code>. Los comentarios empiezan con <code>//</code> al inicio de
una línea o con <code>#</code>; en medio de una expresión <code>//</code> es división entera.</p>
<h2>Vectores</h2><pre>vector notas = [90, 85, 100]
notas[0] = 95
imprimir(notas[1], len(notas))</pre><p>Los índices comienzan en cero.</p>
<h2>Funciones</h2><pre>funcion sumar(a, b)
    retornar a + b
finfuncion

inicio
    imprimir(sumar(3, 5))
fin</pre><p>Las funciones se declaran antes de <code>inicio</code>. Disponibles además:
<code>int</code>, <code>float</code>, <code>str</code>, <code>range</code>, <code>len</code>,
<code>min</code>, <code>max</code> y <code>sum</code>.</p>
<h2>Atajos del IDE</h2><p><b>Ctrl+N</b> nuevo, <b>Ctrl+O</b> abrir, <b>Ctrl+S</b> guardar,
<b>Ctrl+Mayús+S</b> guardar como, <b>F5</b> o <b>Ctrl+Enter</b> ejecutar.</p>
<h2>Errores</h2><p>Si un programa falla, la consola indica el motivo en español y el IDE resalta
la línea del error. Los nombres no pueden ser palabras reservadas de Python (<code>class</code>,
<code>import</code>, <code>lambda</code>…).</p>
<h2>Tipos educativos</h2><p>numerico, entero, real, cadena, logico y caracter. Las declaraciones son opcionales.</p>
<h2>Seguridad</h2><p>El runtime aislado solo admite expresiones, asignaciones,
condiciones, ciclos y llamadas autorizadas. No permite importar módulos ni acceder al
sistema, y aplica límites de tiempo, pasos, salida y tamaño de valores.</p>
"""


class DocsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel("Documentación")
        title.setObjectName("pageTitle")
        browser = QTextBrowser()
        browser.setHtml(DOCS)
        root.addWidget(title)
        root.addWidget(browser, 1)
