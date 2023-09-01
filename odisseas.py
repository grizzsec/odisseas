import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import webbrowser

# Debes reemplazar "YOUR_API_KEY" con tu clave de API de VirusTotal
VIRUSTOTAL_API_KEY = "YOUR_API_KEY"

# Función para realizar la búsqueda y mostrar resultados
def buscar_exploits():
    # Borra cualquier contenido previo en el cuadro de resultados
    resultados_text.delete("1.0", tk.END)

    # Obtener término de búsqueda desde el cuadro de entrada
    termino_busqueda = entrada_busqueda.get()
    plataforma = seleccion_plataforma.get()

    # URL del sitio web de Exploit Database
    url = f"https://www.exploit-db.com/search?cve={termino_busqueda}&platform={plataforma}"

    # Realiza una solicitud HTTP a la página de exploits
    response = requests.get(url)

    # Verifica si la solicitud se realizó correctamente
    if response.status_code == 200:
        # Parsea el contenido HTML de la página
        soup = BeautifulSoup(response.text, "html.parser")

        # Encuentra todos los elementos HTML que contienen información de exploits
        exploit_entries = soup.find_all("div", class_="exploitdb-search-results-row")

        # Crear una lista para almacenar los detalles de los exploits
        exploits_data = []

        # Itera a través de las entradas y extrae la información relevante
        for entry in exploit_entries:
            title = entry.find("a", class_="exploitdb-search-results-title").text.strip()
            date = entry.find("span", class_="exploitdb-search-results-date").text.strip()
            type_of_vulnerability = entry.find("span", class_="exploitdb-search-results-type").text.strip()
            exploit_url = entry.find("a", class_="exploitdb-search-results-title")["href"]

            # Agrega la información al cuadro de resultados
            resultados_text.insert(tk.END, f"Título: {title}\n")
            resultados_text.insert(tk.END, f"Fecha de Publicación: {date}\n")
            resultados_text.insert(tk.END, f"Tipo de Vulnerabilidad: {type_of_vulnerability}\n")
            resultados_text.insert(tk.END, "-" * 40 + "\n")

            # Agrega los detalles a la lista de exploits_data
            exploits_data.append({"Título": title, "Fecha de Publicación": date,
                                   "Tipo de Vulnerabilidad": type_of_vulnerability, "URL": exploit_url})

        # Almacena los detalles de los exploits para su acceso posterior
        ventana.exploits_data = exploits_data

    else:
        resultados_text.insert(tk.END, "No se pudo acceder a la página web.")

# Función para abrir los detalles de un exploit seleccionado
def abrir_detalle():
    # Obtiene el índice de la línea seleccionada
    indice_seleccionado = resultados_text.index(tk.SEL_FIRST)
    indice_linea = int(indice_seleccionado.split(".")[0]) - 1

    # Obtiene la URL del exploit correspondiente
    if 0 <= indice_linea < len(ventana.exploits_data):
        exploit_url = ventana.exploits_data[indice_linea]["URL"]
        webbrowser.open(exploit_url)

# Función para guardar resultados en un archivo CSV
def guardar_resultados_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")])
    if file_path:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Título", "Fecha de Publicación", "Tipo de Vulnerabilidad"])
            text_content = resultados_text.get("1.0", tk.END)
            lines = text_content.splitlines()
            for i in range(0, len(lines), 4):
                title = lines[i].replace("Título: ", "")
                date = lines[i + 1].replace("Fecha de Publicación: ", "")
                type_of_vulnerability = lines[i + 2].replace("Tipo de Vulnerabilidad: ", "")
                writer.writerow([title, date, type_of_vulnerability])

# Función para exportar resultados a un archivo PDF
def exportar_resultados_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])
    if file_path:
        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        text_content = resultados_text.get("1.0", tk.END)
        lines = text_content.splitlines()
        for i in range(0, len(lines), 4):
            title = lines[i].replace("Título: ", "")
            date = lines[i + 1].replace("Fecha de Publicación: ", "")
            type_of_vulnerability = lines[i + 2].replace("Tipo de Vulnerabilidad: ", "")
            c.drawString(50, 750 - i * 12, f"Título: {title}")
            c.drawString(50, 735 - i * 12, f"Fecha de Publicación: {date}")
            c.drawString(50, 720 - i * 12, f"Tipo de Vulnerabilidad: {type_of_vulnerability}")

        c.save()

