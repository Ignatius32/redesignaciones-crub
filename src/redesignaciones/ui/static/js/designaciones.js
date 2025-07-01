/**
 * CRUB Designaciones Frontend JavaScript
 * Handles department-based view of faculty designations
 */

class DesignacionesApp {
    constructor() {
        this.departments = [];
        this.filteredDepartments = [];
        this.currentFilter = 'all';
        this.searchTerm = '';
        this.expandedDepartments = new Set();
        
        this.init();
    }

    async init() {
        this.showLoading(true);
        
        try {
            await this.loadDepartments();
            this.setupEventListeners();
            this.renderDepartments();
            this.updateStatistics();
        } catch (error) {
            this.showError('Error al cargar los datos: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async loadDepartments() {
        try {
            const response = await fetch('/api/departamentos');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.departments = data.departamentos || [];
            this.filteredDepartments = [...this.departments];
            
            console.log(`Loaded ${this.departments.length} departments`);
        } catch (error) {
            console.error('Error loading departments:', error);
            throw error;
        }
    }

    async loadDepartmentDesignaciones(departmentName) {
        try {
            const response = await fetch(`/api/departamentos/${encodeURIComponent(departmentName)}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data.designaciones || [];
        } catch (error) {
            console.error(`Error loading designaciones for ${departmentName}:`, error);
            throw error;
        }
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.applyFilters();
            });
        }

        // Filter select
        const filterSelect = document.getElementById('filterSelect');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.applyFilters();
            });
        }

        // Clear filters button
        const clearBtn = document.getElementById('clearFilters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Department toggle handlers will be added dynamically
    }

    applyFilters() {
        let filtered = [...this.departments];

        // Apply search filter
        if (this.searchTerm) {
            filtered = filtered.filter(dept => 
                dept.nombre.toLowerCase().includes(this.searchTerm)
            );
        }

        // Apply department size filter
        if (this.currentFilter !== 'all') {
            switch (this.currentFilter) {
                case 'large':
                    filtered = filtered.filter(dept => dept.total_designaciones >= 20);
                    break;
                case 'medium':
                    filtered = filtered.filter(dept => 
                        dept.total_designaciones >= 5 && dept.total_designaciones < 20
                    );
                    break;
                case 'small':
                    filtered = filtered.filter(dept => dept.total_designaciones < 5);
                    break;
                case 'with-courses':
                    filtered = filtered.filter(dept => dept.total_materias > 0);
                    break;
            }
        }

        // Sort by name
        filtered.sort((a, b) => a.nombre.localeCompare(b.nombre));

        this.filteredDepartments = filtered;
        this.renderDepartments();
        this.updateStatistics();
    }

    clearFilters() {
        this.searchTerm = '';
        this.currentFilter = 'all';
        
        const searchInput = document.getElementById('searchInput');
        const filterSelect = document.getElementById('filterSelect');
        
        if (searchInput) searchInput.value = '';
        if (filterSelect) filterSelect.value = 'all';
        
        this.applyFilters();
    }

    renderDepartments() {
        const container = document.getElementById('departmentsList');
        if (!container) return;

        if (this.filteredDepartments.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="padding: 3rem;">
                    <h3>No se encontraron departamentos</h3>
                    <p>Intenta ajustar los filtros de búsqueda.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.filteredDepartments.map(dept => `
            <div class="department-item" data-department="${dept.nombre}">
                <div class="department-header" onclick="app.toggleDepartment('${dept.nombre}')">
                    <div class="department-name">${dept.nombre}</div>
                    <div class="department-stats">
                        <span>Designaciones: <strong>${dept.total_designaciones}</strong></span>
                        <span>Docentes: <strong>${dept.total_docentes}</strong></span>
                        <span>Materias: <strong>${dept.total_materias}</strong></span>
                    </div>
                    <div class="department-toggle">▼</div>
                </div>
                <div class="department-content" id="content-${this.sanitizeId(dept.nombre)}">
                    <div class="loading">
                        <div class="spinner"></div>
                        Cargando designaciones...
                    </div>
                </div>
            </div>
        `).join('');
    }

    async toggleDepartment(departmentName) {
        const contentId = `content-${this.sanitizeId(departmentName)}`;
        const content = document.getElementById(contentId);
        const header = content.previousElementSibling;
        
        if (!content) return;

        const isExpanded = this.expandedDepartments.has(departmentName);
        
        if (isExpanded) {
            // Collapse
            content.classList.remove('expanded');
            header.classList.remove('expanded');
            this.expandedDepartments.delete(departmentName);
        } else {
            // Expand
            content.classList.add('expanded');
            header.classList.add('expanded');
            this.expandedDepartments.add(departmentName);
            
            // Load designaciones if not already loaded
            if (content.innerHTML.includes('Cargando designaciones...')) {
                try {
                    const designaciones = await this.loadDepartmentDesignaciones(departmentName);
                    this.renderDesignaciones(contentId, designaciones);
                } catch (error) {
                    content.innerHTML = `
                        <div class="error">
                            Error al cargar las designaciones: ${error.message}
                        </div>
                    `;
                }
            }
        }
    }

    renderDesignaciones(contentId, designaciones) {
        const content = document.getElementById(contentId);
        if (!content) return;

        if (designaciones.length === 0) {
            content.innerHTML = `
                <div class="text-center" style="padding: 2rem;">
                    <p>No hay designaciones en este departamento.</p>
                </div>
            `;
            return;
        }

        content.innerHTML = `
            <table class="designaciones-table">
                <thead>
                    <tr>
                        <th>D_Desig</th>
                        <th>Docente</th>
                        <th>Carácter</th>
                        <th>Dedicación</th>
                        <th>Estado</th>
                        <th>Materias</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${designaciones.map(des => this.renderDesignacionRow(des)).join('')}
                </tbody>
            </table>
        `;
    }

    renderDesignacionRow(designacion) {
        const statusClass = this.getStatusClass(designacion.estado);
        const materiasCount = designacion.materias ? designacion.materias.length : 0;
        const hasMateriasData = materiasCount > 0;
        
        return `
            <tr class="designacion-main-row ${hasMateriasData ? 'has-materias' : ''}" onclick="app.toggleMaterias('${designacion.d_desig}')">
                <td>
                    <div class="d-desig-cell">
                        <span class="d-desig">${designacion.d_desig}</span>
                        ${hasMateriasData ? '<span class="expand-indicator">▼</span>' : '<span class="no-materias-indicator">○</span>'}
                    </div>
                </td>
                <td><span class="docente-name">${designacion.apellido_y_nombre}</span></td>
                <td>${designacion.caracter || '-'}</td>
                <td>${designacion.dedicacion || '-'}</td>
                <td><span class="status-badge ${statusClass}">${designacion.estado || 'N/A'}</span></td>
                <td>
                    <span class="materias-count ${hasMateriasData ? 'with-materias' : 'no-materias'}">
                        ${materiasCount} ${materiasCount === 1 ? 'materia' : 'materias'}
                    </span>
                </td>
                <td>
                    <button class="btn-sm" onclick="event.stopPropagation(); app.viewDesignacion('${designacion.d_desig}')">
                        Ver detalles
                    </button>
                </td>
            </tr>
            <tr id="materias-${designacion.d_desig}" class="materias-row hidden">
                <td colspan="7">
                    ${this.renderDesignacionDetails(designacion)}
                </td>
            </tr>
        `;
    }

    renderDesignacionDetails(designacion) {
        const materiasCount = designacion.materias ? designacion.materias.length : 0;
        
        return `
            <div class="designacion-expanded-details">
                <div class="designacion-info-section">
                    <h4>📋 Información de la Designación</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Legajo:</label>
                            <span>${designacion.legajo || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <label>CUIL:</label>
                            <span>${designacion.cuil || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <label>Cuerpo:</label>
                            <span>${designacion.cuerpo || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <label>Período:</label>
                            <span>${designacion.desde || 'N/A'} - ${designacion.hasta || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <label>Área:</label>
                            <span>${designacion.area || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <label>Orientación:</label>
                            <span>${designacion.orientacion || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <label>Fecha Ingreso:</label>
                            <span>${designacion.fecha_ingreso || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <label>Norma:</label>
                            <span>${designacion.norma || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                
                ${materiasCount > 0 ? `
                <div class="materias-section">
                    <h4>📚 Materias Asignadas (${materiasCount})</h4>
                    <div class="materias-grid">
                        ${designacion.materias.map(materia => this.renderMateriaCard(materia)).join('')}
                    </div>
                </div>
                ` : `
                <div class="no-materias-section">
                    <h4>📚 Materias Asignadas</h4>
                    <p class="no-materias-message">
                        <em>No hay materias asignadas a esta designación</em>
                    </p>
                </div>
                `}
            </div>
        `;
    }

    renderMateriaCard(materia) {
        return `
            <div class="materia-card">
                <div class="materia-header">
                    <h5 class="materia-name">${materia.materia_nombre || 'Sin nombre'}</h5>
                    <span class="materia-codigo">${materia.cod_siu || 'Sin código'}</span>
                </div>
                
                <div class="materia-basic-info">
                    <div class="info-row">
                        <span class="info-label">Carrera:</span>
                        <span class="info-value">${materia.carrera || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Categoría:</span>
                        <span class="info-value">${materia.categoria || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Rol:</span>
                        <span class="info-value">${materia.rol || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Período:</span>
                        <span class="info-value">${materia.periodo || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Módulo:</span>
                        <span class="info-value">${materia.modulo || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Estado:</span>
                        <span class="info-value">
                            <span class="status-badge ${this.getStatusClass(materia.estado_materia)}">${materia.estado_materia || 'N/A'}</span>
                        </span>
                    </div>
                </div>
                
                ${materia.materia_detalle ? `
                <div class="huayca-details">
                    <h6>🎓 Detalles Adicionales (Huayca)</h6>
                    <div class="huayca-info-grid">
                        ${materia.materia_detalle.horas_totales ? `
                        <div class="huayca-item">
                            <span class="huayca-label">Horas Totales:</span>
                            <span class="huayca-value">${materia.materia_detalle.horas_totales}</span>
                        </div>
                        ` : ''}
                        ${materia.materia_detalle.horas_semanales ? `
                        <div class="huayca-item">
                            <span class="huayca-label">Horas Semanales:</span>
                            <span class="huayca-value">${materia.materia_detalle.horas_semanales}</span>
                        </div>
                        ` : ''}
                        ${materia.materia_detalle.depto_principal ? `
                        <div class="huayca-item">
                            <span class="huayca-label">Depto. Principal:</span>
                            <span class="huayca-value">${materia.materia_detalle.depto_principal}</span>
                        </div>
                        ` : ''}
                        ${materia.materia_detalle.trayecto ? `
                        <div class="huayca-item">
                            <span class="huayca-label">Trayecto:</span>
                            <span class="huayca-value">${materia.materia_detalle.trayecto}</span>
                        </div>
                        ` : ''}
                        ${materia.materia_detalle.optativa ? `
                        <div class="huayca-item">
                            <span class="huayca-label">Optativa:</span>
                            <span class="huayca-value">${materia.materia_detalle.optativa}</span>
                        </div>
                        ` : ''}
                        ${materia.materia_detalle.ano_plan ? `
                        <div class="huayca-item">
                            <span class="huayca-label">Año Plan:</span>
                            <span class="huayca-value">${materia.materia_detalle.ano_plan}</span>
                        </div>
                        ` : ''}
                    </div>
                    
                    ${materia.materia_detalle.contenidos_minimos && materia.materia_detalle.contenidos_minimos !== '-' ? `
                    <div class="contenidos-section">
                        <h6>📋 Contenidos Mínimos</h6>
                        <p class="contenidos-text">${materia.materia_detalle.contenidos_minimos}</p>
                    </div>
                    ` : ''}
                    
                    ${materia.materia_detalle.correlativas_para_cursar && materia.materia_detalle.correlativas_para_cursar !== '-' ? `
                    <div class="correlativas-section">
                        <h6>🔗 Correlativas para Cursar</h6>
                        <p class="correlativas-text">${materia.materia_detalle.correlativas_para_cursar}</p>
                    </div>
                    ` : ''}
                    
                    ${materia.materia_detalle.correlativas_para_aprobar && materia.materia_detalle.correlativas_para_aprobar !== '-' ? `
                    <div class="correlativas-section">
                        <h6>✅ Correlativas para Aprobar</h6>
                        <p class="correlativas-text">${materia.materia_detalle.correlativas_para_aprobar}</p>
                    </div>
                    ` : ''}
                </div>
                ` : ''}
            </div>
        `;
    }

    toggleMaterias(dDesig) {
        const row = document.getElementById(`materias-${dDesig}`);
        const mainRow = row.previousElementSibling;
        const expandIndicator = mainRow.querySelector('.expand-indicator');
        const noMateriasIndicator = mainRow.querySelector('.no-materias-indicator');
        
        if (!row) return;
        
        // Don't toggle if there are no materias
        if (noMateriasIndicator) {
            return;
        }
        
        const isHidden = row.classList.contains('hidden');
        
        if (isHidden) {
            // Expand
            row.classList.remove('hidden');
            row.classList.add('expanded');
            mainRow.classList.add('expanded');
            if (expandIndicator) {
                expandIndicator.textContent = '▲';
            }
        } else {
            // Collapse
            row.classList.add('hidden');
            row.classList.remove('expanded');
            mainRow.classList.remove('expanded');
            if (expandIndicator) {
                expandIndicator.textContent = '▼';
            }
        }
    }

    viewDesignacion(dDesig) {
        // Open designation details in new window/tab
        window.open(`/designaciones/by-desig/${dDesig}`, '_blank');
    }

    getStatusClass(estado) {
        if (!estado) return 'status-pendiente';
        
        const status = estado.toLowerCase();
        if (status.includes('activ') || status.includes('vigent')) {
            return 'status-activo';
        } else if (status.includes('inactiv') || status.includes('cerrad')) {
            return 'status-inactivo';
        } else {
            return 'status-pendiente';
        }
    }

    updateStatistics() {
        const totalDepartments = this.filteredDepartments.length;
        const totalDesignaciones = this.filteredDepartments.reduce(
            (sum, dept) => sum + dept.total_designaciones, 0
        );
        const totalDocentes = this.filteredDepartments.reduce(
            (sum, dept) => sum + dept.total_docentes, 0
        );
        const totalMaterias = this.filteredDepartments.reduce(
            (sum, dept) => sum + dept.total_materias, 0
        );

        this.updateStatElement('statDepartments', totalDepartments);
        this.updateStatElement('statDesignaciones', totalDesignaciones);
        this.updateStatElement('statDocentes', totalDocentes);
        this.updateStatElement('statMaterias', totalMaterias);
    }

    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value.toLocaleString();
        }
    }

    sanitizeId(str) {
        return str.replace(/[^a-zA-Z0-9]/g, '_');
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const content = document.getElementById('mainContent');
        
        if (loading) loading.style.display = show ? 'block' : 'none';
        if (content) content.style.display = show ? 'none' : 'block';
    }

    showError(message) {
        const container = document.getElementById('departmentsList');
        if (container) {
            container.innerHTML = `
                <div class="error">
                    <h3>Error</h3>
                    <p>${message}</p>
                    <button onclick="location.reload()" class="clear-btn mt-2">
                        Reintentar
                    </button>
                </div>
            `;
        }
    }
}

// Utility functions for button styles
const style = document.createElement('style');
style.textContent = `
    .btn-sm {
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: var(--transition);
    }
    
    .btn-sm:hover {
        background-color: var(--secondary-color);
    }
    
    .materias-row {
        background-color: #f8f9fa;
    }
    
    .materias-row.hidden {
        display: none;
    }
`;
document.head.appendChild(style);

// Initialize the app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new DesignacionesApp();
});

// Export for global access
window.DesignacionesApp = DesignacionesApp;
