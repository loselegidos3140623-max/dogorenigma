import sys
import os
import requests

# ==========================================
# 🛡️ ESPECIFICACIONES: ByEnigma2.0
# ⚙️ ENTORNO: Termux & QPython (Universal)
# ==========================================

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_ruta_almacenamiento():
    rutas_probables = [
        "/sdcard/Download",
        "/storage/emulated/0/Download",
        os.path.expanduser("~")
    ]
    for ruta in rutas_probables:
        if os.path.exists(ruta) and os.access(ruta, os.W_OK):
            return ruta
    if os.path.exists("/sdcard"):
        return "/sdcard"
    return os.getcwd()

def filtrar_por_secciones(contenido_m3u):
    secciones = {}
    lineas = contenido_m3u.split('\n')
    info_nombre = None
    info_grupo = "Sin Categoría"
    
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith("#EXTINF:") and "group-title=" in linea:
            if any(p in linea.lower() for p in ["peliculas", "movies", "vod", "24/7"]):
                try:
                    info_grupo = linea.split('group-title="')[1].split('"')[0]
                except:
                    info_grupo = "Películas Generales"
                if "," in linea:
                    info_nombre = linea.split(",")[-1].strip()
                    
        elif linea.startswith("http") and info_nombre is not None:
            if info_grupo not in secciones:
                secciones[info_grupo] = []
            secciones[info_grupo].append({
                "nombre": info_nombre,
                "url": linea
            })
            info_nombre = None
            
    return secciones

def descargar_archivo_real(url_origen, nombre_archivo):
    # 🔑 PARCHE MAESTRO: Si la URL intenta usar HTTPS pero el servidor transmite en HTTP falso
    if url_origen.startswith("https://") and ":8443" in url_origen:
        url_origen = url_origen.replace("https://", "http://")

    nombre_limpio = "".join(c for c in nombre_archivo if c.isalnum() or c in (' ', '_', '-')).rstrip()
    carpeta_destino = obtener_ruta_almacenamiento()
    ruta_completa = os.path.join(carpeta_destino, f"{nombre_limpio}.mp4")
    
    print("\n" + "─"*50)
    print(f"💎 ByEnigma2.0 | CONFIGURACIÓN DE ALMACENAMIENTO")
    print(f"📂 Destino: {ruta_completa}")
    print("─"*50)
    print("⏳ Conectando con el stream de datos...")
    
    cabeceras = {'User-Agent': 'Mozilla/5.0 (VLC; Mac OS X 10.15; rv:100.0)'}
    
    try:
        with requests.get(url_origen, headers=cabeceras, stream=True, verify=False, timeout=30) as respuesta:
            respuesta.raise_for_status()
            tamanio_total = int(respuesta.headers.get('content-length', 0))
            
            descargado = 0
            print(f"\n🚀 Descarga Iniciada | ByEnigma2.0")
            
            with open(ruta_completa, 'wb') as f:
                for chunk in respuesta.iter_content(chunk_size=1024 * 16):
                    if chunk:
                        f.write(chunk)
                        descargado += len(chunk)
                        
                        if tamanio_total > 0:
                            porcentaje = int((descargado / tamanio_total) * 100)
                            print(f"\r🚀 Progreso: {porcentaje}% [{descargado // 1024 // 1024} MB / {tamanio_total // 1024 // 1024} MB] | ByEnigma2.0", end="")
                        else:
                            print(f"\r🚀 Recibiendo datos: {descargado // 1024 // 1024} MB... | ByEnigma2.0", end="")
                            
        print(f"\n\n✅ ¡Operación Exitosa por ByEnigma2.0!")
        print(f"🎬 Video completo guardado en tu memoria interna.")
        
    except Exception as e:
        print(f"\n❌ Error crítico de red o de escritura: {e}")

def seleccionar_calidad_y_bajar(peli):
    print("\n" + "═"*50)
    print(f"⚙️ SELECTOR DE RESOLUCIÓN | ByEnigma2.0")
    print("═"*50)
    print(" [1] 📺 Calidad HD (720p)")
    print(" [2] 🎬 Calidad Full HD (1080p)")
    print(" [R] Regresar al catálogo")
    print("─"*50)
    
    opcion = input("👉 Elige calidad: ").strip()
    url_final = peli['url']
    
    if opcion == '1':
        if "1080" in url_final: url_final = url_final.replace("1080", "720")
    elif opcion == '2':
        if "720" in url_final: url_final = url_final.replace("720", "1080")
    elif opcion.upper() == 'R':
        return
        
    descargar_archivo_real(url_final, peli['nombre'])

