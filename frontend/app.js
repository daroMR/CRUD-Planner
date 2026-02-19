// URL base de la API
const api = 'http://localhost:8000';

// -----------------------------
// Logging & UI State
// -----------------------------

function log(msg, type = 'info') {
    const logDiv = document.getElementById('log');
    if (!logDiv) return;
    const time = new Date().toLocaleTimeString();
    const color = type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#a5b4fc';
    logDiv.innerHTML += `<div><span style="color: #64748b">[${time}]</span> <span style="color: ${color}">${msg}</span></div>`;
    logDiv.scrollTop = logDiv.scrollHeight;
}

function showLoading(show) {
    const btn = document.querySelector('.btn-primary');
    if (btn) {
        if (show) {
            btn.innerHTML = '<span class="icon animate-spin">⏳</span> Cargando...';
            btn.disabled = true;
        } else {
            btn.innerHTML = '<span class="icon">🔄</span> Recargar Resumen';
            btn.disabled = false;
        }
    }
}

// -----------------------------
// Resumen (GraphQL)
// -----------------------------

async function graphqlRequest(query, variables = {}) {
    try {
        const res = await fetch(`${api}/graphql`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, variables })
        });
        return await res.json();
    } catch (e) {
        log('Error en conexión GraphQL: ' + e.message, 'error');
        throw e;
    }
}

function renderResumenJson(payload) {
    const pre = document.getElementById('resumenJson');
    if (!pre) return;
    pre.textContent = JSON.stringify(payload, null, 2);
}

function renderResumenArbol(plans) {
    const root = document.getElementById('resumenArbol');
    if (!root) return;
    root.innerHTML = '';

    const ul = document.createElement('ul');
    ul.className = 'tree-list';

    (plans || []).forEach(p => {
        const liPlan = document.createElement('li');
        liPlan.innerHTML = `<span class="tree-node plan-node">📁 Plan: <strong>${p.name}</strong> <small>(#${p.id})</small></span>`;

        const ulBuckets = document.createElement('ul');
        (p.buckets || []).forEach(b => {
            const liBucket = document.createElement('li');
            liBucket.innerHTML = `<span class="tree-node bucket-node">🗄️ Bucket: ${b.name}</span>`;

            const ulTasks = document.createElement('ul');
            (b.tasks || []).forEach(t => {
                const liTask = document.createElement('li');
                const progressColor = t.percentComplete === 100 ? '#10b981' : '#3b82f6';
                liTask.innerHTML = `
                    <span class="tree-node task-node">
                        📝 ${t.title} 
                        <span class="progress-pill" style="background: ${progressColor}">${t.percentComplete}%</span>
                    </span>`;
                ulTasks.appendChild(liTask);
            });

            liBucket.appendChild(ulTasks);
            ulBuckets.appendChild(liBucket);
        });

        liPlan.appendChild(ulBuckets);
        ul.appendChild(liPlan);
    });

    root.appendChild(ul);
}

async function cargarResumenPlanner() {
    showLoading(true);
    const query = `
    query PlannerSummary {
      plans {
        id
        name
        buckets {
          id
          name
          planId
          tasks {
            id
            title
            percentComplete
            bucketId
            planId
          }
        }
      }
    }
  `;

    try {
        const payload = await graphqlRequest(query);
        if (payload.errors) {
            renderResumenJson(payload);
            log('Errores en GraphQL', 'error');
        } else {
            renderResumenJson(payload.data);
            renderResumenArbol(payload.data?.plans || []);
            log('Datos sincronizados correctamente', 'success');
        }
    } catch (e) {
        log('Fallo al cargar resumen: ' + e.message, 'error');
    } finally {
        showLoading(false);
    }
}

// -----------------------------
// CRUD Functions
// -----------------------------

