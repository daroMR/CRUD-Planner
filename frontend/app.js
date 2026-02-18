// URL base de la API
const api = 'http://localhost:8000';

// -----------------------------
// Resumen inicial (GraphQL)
// -----------------------------

async function graphqlRequest(query, variables = {}) {
  const res = await fetch(`${api}/graphql`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables })
  });
  return await res.json();
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

  (plans || []).forEach(p => {
    const liPlan = document.createElement('li');
    liPlan.textContent = `Plan #${p.id} - ${p.name}`;

    const ulBuckets = document.createElement('ul');
    (p.buckets || []).forEach(b => {
      const liBucket = document.createElement('li');
      liBucket.textContent = `Bucket #${b.id} - ${b.name}`;

      const ulTasks = document.createElement('ul');
      (b.tasks || []).forEach(t => {
        const liTask = document.createElement('li');
        liTask.textContent = `Task #${t.id} - ${t.title} (${t.percentComplete}%)`;
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
      log('GraphQL (resumen) devolvió errores: ' + JSON.stringify(payload.errors));
      return;
    }

    renderResumenJson(payload.data);
    renderResumenArbol(payload.data?.plans || []);
    log('Resumen GraphQL actualizado');
  } catch (e) {
    log('Error cargar resumen GraphQL: ' + e);
  }
}

// Función para mostrar mensajes en el panel de logs
function log(msg) {
  const logDiv = document.getElementById('log');
  logDiv.innerHTML += `<div>${new Date().toLocaleTimeString()} - ${msg}</div>`;
  logDiv.scrollTop = logDiv.scrollHeight;
}

// Renderiza la tabla de planes con filtro por nombre
function renderTablaPlanes(planes) {
  const filtro = document.getElementById('filtroPlan').value.toLowerCase();
  const tbody = document.querySelector('#tablaPlanes tbody');
  tbody.innerHTML = '';
  planes.filter(p => p.name.toLowerCase().includes(filtro)).forEach(p => {
    tbody.innerHTML += `<tr><td>${p.id}</td><td>${p.name}</td></tr>`;
  });
}
// Renderiza la tabla de buckets con filtros por nombre y plan_id
function renderTablaBuckets(buckets) {
  const filtro = document.getElementById('filtroBucket').value.toLowerCase();
  const filtroPlanId = document.getElementById('filtroBucketPlanId').value;
  const tbody = document.querySelector('#tablaBuckets tbody');
  tbody.innerHTML = '';
  buckets.filter(b =>
    b.name.toLowerCase().includes(filtro) &&
    (filtroPlanId === '' || b.plan_id === parseInt(filtroPlanId))
  ).forEach(b => {
    tbody.innerHTML += `<tr><td>${b.id}</td><td>${b.name}</td><td>${b.plan_id}</td></tr>`;
  });
}
// Renderiza la tabla de tareas con filtros por título, bucket_id y plan_id
function renderTablaTareas(tareas) {
  const filtro = document.getElementById('filtroTarea').value.toLowerCase();
  const filtroBucketId = document.getElementById('filtroTareaBucketId').value;
  const filtroPlanId = document.getElementById('filtroTareaPlanId').value;
  const tbody = document.querySelector('#tablaTareas tbody');
  tbody.innerHTML = '';
  tareas.filter(t =>
    t.title.toLowerCase().includes(filtro) &&
    (filtroBucketId === '' || t.bucket_id === parseInt(filtroBucketId)) &&
    (filtroPlanId === '' || t.plan_id === parseInt(filtroPlanId))
  ).forEach(t => {
    tbody.innerHTML += `<tr><td>${t.id}</td><td>${t.title}</td><td>${t.percent_complete}</td><td>${t.bucket_id}</td><td>${t.plan_id}</td></tr>`;
  });
}

// Validación de formularios antes de enviar datos
function validarCampos(campos) {
  for (const c of campos) {
    if (c.value === '' || c.value === null) {
      log(`El campo "${c.name}" es obligatorio.`);
      c.focus();
      return false;
    }
  }
  return true;
}
// Crear un nuevo plan
async function crearPlan() {
  const name = document.getElementById('planName');
  const id = document.getElementById('planId');
  if (!validarCampos([name, id])) return;
  try {
    const res = await fetch(`${api}/plans`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: parseInt(id.value), name: name.value })
    });
    log('Crear Plan: ' + await res.text());
    listarPlanes();
  } catch (e) { log('Error crear plan: ' + e); }
}
// Crear un nuevo bucket
async function crearBucket() {
  const name = document.getElementById('bucketName');
  const id = document.getElementById('bucketId');
  const plan_id = document.getElementById('bucketPlanId');
  if (!validarCampos([name, id, plan_id])) return;
  try {
    const res = await fetch(`${api}/buckets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: parseInt(id.value), name: name.value, plan_id: parseInt(plan_id.value) })
    });
    log('Crear Bucket: ' + await res.text());
    listarBuckets();
  } catch (e) { log('Error crear bucket: ' + e); }
}
// Crear una nueva tarea
async function crearTarea() {
  const title = document.getElementById('taskTitle');
  const id = document.getElementById('taskId');
  const bucket_id = document.getElementById('taskBucketId');
  const plan_id = document.getElementById('taskPlanId');
  const percent_complete = document.getElementById('taskPercent');
  if (!validarCampos([title, id, bucket_id, plan_id, percent_complete])) return;
  try {
    const res = await fetch(`${api}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: parseInt(id.value),
        title: title.value,
        bucket_id: parseInt(bucket_id.value),
        plan_id: parseInt(plan_id.value),
        percent_complete: parseInt(percent_complete.value)
      })
    });
    log('Crear Tarea: ' + await res.text());
    listarTareas();
  } catch (e) { log('Error crear tarea: ' + e); }
}
// Listar y renderizar planes
async function listarPlanes() {
  try {
    const res = await fetch(`${api}/plans`);
    const planes = await res.json();
    renderTablaPlanes(planes);
    log('Planes actualizados');
  } catch (e) { log('Error listar planes: ' + e); }
}
// Listar y renderizar buckets
async function listarBuckets() {
  try {
    const res = await fetch(`${api}/buckets`);
    const buckets = await res.json();
    renderTablaBuckets(buckets);
    log('Buckets actualizados');
  } catch (e) { log('Error listar buckets: ' + e); }
}
// Listar y renderizar tareas
async function listarTareas() {
  try {
    const res = await fetch(`${api}/tasks`);
    const tareas = await res.json();
    renderTablaTareas(tareas);
    log('Tareas actualizadas');
  } catch (e) { log('Error listar tareas: ' + e); }
}
// Actualizar una tarea existente
async function actualizarTarea() {
  const id = document.getElementById('updateTaskId');
  const title = document.getElementById('updateTaskTitle');
  const percent_complete = document.getElementById('updateTaskPercent');
  const bucket_id = document.getElementById('updateTaskBucketId');
  const plan_id = document.getElementById('updateTaskPlanId');
  if (!validarCampos([id, title, percent_complete, bucket_id, plan_id])) return;
  try {
    const res = await fetch(`${api}/tasks/${parseInt(id.value)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: parseInt(id.value),
        title: title.value,
        percent_complete: parseInt(percent_complete.value),
        bucket_id: parseInt(bucket_id.value),
        plan_id: parseInt(plan_id.value)
      })
    });
    log('Actualizar Tarea: ' + await res.text());
    listarTareas();
  } catch (e) { log('Error actualizar tarea: ' + e); }
}
// Eliminar una tarea existente
async function eliminarTarea() {
  const id = document.getElementById('deleteTaskId');
  if (!validarCampos([id])) return;
  try {
    const res = await fetch(`${api}/tasks/${parseInt(id.value)}`, { method: 'DELETE' });
    log('Eliminar Tarea: ' + await res.text());
    listarTareas();
  } catch (e) { log('Error eliminar tarea: ' + e); }
}
// Inicializar tablas y filtros al cargar la página
window.onload = function() {
  cargarResumenPlanner();
  listarPlanes();
  listarBuckets();
  listarTareas();
};
