import os
import re
import json
import msal
import requests
import xlwings as xw
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno desde el directorio padre
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

CLIENT_ID = os.getenv('MS_GRAPH_CLIENT_ID')
TENANT_ID = os.getenv('MS_GRAPH_TENANT_ID')
CLIENT_SECRET = os.getenv('MS_GRAPH_CLIENT_SECRET')

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# Colores de Resaltado Visual
COLOR_PLANNER_NEW = (255, 230, 153) # Naranja claro (Planner tiene datos nuevos)
COLOR_EXCEL_NEW = (189, 215, 238)   # Azul claro (Excel tiene cambios locales)
COLOR_CONFLICT = (248, 203, 173)    # Rojo claro (Ambos cambiaron)
COLOR_DEFAULT = (255, 255, 255)     # Blanco/Sin color

def get_access_token():
    """Obtiene el token de acceso de Microsoft Graph usando MSAL."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"No se pudo adquirir el token: {result.get('error_description')}")

def graph_get(url, token):
    """Realiza una petición GET a Microsoft Graph API."""
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def graph_patch(url, token, data, etag):
    """Realiza una petición PATCH a Microsoft Graph API con If-Match (ETag)."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'If-Match': etag
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def parse_description(description):
    """
    Analiza la descripción de una tarea en busca de etiquetas ##Clave: Valor.
    Soporta alias como ##Dinero, ##Fecha y booleanos (ON/OFF).
    """
    if not description:
        return {}
    
    tags = {}
    # Patrón para encontrar ##Clave: Valor o ##Clave Valor
    # Asegura que se detenga antes de la siguiente etiqueta ## o del final de la línea
    matches = re.finditer(r'##([\w\$\-]+)(?:[:\s=]+)(.*?)(?=\s*##|$)', description)
    
    for match in matches:
        key = match.group(1).strip()
        value = match.group(2).strip()
        
        # Alias Amigables
        if key == '$' or key.lower() == 'dinero': 
            key = 'Dinero'
            try: 
                # Buscar el primer número en el valor (ignora $, texto extra, etc.)
                num_match = re.search(r'[\d,.]+', value)
                if num_match:
                    value = float(num_match.group(0).replace(',', ''))
            except: pass
        elif key == 'F' or key.lower() == 'fecha': 
            key = 'Fecha'
            try: value = datetime.strptime(value.strip(), '%Y-%m-%d')
            except: pass
        elif key == 'D' or key.lower() == 'desc': 
            key = 'Descripcion_Extra'
        elif key.startswith('B-') or key.lower().startswith('check'):
            key = key.replace('B-', '').replace('Check-', '').replace('check-', '')
            value = value.upper().strip() in ['ON', 'TRUE', '1', 'SI', 'YES']
        elif key.startswith('PR-') or key.startswith('PG-') or key == 'PS':
            try: 
                num_match = re.search(r'[\d,.]+', value)
                if num_match:
                    value = float(num_match.group(0).replace(',', ''))
            except: pass
            
        tags[key] = value
    return tags

