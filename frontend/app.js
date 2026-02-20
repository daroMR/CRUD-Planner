// URL base de la API
// URL base de la API — Detecta si estás en local o en Render automáticamente
const api = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : window.location.origin;


// -----------------------------
// Logging, UI State & Global Data
// -----------------------------

let currentPlans = [];
let currentBuckets = [];
let currentTasks = [];

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

async function refreshAll() {
    log('Actualizando todos los datos...', 'info');
    await cargarResumenPlanner();
    await listarPlanes();
    await listarBuckets();
    await listarTareas();
}

function renderMasterTable(plansInput) {
    const tbody = document.getElementById('masterTableBody');
    if (!tbody) return;

    // Si se pasan planes, los guardamos en una variable global para la búsqueda reactiva
    if (plansInput) window.lastHierarchicalData = plansInput;
    const plans = plansInput || window.lastHierarchicalData || [];

    const search = (document.getElementById('masterSearch')?.value || '').toLowerCase();
    tbody.innerHTML = '';

    plans.forEach(p => {
        (p.buckets || []).forEach(b => {
            (b.tasks || []).forEach(t => {
                const searchStr = `${p.name} ${b.name} ${t.title} ${t.id}`.toLowerCase();
                if (search && !searchStr.includes(search)) return;

                const tr = document.createElement('tr');
                const progressColor = t.percentComplete === 100 ? '#10b981' : '#3b82f6';

                tr.innerHTML = `
                    <td><strong>${p.name}</strong></td>
                    <td>${b.name}</td>
                    <td>${t.title}</td>
                    <td><span class="progress-pill" style="background: ${progressColor}">${t.percentComplete}%</span></td>
                    <td style="font-size: 0.7rem; color: #64748b; font-family: 'Fira Code', monospace;">
                        P: ${p.id}<br>B: ${b.id}<br>T: ${t.id}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
    });
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
            const plans = payload.data?.plans || [];
            renderResumenJson(payload.data);
            renderResumenArbol(plans);
            renderMasterTable(plans);
            log('Resumen sincronizado', 'success');
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
        currentPlans = data;
        populateSelects();
        log('Planes listados', 'info');
    } catch (e) { log('Error en listarPlanes: ' + e.message, 'error'); }
}

async function listarBuckets() {
    try {
        const res = await fetch(`${api}/buckets`);
        const data = await res.json();
        currentBuckets = data;
        populateSelects();
        log('Buckets listados', 'info');
    } catch (e) { log('Error en listarBuckets: ' + e.message, 'error'); }
}

async function listarTareas() {
    try {
        const res = await fetch(`${api}/tasks`);
        const data = await res.json();
        currentTasks = data;
        populateSelects();
        log('Tareas listadas', 'info');
    } catch (e) { log('Error en listarTareas: ' + e.message, 'error'); }
}

// -----------------------------
// UI Helper Functions
// -----------------------------

function populateSelects() {
    fillSelect('managePlanId', currentPlans, 'id', 'name', 'Seleccionar Plan...');
    fillSelect('bucketPlanId', currentPlans, 'id', 'name', 'Seleccionar Plan...');
    fillSelect('taskPlanId', currentPlans, 'id', 'name', 'Seleccionar Plan...');
    fillSelect('manageBucketPlanId', currentPlans, 'id', 'name', 'Plan Asociado...');
    fillSelect('updateTaskPlanId', currentPlans, 'id', 'name', 'Plan...');

    fillSelect('manageBucketId', currentBuckets, 'id', 'name', 'Seleccionar Bucket...');
    fillSelect('updateTaskId', currentTasks, 'id', 'title', 'Seleccionar Tarea...');
    fillSelect('deleteTaskId', currentTasks, 'id', 'title', 'Seleccionar Tarea...');
}

function fillSelect(elemId, data, valKey, textKey, defaultText) {
    const sel = document.getElementById(elemId);
    if (!sel) return;
    const currentVal = sel.value;
    sel.innerHTML = `<option value="">${defaultText}</option>`;
    data.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item[valKey];
        opt.textContent = `${item[textKey]} (${item[valKey]})`;
        sel.appendChild(opt);
    });
    if (data.some(d => String(d[valKey]) === currentVal)) sel.value = currentVal;
}

function fillPlanData() {
    const id = document.getElementById('managePlanId').value;
    const plan = currentPlans.find(p => String(p.id) === id);
    if (plan) {
        document.getElementById('managePlanName').value = plan.name;
    }
}

function fillBucketData() {
    const id = document.getElementById('manageBucketId').value;
    const bucket = currentBuckets.find(b => String(b.id) === id);
    if (bucket) {
        document.getElementById('manageBucketName').value = bucket.name;
        document.getElementById('manageBucketPlanId').value = bucket.plan_id;
    }
}

function fillTaskData() {
    const id = document.getElementById('updateTaskId').value;
    const task = currentTasks.find(t => String(t.id) === id);
    if (task) {
        document.getElementById('updateTaskTitle').value = task.title;
        document.getElementById('updateTaskPercent').value = task.percent_complete;
        document.getElementById('updateTaskPlanId').value = task.plan_id;
        updateBucketSelect('updateTaskPlanId', 'updateTaskBucketId');
        document.getElementById('updateTaskBucketId').value = task.bucket_id;
    }
}

function updateBucketSelect(planSelId, bucketSelId) {
    const planId = document.getElementById(planSelId).value;
    const filteredBuckets = currentBuckets.filter(b => !planId || String(b.plan_id) === planId);
    fillSelect(bucketSelId, filteredBuckets, 'id', 'name', 'Seleccionar Bucket...');
}

async function apiDelete(endpoint) {
    const res = await fetch(`${api}${endpoint}`, {
        method: 'DELETE'
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Fallo en DELETE');
    }
    return res.json();
}

async function apiPut(endpoint, body) {
    const res = await fetch(`${api}${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Fallo en PUT');
    }
    return res.json();
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
        await apiPost('/plans', { id: id.value, name: name.value });
        log(`Plan "${name.value}" creado`, 'success');
        listarPlanes();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function actualizarPlan() {
    const id = document.getElementById('managePlanId').value;
    const name = document.getElementById('managePlanName').value;
    if (!id || !name) return log('ID y Nombre son obligatorios', 'error');

    try {
        await apiPut(`/plans/${id}`, { name });
        log(`Plan ${id} actualizado`, 'success');
        listarPlanes();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function eliminarPlan() {
    const id = document.getElementById('managePlanId').value;
    if (!id) return log('ID es obligatorio', 'error');
    if (!confirm('¿Estás seguro de eliminar este plan (Local)? Nota: Microsoft Graph no permite borrar planes directamente.')) return;

    try {
        await apiDelete(`/plans/${id}`);
        log(`Plan ${id} eliminado`, 'success');
        listarPlanes();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function crearBucket() {
    const name = document.getElementById('bucketName');
    const id = document.getElementById('bucketId');
    const planId = document.getElementById('bucketPlanId');
    if (!name.value || !id.value || !planId.value) return log('Faltan campos obligatorios', 'error');

    try {
        await apiPost('/buckets', { id: id.value, name: name.value, plan_id: planId.value });
        log(`Bucket "${name.value}" creado`, 'success');
        listarBuckets();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function actualizarBucket() {
    const id = document.getElementById('manageBucketId').value;
    const name = document.getElementById('manageBucketName').value;
    const planId = document.getElementById('manageBucketPlanId').value;
    if (!id || !name) return log('ID y Nombre son obligatorios', 'error');

    try {
        await apiPut(`/buckets/${id}`, { name, plan_id: planId || "" });
        log(`Bucket ${id} actualizado`, 'success');
        listarBuckets();
    } catch (e) { log('Error: ' + e.message, 'error'); }
}

async function eliminarBucket() {
    const id = document.getElementById('manageBucketId').value;
    if (!id) return log('ID es obligatorio', 'error');
    if (!confirm('¿Estás seguro de eliminar este bucket?')) return;

    try {
        await apiDelete(`/buckets/${id}`);
        log(`Bucket ${id} eliminado`, 'success');
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
            id: id.value,
            title: title.value,
            bucket_id: bId.value,
            plan_id: pId.value,
            percent_complete: parseInt(pc.value) || 0
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

// -----------------------------
// Autenticación (MS Graph)
// -----------------------------

async function verificarAuth() {
    try {
        const res = await fetch(`${api}/auth/status`);
        const data = await res.json();
        const loginBtn = document.getElementById('loginBtn');
        const userInfo = document.getElementById('userInfo');
        const userName = document.getElementById('userName');

        if (data.authenticated) {
            loginBtn.style.display = 'none';
            userInfo.style.display = 'block';
            userName.textContent = data.user || 'Planner Conectado';
            log('Sesión activa en Microsoft Graph', 'success');
            return true;
        } else {
            loginBtn.style.display = 'block';
            userInfo.style.display = 'none';
            return false;
        }
    } catch (e) {
        console.error('Error verificando auth', e);
        return false;
    }
}

async function iniciarSesion() {
    try {
        log('Iniciando flujo de autenticación...', 'info');
        const res = await fetch(`${api}/auth/login`);
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Fallo al iniciar sesión');
        }
        const flow = await res.json();

        if (!flow || !flow.user_code) {
            throw new Error('No se recibió código de autenticación');
        }

        // Mostrar Modal
        document.getElementById('authCode').textContent = flow.user_code;
        document.getElementById('authUrl').href = flow.verification_uri || '#';
        document.getElementById('authModal').style.display = 'block';
        document.getElementById('modalOverlay').style.display = 'block';

        // Poll para completar
        const pollInterval = setInterval(async () => {
            try {
                const completeRes = await fetch(`${api}/auth/complete`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(flow)
                });
                const result = await completeRes.json();

                if (result.status === 'success') {
                    clearInterval(pollInterval);
                    document.getElementById('authModal').style.display = 'none';
                    document.getElementById('modalOverlay').style.display = 'none';
                    log(`Bienvenido, ${result.user}!`, 'success');
                    verificarAuth();
                    refreshAll();
                } else if (result.status === 'error' && result.detail !== 'authorization_pending') {
                    clearInterval(pollInterval);
                    log('Error en autenticación: ' + result.detail, 'error');
                }
            } catch (e) {
                console.error('Error polling auth', e);
            }
        }, 5000);

    } catch (e) {
        log('Error al iniciar sesión: ' + e.message, 'error');
    }
}

window.onload = async () => {
    log('Dashboard inicializando...', 'info');
    const autenticado = await verificarAuth();
    await refreshAll();
    if (autenticado) {
        log('Conexión con Planner establecida', 'success');
    } else {
        log('Modo local (Sin conexión a Microsoft)', 'info');
    }
};
