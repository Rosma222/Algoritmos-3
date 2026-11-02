document.addEventListener('DOMContentLoaded', () => {
    let currentUser = null;
    let currentTicketId = null;
    let allTickets = [];
    let rubrosList = [];

    // Elementos DOM
    const views = document.querySelectorAll('.view');
    const navMenu = document.getElementById('nav-menu');
    
    // Auth Forms
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const showRegisterLink = document.getElementById('show-register');
    const showLoginLink = document.getElementById('show-login');
    const boxRegister = document.getElementById('box-register');
    const boxLogin = document.getElementById('form-login').parentElement;
    const regRoleSelect = document.getElementById('reg-role');
    const groupRubro = document.getElementById('group-rubro');
    const regRubroSelect = document.getElementById('reg-rubro');

    // Modals
    const modalTicket = document.getElementById('modal-ticket');
    const btnOpenCreateTicket = document.getElementById('btn-open-create-ticket');
    const closeModalTicket = document.getElementById('close-modal-ticket');
    const formCreateTicket = document.getElementById('form-create-ticket');

    const modalProduct = document.getElementById('modal-product');
    const btnOpenCreateProduct = document.getElementById('btn-open-create-product');
    const closeModalProduct = document.getElementById('close-modal-product');
    const formCreateProduct = document.getElementById('form-create-product');

    // Navegación Vistas
    function switchView(viewId) {
        views.forEach(v => v.classList.remove('active'));
        document.getElementById(viewId).classList.add('active');
    }

    // Verificar sesión inicial
    async function checkSession() {
        try {
            const res = await fetch('/api/session');
            const data = await res.json();
            if (data.logged_in) {
                currentUser = data.user;
                renderNavbar();
                loadDashboard();
            } else {
                switchView('view-auth');
                loadRubrosForRegister();
            }
        } catch (e) {
            console.error(e);
            switchView('view-auth');
        }
    }

    function renderNavbar() {
        navMenu.innerHTML = `
            <span>Hola, <strong>${currentUser.username}</strong> (${currentUser.role})</span>
            <button id="nav-dashboard" class="btn-link">Tickets</button>
            <button id="nav-products" class="btn-link">Productos & Rubros</button>
            <button id="btn-logout" class="btn btn-secondary" style="margin:0; padding:0.4rem 0.8rem;">Cerrar Sesión</button>
        `;

        document.getElementById('nav-dashboard').addEventListener('click', () => {
            switchView('view-dashboard');
            loadDashboard();
        });

        document.getElementById('nav-products').addEventListener('click', () => {
            switchView('view-products');
            loadProductsAndRubros();
        });

        document.getElementById('btn-logout').addEventListener('click', async () => {
            await fetch('/api/logout', { method: 'POST' });
            currentUser = null;
            switchView('view-auth');
            loadRubrosForRegister();
        });
    }

    // Auth Switch
    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault();
        boxLogin.classList.add('hidden');
        boxRegister.classList.remove('hidden');
    });

    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        boxRegister.classList.add('hidden');
        boxLogin.classList.remove('hidden');
    });

    regRoleSelect.addEventListener('change', (e) => {
        if (e.target.value === 'representative') {
            groupRubro.classList.remove('hidden');
        } else {
            groupRubro.classList.add('hidden');
        }
    });

    async function loadRubrosForRegister() {
        const res = await fetch('/api/rubros');
        rubrosList = await res.json();
        regRubroSelect.innerHTML = rubrosList.map(r => `<option value="${r.id}">${r.nombre}</option>`).join('');
    }

    // Login Submit
    formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            currentUser = data.user;
            renderNavbar();
            switchView('view-dashboard');
            loadDashboard();
        } else {
            alert(data.error || 'Error al iniciar sesión');
        }
    });

    // Register Submit
    formRegister.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const role = document.getElementById('reg-role').value;
        const rubro_id = role === 'representative' ? regRubroSelect.value : null;

        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, role, rubro_id })
        });
        const data = await res.json();
        if (res.ok) {
            alert('¡Registro exitoso! Ya puedes iniciar sesión.');
            boxRegister.classList.add('hidden');
            boxLogin.classList.remove('hidden');
        } else {
            alert(data.error || 'Error en el registro');
        }
    });

    // Dashboard Tickets
    async function loadDashboard() {
        const res = await fetch('/api/tickets');
        allTickets = await res.json();
        renderTickets(allTickets);
    }

    function renderTickets(tickets) {
        const container = document.getElementById('ticket-container');
        if (tickets.length === 0) {
            container.innerHTML = `<p style="text-align: center; color: #64748b; padding: 2rem;">No hay tickets registrados.</p>`;
            return;
        }

        container.innerHTML = tickets.map(t => `
            <div class="ticket-card" data-id="${t.id}">
                <div>
                    <h4>#${t.id} - ${t.asunto}</h4>
                    <p style="font-size: 0.9rem; color: #64748b;">Rubro: <strong>${t.rubro_name}</strong> | Producto: ${t.product_info} | Cliente: ${t.client_name} | Asignado: ${t.representative_name}</p>
                    <small>Creado: ${t.fecha_creacion}</small>
                </div>
                <div>
                    <span class="badge badge-${t.estado.replace(' ', '-')}">${t.estado}</span>
                </div>
            </div>
        `).join('');

        document.querySelectorAll('.ticket-card').forEach(card => {
            card.addEventListener('click', () => {
                const ticketId = card.getAttribute('data-id');
                loadTicketDetail(ticketId);
            });
        });
    }

    // Filtros por estado
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.getAttribute('data-filter');
            if (filter === 'all') {
                renderTickets(allTickets);
            } else {
                renderTickets(allTickets.filter(t => t.estado === filter));
            }
        });
    });

    // Detalle de Ticket
    async function loadTicketDetail(id) {
        currentTicketId = id;
        const res = await fetch('/api/tickets');
        const tickets = await res.json();
        const ticket = tickets.find(t => t.id == id);
        if (!ticket) return;

        const detailContainer = document.getElementById('ticket-detail-content');
        detailContainer.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h2>Ticket #${ticket.id}: ${ticket.asunto}</h2>
                    <p><strong>Rubro:</strong> ${ticket.rubro_name}</p>
                    <p><strong>Producto:</strong> ${ticket.product_info}</p>
                    <p><strong>Cliente:</strong> ${ticket.client_name} | <strong>Representante:</strong> ${ticket.representative_name}</p>
                    <p><strong>Fecha:</strong> ${ticket.fecha_creacion}</p>
                </div>
                <div>
                    <p><strong>Estado Actual:</strong> <span class="badge badge-${ticket.estado.replace(' ', '-')}">${ticket.estado}</span></p>
                    ${currentUser.role === 'representative' || currentUser.role === 'admin' ? `
                        <div style="margin-top: 0.5rem;">
                            <select id="select-change-estado" style="padding: 0.4rem; border-radius: 4px;">
                                <option value="Abierto" ${ticket.estado=='Abierto'?'selected':''}>Abierto</option>
                                <option value="En Progreso" ${ticket.estado=='En Progreso'?'selected':''}>En Progreso</option>
                                <option value="Resuelto" ${ticket.estado=='Resuelto'?'selected':''}>Resuelto</option>
                                <option value="Cerrado" ${ticket.estado=='Cerrado'?'selected':''}>Cerrado</option>
                            </select>
                            <button id="btn-update-estado" class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.85rem; width: auto; margin-top: 0.3rem;">Actualizar Estado</button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        if (document.getElementById('btn-update-estado')) {
            document.getElementById('btn-update-estado').addEventListener('click', async () => {
                const nuevoEstado = document.getElementById('select-change-estado').value;
                const r = await fetch(`/api/tickets/${ticket.id}/estado`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ estado: nuevoEstado })
                });
                if (r.ok) {
                    loadTicketDetail(ticket.id);
                }
            });
        }

        const hitosContainer = document.getElementById('hitos-container');
        hitosContainer.innerHTML = ticket.hitos.map(h => `
            <div class="hito-item">
                <div class="hito-header">
                    <span><strong>${h.username}</strong> (${h.role})</span>
                    <span>${h.fecha}</span>
                </div>
                <p>${h.mensaje}</p>
            </div>
        `).join('');

        switchView('view-ticket-detail');
    }

    // Enviar Hito / Mensaje
    document.getElementById('form-add-hito').addEventListener('submit', async (e) => {
        e.preventDefault();
        const mensaje = document.getElementById('hito-mensaje').value;
        const res = await fetch(`/api/tickets/${currentTicketId}/hitos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUser.id, mensaje })
        });
        if (res.ok) {
            document.getElementById('hito-mensaje').value = '';
            loadTicketDetail(currentTicketId);
        } else {
            const data = await res.json();
            alert(data.error || 'Error al enviar mensaje');
        }
    });

    document.getElementById('btn-back-dashboard').addEventListener('click', () => {
        switchView('view-dashboard');
        loadDashboard();
    });

    // Modals Handlers
    btnOpenCreateTicket.addEventListener('click', async () => {
        // Cargar productos disponibles y usuarios si es admin/rep
        const prodRes = await fetch('/api/products');
        const products = await prodRes.json();
        const prodSelect = document.getElementById('ticket-product-id');
        prodSelect.innerHTML = products.map(p => `<option value="${p.id}">${p.marca} ${p.nombre} (Rubro: ${p.rubro}) - Cód: ${p.codigo_interno}</option>`).join('');

        if (currentUser.role === 'admin' || currentUser.role === 'representative') {
            document.getElementById('client-select-group').classList.remove('hidden');
            const userRes = await fetch('/api/users');
            const users = await userRes.json();
            const clientSelect = document.getElementById('ticket-client-id');
            clientSelect.innerHTML = users.filter(u => u.role === 'client').map(u => `<option value="${u.id}">${u.username} (${u.email})</option>`).join('');
        } else {
            document.getElementById('client-select-group').classList.add('hidden');
        }

        modalTicket.classList.add('active');
    });

    closeModalTicket.addEventListener('click', () => modalTicket.classList.remove('active'));

    formCreateTicket.addEventListener('submit', async (e) => {
        e.preventDefault();
        const product_id = document.getElementById('ticket-product-id').value;
        const asunto = document.getElementById('ticket-asunto').value;
        const mensaje_inicial = document.getElementById('ticket-mensaje').value;
        const client_id = currentUser.role !== 'client' ? document.getElementById('ticket-client-id').value : currentUser.id;

        const res = await fetch('/api/tickets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ client_id, product_id, asunto, mensaje_inicial })
        });
        const data = await res.json();
        if (res.ok) {
            modalTicket.classList.remove('active');
            formCreateTicket.reset();
            loadDashboard();
        } else {
            alert(data.error || 'Error al crear ticket');
        }
    });

    // Productos y Rubros Vista
    btnOpenCreateProduct.addEventListener('click', async () => {
        const prodRubroSelect = document.getElementById('prod-rubro-id');
        prodRubroSelect.innerHTML = rubrosList.map(r => `<option value="${r.id}">${r.nombre}</option>`).join('');
        modalProduct.classList.add('active');
    });

    closeModalProduct.addEventListener('click', () => modalProduct.classList.remove('active'));

    formCreateProduct.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nombre = document.getElementById('prod-nombre').value;
        const marca = document.getElementById('prod-marca').value;
        const modelo = document.getElementById('prod-modelo').value;
        const nro_serie = document.getElementById('prod-serie').value;
        const codigo_interno = document.getElementById('prod-codigo').value;
        const rubro_id = document.getElementById('prod-rubro-id').value;

        const res = await fetch('/api/products', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, marca, modelo, nro_serie, codigo_interno, rubro_id })
        });
        const data = await res.json();
        if (res.ok) {
            modalProduct.classList.remove('active');
            formCreateProduct.reset();
            loadProductsAndRubros();
        } else {
            alert(data.error || 'Error al registrar producto');
        }
    });

    async function loadProductsAndRubros() {
        const rubrosRes = await fetch('/api/rubros');
        const rubros = await rubrosRes.json();
        rubrosList = rubros;

        const rubrosUl = document.getElementById('rubros-list');
        rubrosUl.innerHTML = rubros.map(r => `<li><strong>${r.nombre}</strong>: ${r.descripcion}</li>`).join('');

        const prodRes = await fetch('/api/products');
        const products = await prodRes.json();
        const prodDiv = document.getElementById('products-list');
        prodDiv.innerHTML = products.length === 0 ? '<p>No hay productos registrados.</p>' : products.map(p => `
            <div style="padding: 0.75rem; border-bottom: 1px solid #cbd5e1;">
                <strong>${p.marca} ${p.nombre}</strong> (${p.modelo})<br>
                <small>Rubro: ${p.rubro} | Nro Serie: ${p.nro_serie} | Cód. Interno: ${p.codigo_interno}</small>
            </div>
        `).join('');
    }

    // Inicializar
    checkSession();
});