def sync(mode="full"):
    """
    Modos de sincronización:
    - "full": Actualiza todos los datos y aplica estilos Premium.
    - "compare": Solo resalta diferencias usando ETags sin sobrescribir Excel.
    """
    try:
        print(f"Iniciando sincronización en modo {mode}...")
        token = get_access_token()
        
        # Obteniendo Planes
        plans_data = graph_get("https://graph.microsoft.com/v1.0/planner/plans", token)
        plans = plans_data.get('value', [])
        
        all_planner_tasks = {} # Diccionario para indexar tareas por ID
        all_dynamic_cols = set() # Conjunto para rastrear columnas dinámicas únicas
        
        for plan in plans:
            plan_id = plan['id']
            plan_name = plan['title']
            
            # Obteniendo Buckets (Cubetas)
            buckets_data = graph_get(f"https://graph.microsoft.com/v1.0/planner/plans/{plan_id}/buckets", token)
            buckets = buckets_data.get('value', [])
            
            for bucket in buckets:
                bucket_name = bucket['name']
                bucket_id = bucket['id']
                
                # Obteniendo Tareas de la cubeta
                tasks_data = graph_get(f"https://graph.microsoft.com/v1.0/planner/buckets/{bucket_id}/tasks", token)
                tasks = tasks_data.get('value', [])
                
                for task in tasks:
                    task_id = task['id']
                    # Detalles de la tarea para obtener la descripción
                    details = graph_get(f"https://graph.microsoft.com/v1.0/planner/tasks/{task_id}/details", token)
                    description = details.get('description', '')
                    
                    parsed_tags = parse_description(description)
                    all_dynamic_cols.update(parsed_tags.keys())
                    
                    percent = task.get('percentComplete', 0)
                    all_planner_tasks[task_id] = {
                        "Task ID": task_id,
                        "Plan ID": plan_id,
                        "Plan Name": plan_name,
                        "Bucket Name": bucket_name,
                        "Task Title": task.get('title', ''),
                        "Status": "Completada" if percent == 100 else ("Iniciada" if percent > 0 else "No Iniciada"),
                        "ETag": task.get('@odata.etag', ''),
                        **parsed_tags
                    }
        
        # Integración con Excel
        try:
            wb = xw.Book.caller()
        except Exception:
            wb = xw.books.active
        sheet = wb.sheets.active
        
        # Asegurar Encabezados base
        base_headers = ["Task ID", "Plan Name", "Bucket Name", "Task Title", "Status", "ETag"]
        existing_headers = sheet.range('A1').expand('right').value
        
        if not existing_headers or existing_headers == [None] or isinstance(existing_headers, str):
            existing_headers = base_headers
        if isinstance(existing_headers, str): existing_headers = [existing_headers]
        
        # Añadir columnas dinámicas detectadas
        for col in sorted(list(all_dynamic_cols)):
            if col not in existing_headers:
                existing_headers.append(col)
        
        sheet.range('A1').value = existing_headers
        
        # Mapeo de columnas para indexación rápida
        header_map = {h: i for i, h in enumerate(existing_headers)}
        id_col_idx = header_map.get("Task ID", 0)
        etag_col_idx = header_map.get("ETag", 5)
        
        # Cargar datos existentes de Excel para comparación
        last_row_idx = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        excel_data = {}
        if last_row_idx > 1:
            rows = sheet.range(f'A2:{xw.utils.col_name(len(existing_headers))}{last_row_idx}').value
            if last_row_idx == 2: rows = [rows] # Ajuste para fila única
            for r_idx, row in enumerate(rows):
                if row and row[id_col_idx]:
                    excel_data[row[id_col_idx]] = {"row_idx": r_idx + 2, "data": row}

        # Procesamiento de Cambios
        data_to_write = []
        rows_to_highlight = {} # indice_fila: color
        
        if mode == "full":
            # Reconstruir matriz de datos y escribir todo
            for t_id, t_info in all_planner_tasks.items():
                row_list = [t_info.get(h, "") for h in existing_headers]
                data_to_write.append(row_list)
            
            if last_row_idx > 1:
                sheet.range(f'A2:ZZ{last_row_idx}').clear_contents()
                sheet.range(f'A2:ZZ{last_row_idx}').color = None
            
            if data_to_write:
                sheet.range('A2').value = data_to_write
            
            apply_premium_styling(sheet)
            print(f"Sincronización completa. {len(data_to_write)} tareas actualizadas.")

        elif mode == "compare":
            # Lógica de comparación inteligente (Semáforo completo)
            title_col_idx = header_map.get("Task Title", 3)
            status_col_idx = header_map.get("Status", 4)

            for t_id, p_task in all_planner_tasks.items():
                if t_id in excel_data:
                    e_task_row = excel_data[t_id]
                    e_row_idx = e_task_row["row_idx"]
                    e_etag = e_task_row["data"][etag_col_idx]
                    e_title = e_task_row["data"][title_col_idx] if title_col_idx < len(e_task_row["data"]) else ""
                    e_status = e_task_row["data"][status_col_idx] if status_col_idx < len(e_task_row["data"]) else ""

                    planner_changed = (p_task["ETag"] != e_etag)
                    excel_changed = (e_title != p_task.get("Task Title", "")) or (e_status != p_task.get("Status", ""))

                    if planner_changed and excel_changed:
                        # Both sides changed — CONFLICT
                        rows_to_highlight[e_row_idx] = COLOR_CONFLICT
                    elif planner_changed:
                        # Only Planner changed
                        rows_to_highlight[e_row_idx] = COLOR_PLANNER_NEW
                    elif excel_changed:
                        # Only Excel was edited locally
                        rows_to_highlight[e_row_idx] = COLOR_EXCEL_NEW
                    else:
                        rows_to_highlight[e_row_idx] = COLOR_DEFAULT

            # Aplicar Resaltado Visual
            for r_idx, color in rows_to_highlight.items():
                sheet.range(f'{r_idx}:{r_idx}').color = color

            print("Comparación finalizada. Resaltado aplicado en Excel.")

        elif mode == "push":
            # Lógica de Push: Excel → Planner (con If-Match ETag)
            title_col_idx = header_map.get("Task Title", 3)
            status_col_idx = header_map.get("Status", 4)
            pushed = 0
            errors = 0

            for t_id, e_info in excel_data.items():
                e_row_idx = e_info["row_idx"]
                e_data = e_info["data"]
                e_etag = e_data[etag_col_idx] if etag_col_idx < len(e_data) else None

                if not t_id or not e_etag:
                    continue

                e_title = e_data[title_col_idx] if title_col_idx < len(e_data) else ""
                e_status = e_data[status_col_idx] if status_col_idx < len(e_data) else ""

                # Convert status text back to percentComplete
                if e_status == "Completada":
                    percent = 100
                elif e_status == "Iniciada":
                    percent = 50
                else:
                    percent = 0

                patch_body = {
                    "title": e_title,
                    "percentComplete": percent
                }

                try:
                    result = graph_patch(
                        f"https://graph.microsoft.com/v1.0/planner/tasks/{t_id}",
                        token, patch_body, e_etag
                    )
                    # Update ETag in Excel with the new one from server
                    new_etag = result.get('@odata.etag', e_etag)
                    sheet.range(f'{xw.utils.col_name(etag_col_idx + 1)}{e_row_idx}').value = new_etag
                    pushed += 1
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 412:
                        # Precondition Failed — someone else modified the task
                        sheet.range(f'{e_row_idx}:{e_row_idx}').color = COLOR_CONFLICT
                    errors += 1
                    print(f"Error al subir tarea {t_id}: {e}")
                except Exception as e:
                    errors += 1
                    print(f"Error inesperado en tarea {t_id}: {e}")

            print(f"Push finalizado. {pushed} tareas subidas, {errors} errores.")

    except Exception as e:
        print(f"ERROR: {e}")
        try: xw.books.active.sheets.active.range('A1').status_bar = f"Error: {e}"
        except: pass

def apply_premium_styling(sheet):
    """Aplica formato visual de alta calidad a la hoja de Excel."""
    header_range = sheet.range('1:1')
    header_range.api.Font.Bold = True
    header_range.api.Font.Color = 0xFFFFFF # Blanco
    header_range.color = (0, 32, 96) # Azul Oscuro
    
    sheet.autofit() # Auto-ajustar columnas
    
    # Congelar la fila de encabezados
    sheet.api.Application.ActiveWindow.FreezePanes = False
    sheet.range('A2').select()
    sheet.api.Application.ActiveWindow.FreezePanes = True

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "full"
    if arg not in ("full", "compare", "push"):
        print(f"Modo desconocido: {arg}. Usa: full, compare, push")
    else:
        sync(arg)
