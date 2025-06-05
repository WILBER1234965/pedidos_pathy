// static/js/pedido_multi_form.js

document.addEventListener('DOMContentLoaded', function() {
  // Referencias globales
  const inputCliente = document.getElementById('autocompleteCliente');
  const sugerencias = document.getElementById('sugerenciasClientes');
  const clienteHidden = document.getElementById('clienteIdHidden');
  const btnAgregarPrenda = document.getElementById('btnAgregarPrenda');
  const formPedido = document.getElementById('formPedidoMulti');

  // Plantilla HTML base para un bloque de prenda (índice 0)
  const bloqueBase = document.querySelector('.bloque-prenda[data-index="0"]').outerHTML;
  let contadorBloques = 1; // el siguiente bloque que agreguemos tendrá índice = 1

  // 1) AUTOCOMPLETE DE CLIENTES (misma lógica que antes)
  let timeoutBusqueda = null;
  inputCliente.addEventListener('input', function() {
    const texto = this.value.trim();
    sugerencias.innerHTML = '';
    clienteHidden.value = '';

    if (texto.length < 3) return;

    if (timeoutBusqueda) clearTimeout(timeoutBusqueda);
    timeoutBusqueda = setTimeout(function() {
      fetch(`/admin/clientes/buscar?q=${encodeURIComponent(texto)}`)
        .then(resp => resp.json())
        .then(data => {
          sugerencias.innerHTML = '';
          data.forEach(c => {
            const item = document.createElement('button');
            item.type = 'button';
            item.classList.add('list-group-item', 'list-group-item-action');
            item.textContent = c.nombre;
            item.dataset.id = c.id;
            item.addEventListener('click', function() {
              inputCliente.value = this.textContent;
              clienteHidden.value = this.dataset.id;
              sugerencias.innerHTML = '';
              // Al seleccionar cliente, revisamos cada bloque de prenda activo
              document.querySelectorAll('.bloque-prenda').forEach(divBloque => {
                const index = divBloque.dataset.index;
                const selectPrenda = document.getElementById(`selectTipoPrenda_${index}`);
                if (selectPrenda && selectPrenda.value) {
                  verificarMedidasExistentes(index, selectPrenda.value, clienteHidden.value);
                }
              });
            });
            sugerencias.appendChild(item);
          });
        });
    }, 300);
  });

  document.addEventListener('click', function(e) {
    if (!inputCliente.contains(e.target) && !sugerencias.contains(e.target)) {
      sugerencias.innerHTML = '';
    }
  });
  const modalClienteEl = document.getElementById('modalCrearCliente');
  if (modalClienteEl) {
    modalClienteEl.addEventListener('show.bs.modal', function () {
      sugerencias.innerHTML = '';
      document.getElementById('errorCliente').textContent = '';
      document.getElementById('formCrearClienteModal').reset();
    });
  }

  // 2) AL CAMBIAR EL SELECTOR DE PRENDA EN CUALQUIER BLOQUE
  function onChangeTipoPrenda(event) {
    const select = event.target;
    const index = select.closest('.bloque-prenda').dataset.index;
    const tipoPrenda = select.value;
    const clienteId = clienteHidden.value || null;

    // Limpiar contenedor de medidas previo
    document.getElementById(`contenedorMedidas_${index}`).innerHTML = '';

    if (clienteId) {
      // Si hay cliente, ver si tiene medidas para esta prenda
      verificarMedidasExistentes(index, tipoPrenda, clienteId);
    } else {
      // Si no hay cliente seleccionado, solo mostramos el formulario en blanco
      cargarFormularioMedidasEnBlanco(index, tipoPrenda);
    }
  }

  // 3) FUNCIÓN PARA CONSULTAR MEDIDAS EXISTENTES vía AJAX
  function verificarMedidasExistentes(index, tipoPrenda, clienteId) {
    fetch(`/admin/medidas/obtener?cliente_id=${clienteId}&tipo_prenda=${tipoPrenda}`)
      .then(resp => resp.json())
      .then(data => {
        const contenedor = document.getElementById(`contenedorMedidas_${index}`);
        if (data.existe) {
          // Construir <select> con las medidas guardadas
          let htmlSelect = `
            <h5>Medidas existentes</h5>
            <div class="mb-3">
              <label for="selectMedidaExistente_${index}" class="form-label">Selecciona la medida</label>
              <select class="form-select" id="selectMedidaExistente_${index}" name="prenda[${index}][medida_id]" required>
                <option value="" disabled selected>-- Selecciona --</option>
                ${data.medidas.map(m => `<option value="${m.id}">${m.descripcion_corta}</option>`).join('')}
              </select>
            </div>
            <div class="mb-3">
              <button type="button" class="btn btn-sm btn-secondary" id="btnUsarMedida_${index}">Usar esta medida</button>
              <button type="button" class="btn btn-sm btn-link" id="btnEditarMedida_${index}">Editar medidas</button>
            </div>
          `;
          contenedor.innerHTML = htmlSelect;

          // Cuando el usuario haga clic en “Usar esta medida”:
          document.getElementById(`btnUsarMedida_${index}`).addEventListener('click', function() {
            const selectMedida = document.getElementById(`selectMedidaExistente_${index}`);
            if (!selectMedida.value) {
              alert('Selecciona primero una medida existente.');
              return;
            }
            // Marcamos que NO se crearán medidas nuevas:
            document.querySelector(`.bloque-prenda[data-index="${index}"] .crearMedidasHidden`).value = 'off';
          });

          // Cuando el usuario haga clic en “Editar medidas”:
          document.getElementById(`btnEditarMedida_${index}`).addEventListener('click', function() {
            cargarFormularioMedidasEnBlanco(index, tipoPrenda);
          });
        } else {
          // No hay medidas guardadas → carga formulario en blanco
          cargarFormularioMedidasEnBlanco(index, tipoPrenda);
        }
      });
  }

  // 4) FUNCIÓN PARA CARGAR FORMULARIO EN BLANCO (inputs) SEGÚN TIPO DE PRENDA
  function cargarFormularioMedidasEnBlanco(index, tipoPrenda) {
    const contenedor = document.getElementById(`contenedorMedidas_${index}`);
    // Guardamos que vamos a crear medidas nuevas:
    contenedor.closest('.bloque-prenda').querySelector('.crearMedidasHidden').value = 'on';

    // A continuación construimos dinámicamente el HTML para los inputs según el tipo. 
    // Por ejemplo, para “blusa_cochala” o “blusa_sucrena”:
    if (tipoPrenda === 'blusa_cochala' || tipoPrenda === 'blusa_sucreña') {
      contenedor.innerHTML = `
        <h5>Registrar medidas para blusa</h5>
        <div class="row">
          <div class="col-md-4 mb-2">
            <label for="largo_espalda_${index}" class="form-label">Largo espalda</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][largo_espalda]" id="largo_espalda_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="largo_delantero_${index}" class="form-label">Largo delantero</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][largo_delantero]" id="largo_delantero_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="cintura_${index}" class="form-label">Cintura</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][cintura]" id="cintura_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="busto_${index}" class="form-label">Busto</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][busto]" id="busto_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="media_cintura_${index}" class="form-label">Media cintura</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][media_cintura]" id="media_cintura_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="sisa_${index}" class="form-label">Sisa</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][sisa]" id="sisa_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="escote_${index}" class="form-label">Escote</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][escote]" id="escote_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="largo_manga_${index}" class="form-label">Largo manga</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][largo_manga]" id="largo_manga_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="puño_${index}" class="form-label">Puño</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][puño]" id="puño_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="cuello_${index}" class="form-label">Cuello</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][cuello]" id="cuello_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="abertura_${index}" class="form-label">Abertura</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][abertura]" id="abertura_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="ancho_espalda_${index}" class="form-label">Ancho espalda</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][ancho_espalda]" id="ancho_espalda_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="figura_${index}" class="form-label">Figura</label>
            <input type="text" class="form-control" name="prenda[${index}][figura]" id="figura_${index}" required>
          </div>
        </div>
      `;
    }

    // Repite la misma lógica para "pollera_cochala", "pollera_sucreña", "juste_cochala", ...
    // Ejemplo breve para Pollera Cochala:
    if (tipoPrenda === 'pollera_cochala') {
      contenedor.innerHTML = `
        <h5>Registrar medidas para pollera cochala</h5>
        <div class="row">
          <div class="col-md-4 mb-2">
            <label for="cintura_${index}" class="form-label">Cintura</label>
            <input type="number" step="0.1" class="form-control" name="prenda[${index}][cintura]" id="cintura_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="alforza_${index}" class="form-label">Alforza</label>
            <input type="text" class="form-control" name="prenda[${index}][alforza]" id="alforza_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="paños_${index}" class="form-label">Paños</label>
            <input type="number" class="form-control" name="prenda[${index}][paños]" id="paños_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="wato_${index}" class="form-label">Wato</label>
            <input type="text" class="form-control" name="prenda[${index}][wato]" id="wato_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="corridas_${index}" class="form-label">Corridas</label>
            <input type="text" class="form-control" name="prenda[${index}][corridas]" id="corridas_${index}" required>
          </div>
          <div class="col-md-4 mb-2">
            <label for="color_${index}" class="form-label">Color</label>
            <input type="text" class="form-control" name="prenda[${index}][color]" id="color_${index}" required>
          </div>
        </div>
      `;
    }

    // Y así para cada tipo: “pollera_sucreña”, “juste_cochala”, “juste_sucreña”, “centro_cochala”, “centro_sucreña”, “inagua_cochala”, “inagua_sucreña” 
    // Con sus respectivos campos en blanco. Solo es copiar la estructura del HTML de tu modelo de medida y cambiar los names: prenda[index][campo].

    // Finalmente, agregamos un botón “Eliminar prenda” en cada bloque para facilitar la interfaz:
    contenedor.insertAdjacentHTML('beforeend', `
      <button type="button" class="btn btn-sm btn-danger mt-2 btnEliminarPrenda" data-index="${index}">
        Eliminar esta prenda
      </button>
    `);

    // Listener para “Eliminar prenda”
    contenedor.querySelector(`.btnEliminarPrenda[data-index="${index}"]`)
      .addEventListener('click', function() {
        document.querySelector(`.bloque-prenda[data-index="${index}"]`).remove();
      });
  }

  // 5) AGREGAR NUEVO BLOQUE DE PRENDA AL PRESIONAR “+ Añadir otra prenda”
  btnAgregarPrenda.addEventListener('click', function() {
    // Tomamos el bloqueBase, reemplazamos data-index="0" por el nuevo índice
    let nuevoBloqueHTML = bloqueBase.replace(/data-index="0"/g, `data-index="${contadorBloques}"`)
                                     .replace(/selectTipoPrenda_0/g, `selectTipoPrenda_${contadorBloques}`)
                                     .replace(/id="contenedorMedidas_0"/g, `id="contenedorMedidas_${contadorBloques}"`)
                                     .replace(/name="prenda\[0\]\[tipo_prenda\]"/g, `name="prenda[${contadorBloques}][tipo_prenda]"`)
                                     .replace(/name="prenda\[0\]\[medida_id\]"/g, `name="prenda[${contadorBloques}][medida_id]"`)
                                     .replace(/name="prenda\[0\]\[crear_medidas\]"/g, `name="prenda[${contadorBloques}][crear_medidas]"`);
    // Insertamos al final del último bloque de prenda
    const ultimoBloque = document.querySelector('.bloque-prenda[data-index]:last-of-type');
    ultimoBloque.insertAdjacentHTML('afterend', nuevoBloqueHTML);

    // Agregamos listener al nuevo select de prenda:
    const nuevoSelect = document.getElementById(`selectTipoPrenda_${contadorBloques}`);
    nuevoSelect.addEventListener('change', onChangeTipoPrenda);

    contadorBloques++;
  });

  // 6) VINCULAR AL SELECT DEL BLOQUE 0 el listener onChangeTipoPrenda
  document.getElementById('selectTipoPrenda_0').addEventListener('change', onChangeTipoPrenda);
 // Manejar envío del formulario de nuevo cliente
  const formClienteModal = document.getElementById('formCrearClienteModal');
  if (formClienteModal) {
    formClienteModal.addEventListener('submit', function(e) {
      e.preventDefault();
      const datos = new FormData(formClienteModal);
      // Reutilizamos el token CSRF generado en el formulario principal
      const csrf = document.querySelector('input[name="csrf_token"]').value;
      datos.append('csrf_token', csrf);
      fetch('/admin/clientes/nuevo_ajax', {
        method: 'POST',
        body: datos
      })
        .then(r => r.json())
        .then(resp => {
          if (resp.ok) {
            inputCliente.value = resp.nombre;
            clienteHidden.value = resp.id;
            const modal = bootstrap.Modal.getInstance(modalClienteEl);
            modal.hide();
          } else if (resp.errores) {
            document.getElementById('errorCliente').textContent = Object.values(resp.errores).join(' ');
          }
        });
    });
  }

  // 7) ESCUCHAR EDICIÓN DEL FORMULARIO PARA VALIDAR QUE EXISTA AL MENOS UNA PRENDA Y UN CLIENTE
  formPedido.addEventListener('submit', function(e) {
    // Validaciones extra (por ejemplo, must have cliente, must have al menos 1 prenda con sus medidas o medida_id)
    if (!clienteHidden.value) {
      alert('Debes seleccionar o registrar un cliente antes de guardar el pedido.');
      e.preventDefault();
      return;
    }
    // Verificar cada bloque que tenga prenda y medidas:
    const bloques = document.querySelectorAll('.bloque-prenda');
    let ok = false;
    bloques.forEach(div => {
      const index = div.dataset.index;
      const selectPrenda = document.getElementById(`selectTipoPrenda_${index}`);
      const medidaId = div.querySelector(`input[name="prenda[${index}][medida_id]"]`).value;
      const crearMed = div.querySelector(`input[name="prenda[${index}][crear_medidas]"]`).value;
      if (selectPrenda && selectPrenda.value) {
        // Si usar medida existente, medidaId debe tener un valor
        if (crearMed === 'off' && medidaId) {
          ok = true;
        }
        // Si crear medidas, al menos uno de los campos de medida debe estar completado (opcional: chequear más a fondo)
        if (crearMed === 'on') {
          ok = true;
        }
      }
    });
    if (!ok) {
      alert('Debes seleccionar al menos una prenda con sus medidas (o elegir una medida existente).');
      e.preventDefault();
      return;
    }
  });

  // 8) Si estamos EDITANDO un pedido, levantamos la prenda y las medidas guardadas (puedes rehacer esta parte según tus necesidades)
  {% if pedido %}
    // Aquí podrías precargar los selectTipoPrenda_x, contenedorMedidas_x con los valores de edición
  {% endif %}
});