def mostrar_menu_interno_peliculas(nombre_seccion, lista_pelis):
    limite_por_pagina = 20
    pagina_actual = 0
    total_paginas = (len(lista_pelis) - 1) // limite_por_pagina + 1

    while True:
        inicio = pagina_actual * limite_por_pagina
        fin = inicio + limite_por_pagina
        bloque_actual = lista_pelis[inicio:fin]

        print("\n" + "═"*50)
        print(f" 📂 CARPETA: {nombre_seccion} | ByEnigma2.0")
        print(f" 📄 PÁGINA {pagina_actual + 1} de {total_paginas} (Títulos {inicio + 1} al {min(fin, len(lista_pelis))})")
        print("═"*50)
        
        for i, peli in enumerate(bloque_actual, start=inicio + 1):
            print(f" [{i}] 🎥 {peli['nombre']}")
            
        print("─"*50)
        controles = []
        if pagina_actual < total_paginas - 1:
            print(" [N] ➡️ Siguiente Página")
            controles.append('N')
        if pagina_actual > 0:
            print(" [P] ⬅️ Página Anterior")
            controles.append('P')
            
        print(" [R] ↩️ Regresar al menú principal")
        print("─"*50)
        
        opcion = input("👉 Selecciona película o comando [ByEnigma2.0]: ").strip().upper()
        
        if opcion == 'R':
            break
        elif opcion == 'N' and 'N' in controles:
            pagina_actual += 1
        elif opcion == 'P' and 'P' in controles:
            pagina_actual -= 1
        elif opcion.isdigit():
            num = int(opcion)
            if 1 <= num <= len(lista_pelis):
                seleccionar_calidad_y_bajar(lista_pelis[num - 1])
                input("\nPresiona Enter para continuar...")
            else:
                print(f"\n❌ Rango incorrecto. Máximo {len(lista_pelis)}.")
        else:
            print("\n❌ Opción no válida.")

def mostrar_menu_principal_categorias(secciones):
    lista_secciones = list(secciones.keys())
    
    while True:
        print("\n" + "═"*50)
        print(" 🗂️  SISTEMA DE CATEGORÍAS AUTOMÁTICAS | ByEnigma2.0")
        print("═"*50)
        
        for indice, seccion in enumerate(lista_secciones, start=1):
            print(f" [{indice}] 📁 {seccion} ({len(secciones[seccion])} títulos)")
            
        print("─"*50)
        print(" [X] Salir del Script")
        print("─"*50)
        
        opcion = input("👉 Elige el número de carpeta: ").strip()
        
        if opcion.upper() == 'X':
            print("\nCerrando sistema... ByEnigma2.0")
            sys.exit()
        elif opcion.isdigit() and 1 <= int(opcion) <= len(lista_secciones):
            seccion_elegida = lista_secciones[int(opcion) - 1]
            mostrar_menu_interno_peliculas(seccion_elegida, secciones[seccion_elegida])
        else:
            print("\n❌ Entrada inválida.")

def iniciar_bunker():
    print("🚀 [Savage-Bunker] Motor de Red Nativo Activo | ByEnigma2.0")
    enlace_iptv = input("\n🔗 Pega el link HTTP de tu lista IPTV: ").strip()
    
    if not enlace_iptv:
        print("❌ Enlace requerido.")
        return
        
    try:
        print("\n📡 Descargando datos del servidor remoto... Espere...")
        cabeceras = {'User-Agent': 'Mozilla/5.0'}
        
        respuesta = requests.get(enlace_iptv, headers=cabeceras, verify=False, timeout=25)
        respuesta.raise_for_status()
        
        contenido_texto = respuesta.text
        secciones_mapeadas = filtrar_por_secciones(contenido_texto)
        
        if secciones_mapeadas:
            mostrar_menu_principal_categorias(secciones_mapeadas)
        else:
            print("\n❌ No se estructuró contenido multimedia legible.")
                
    except Exception as e:
        print(f"❌ Fallo en la conexión remota: {e}")

if __name__ == "__main__":
    iniciar_bunker()