# Función para limpiar el cuadro de resultados
def limpiar_resultados():
    resultados_text.delete("1.0", tk.END)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Búsqueda de Exploits en Exploit Database - Odisseas")

# Etiqueta de título
etiqueta = ttk.Label(ventana, text="Búsqueda de Exploits en Exploit Database - Odisseas", font=("Helvetica", 16))
etiqueta.pack(pady=10)

# Marco para la entrada y los botones
marco_busqueda = ttk.Frame(ventana)
marco_busqueda.pack(padx=10, pady=10)

# Etiqueta de búsqueda
etiqueta_busqueda = ttk.Label(marco_busqueda, text="Buscar por CVE o Término Clave:")
etiqueta_busqueda.grid(row=0, column=0, padx=5)

# Cuadro de entrada
entrada_busqueda = ttk.Entry(marco_busqueda, width=40)
entrada_busqueda.grid(row=0, column=1, padx=5)

# Etiqueta de selección de plataforma
etiqueta_plataforma = ttk.Label(marco_busqueda, text="Plataforma:")
etiqueta_plataforma.grid(row=0, column=2, padx=5)

# Lista desplegable de selección de plataforma
plataformas = ["", "Windows", "Linux", "Unix", "Web Apps", "Hardware"]
seleccion_plataforma = ttk.Combobox(marco_busqueda, values=plataformas)
seleccion_plataforma.grid(row=0, column=3, padx=5)
seleccion_plataforma.set("")

# Botón de búsqueda
boton_buscar = ttk.Button(marco_busqueda, text="Buscar", command=buscar_exploits)
boton_buscar.grid(row=0, column=4, padx=5)

# Cuadro de resultados
resultados_text = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=60, height=20)
resultados_text.pack(padx=10, pady=10)

# Botón para abrir detalles de un exploit
boton_abrir_detalle = ttk.Button(ventana, text="Abrir Detalles", command=abrir_detalle)
boton_abrir_detalle.pack()

# Botón para guardar resultados en formato CSV
boton_guardar_csv = ttk.Button(ventana, text="Guardar Resultados en CSV", command=guardar_resultados_csv)
boton_guardar_csv.pack()

# Botón para exportar resultados a un archivo PDF
boton_exportar_pdf = ttk.Button(ventana, text="Exportar Resultados a PDF", command=exportar_resultados_pdf)
boton_exportar_pdf.pack()

# Botón para limpiar resultados
boton_limpiar = ttk.Button(ventana, text="Limpiar Resultados", command=limpiar_resultados)
boton_limpiar.pack()

# Etiqueta de autor y derechos reservados
etiqueta_autor = ttk.Label(ventana, text="Creado por Christian - Todos los derechos reservados")
etiqueta_autor.pack(pady=10)

# Etiqueta de instrucciones
etiqueta_instrucciones = ttk.Label(ventana, text="Instrucciones: Ingrese un CVE o término clave para buscar. "
                                                  "Puede filtrar por plataforma. "
                                                  "Haga clic en 'Buscar' para obtener resultados. "
                                                  "Seleccione una línea y haga clic en 'Abrir Detalles' para ver más información.")
etiqueta_instrucciones.pack(pady=10)

# Etiqueta y entrada para la API de VirusTotal
etiqueta_api_key = ttk.Label(ventana, text="API de VirusTotal:")
etiqueta_api_key.pack()
api_key_entry = ttk.Entry(ventana, show="*")  # Oculta la clave API
api_key_entry.pack()

# Botón para analizar archivo en VirusTotal
boton_analizar_archivo = ttk.Button(ventana, text="Analizar Archivo en VirusTotal", command=analizar_archivo)
boton_analizar_archivo.pack()

# Iniciar la interfaz gráfica
ventana.mainloop()