function renderTable(tableId, data, columns, filterFn) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody) return;
    tbody.innerHTML = '';
    
    const filteredData = filterFn ? data.filter(filterFn) : data;
    
    filteredData.forEach(item => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = item[col];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

async function listarPlanes() {
    try {
        const res = await fetch(`${api}/plans`);
        const data = await res.json();
        const filtro = document.getElementById('filtroPlan').value.toLowerCase();
        renderTable('tablaPlanes', data, ['id', 'name'], p => p.name.toLowerCase().includes(filtro));
        log('Planes listados', 'info');
    } catch (e) { log('Error al listar planes', 'error'); }
}

async function listarBuckets() {
    try {
        const res = await fetch(`${api}/buckets`);
        const data = await res.json();
        const nameFeltro = document.getElementById('filtroBucket').value.toLowerCase();
        const planIdFeltro = document.getElementById('filtroBucketPlanId').value;
        
        renderTable('tablaBuckets', data, ['id', 'name', 'plan_id'], b => 
            b.name.toLowerCase().includes(nameFeltro) && 
            (planIdFeltro === '' || b.plan_id === parseInt(planIdFeltro))
        );
        log('Buckets listados', 'info');
    } catch (e) { log('Error al listar buckets', 'error'); }
}

async function listarTareas() {
    try {
        const res = await fetch(`${api}/tasks`);
        const data = await res.json();
        const titleFeltro = document.getElementById('filtroTarea').value.toLowerCase();
        const bucketIdFeltro = document.getElementById('filtroTareaBucketId').value;
        const planIdFeltro = document.getElementById('filtroTareaPlanId').value;

        renderTable('tablaTareas', data, ['id', 'title', 'percent_complete', 'bucket_id', 'plan_id'], t => 
            t.title.toLowerCase().includes(titleFeltro) &&
            (bucketIdFeltro === '' || t.bucket_id === parseInt(bucketIdFeltro)) &&
            (planIdFeltro === '' || t.plan_id === parseInt(planIdFeltro))
        );
        log('Tareas listadas', 'info');
    } catch (e) { log('Error al listar tareas', 'error'); }
}

async function apiPost(endpoint, body) {
    const res = await fetch(`${api}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function crearPlan() {
    const name = document.getElementById('planName');
    const id = document.getElementById('planId');
    if (!name.value || !id.value) return log('Nombre e ID son obligatorios', 'error');
    
    try {
        await apiPost('/plans', { id: parseInt(id.value), name: name.value });
        log(`Plan "${name.value}" creado`, 'success');
        listarPlanes();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function crearBucket() {
    const name = document.getElementById('bucketName');
    const id = document.getElementById('bucketId');
    const planId = document.getElementById('bucketPlanId');
    if (!name.value || !id.value || !planId.value) return log('Faltan campos obligatorios', 'error');

    try {
        await apiPost('/buckets', { id: parseInt(id.value), name: name.value, plan_id: parseInt(planId.value) });
        log(`Bucket "${name.value}" creado`, 'success');
        listarBuckets();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function crearTarea() {
    const title = document.getElementById('taskTitle');
    const id = document.getElementById('taskId');
    const bId = document.getElementById('taskBucketId');
    const pId = document.getElementById('taskPlanId');
    const pc = document.getElementById('taskPercent');

    try {
        await apiPost('/tasks', {
            id: parseInt(id.value),
            title: title.value,
            bucket_id: parseInt(bId.value),
            plan_id: parseInt(pId.value),
            percent_complete: parseInt(pc.value)
        });
        log(`Tarea "${title.value}" creada`, 'success');
        listarTareas();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function actualizarTarea() {
    const id = document.getElementById('updateTaskId').value;
    const title = document.getElementById('updateTaskTitle').value;
    const pc = document.getElementById('updateTaskPercent').value;
    const bId = document.getElementById('updateTaskBucketId').value;
    const pId = document.getElementById('updateTaskPlanId').value;

    try {
        const res = await fetch(`${api}/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: parseInt(id),
                title,
                percent_complete: parseInt(pc),
                bucket_id: parseInt(bId),
                plan_id: parseInt(pId)
            })
        });
        if (!res.ok) throw new Error(await res.text());
        log(`Tarea #${id} actualizada`, 'success');
        listarTareas();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function eliminarTarea() {
    const id = document.getElementById('deleteTaskId').value;
    if (!id) return log('ID de tarea requerido', 'error');
    
    try {
        const res = await fetch(`${api}/tasks/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error(await res.text());
        log(`Tarea #${id} eliminada`, 'success');
        listarTareas();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

window.onload = () => {
    cargarResumenPlanner();
    listarPlanes();
    listarBuckets();
    listarTareas();
    log('Dashboard inicializado', 'info');
};
