// pedido_form.js

$(document).ready(function() {
  $('#autocompleteCliente').on('input', function() {
    let query = $(this).val().trim();
    if (query.length < 2) {
      $('#infoClienteSeleccionado').html('');
      $('#cliente_id').val('');
      return;
    }
    $.ajax({
      url: '/admin/clientes/buscar',
      data: { q: query },
      success: function(data) {
        let lista = $('<ul class="list-group position-absolute" style="z-index: 10000; width: 90%;"></ul>');
        data.forEach(function(item) {
          let opcion = $(`<li class="list-group-item list-group-item-action" data-id="${item.id}">${item.nombre}</li>`);
          opcion.on('click', function() {
            $('#autocompleteCliente').val(item.nombre);
            $('#cliente_id').val(item.id);
            $('#infoClienteSeleccionado').html(`<strong>Cliente seleccionado:</strong> ${item.nombre}`);
            lista.remove();
          });
          lista.append(opcion);
        });
        $('.list-group.position-absolute').remove();
        $('#autocompleteCliente').after(lista);
      }
    });
  });

  $(document).on('click', function(e) {
    if (!$(e.target).closest('#autocompleteCliente').length) {
      $('.list-group.position-absolute').remove();
    }
  });

  function generarBloquesMedida() {
    const contenedor = $('#bloque_medidas');
    contenedor.empty();

    const bloques = {
      'blusa_cochala': [
        { label: 'Largo espalda', name: 'largo_espalda', type: 'number' },
        { label: 'Largo delantero', name: 'largo_delantero', type: 'number' },
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Busto', name: 'busto', type: 'number' },
        { label: 'Media cintura', name: 'media_cintura', type: 'number' },
        { label: 'Sisa', name: 'sisa', type: 'number' },
        { label: 'Escote', name: 'escote', type: 'number' },
        { label: 'Largo manga', name: 'largo_manga', type: 'number' },
        { label: 'Puño', name: 'puño', type: 'number' },
        { label: 'Cuello', name: 'cuello', type: 'number' },
        { label: 'Abertura', name: 'abertura', type: 'number' },
        { label: 'Ancho espalda', name: 'ancho_espalda', type: 'number' },
        { label: 'Figura', name: 'figura', type: 'text' }
      ],
      'blusa_sucreña': [
        { label: 'Largo espalda', name: 'largo_espalda', type: 'number' },
        { label: 'Largo delantero', name: 'largo_delantero', type: 'number' },
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Busto', name: 'busto', type: 'number' },
        { label: 'Media cintura', name: 'media_cintura', type: 'number' },
        { label: 'Sisa', name: 'sisa', type: 'number' },
        { label: 'Escote', name: 'escote', type: 'number' },
        { label: 'Largo manga', name: 'largo_manga', type: 'number' },
        { label: 'Puño', name: 'puño', type: 'number' },
        { label: 'Cuello', name: 'cuello', type: 'number' },
        { label: 'Abertura', name: 'abertura', type: 'number' },
        { label: 'Ancho espalda', name: 'ancho_espalda', type: 'number' },
        { label: 'Figura', name: 'figura', type: 'text' }
      ],
      'pollera_cochala': [
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Alforza', name: 'alforza', type: 'number' },
        { label: 'Paños', name: 'paños', type: 'number' },
        { label: 'Wato', name: 'wato', type: 'number' },
        { label: 'Corridas', name: 'corridas', type: 'number' },
        { label: 'Color', name: 'color', type: 'text' }
      ],
      'pollera_sucreña': [
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Cadera', name: 'cadera', type: 'number' },
        { label: 'Talla', name: 'talla', type: 'text' },
        { label: 'Paños', name: 'paños', type: 'number' },
        { label: 'Quebrado', name: 'quebrado', type: 'number' },
        { label: 'Wato', name: 'wato', type: 'number' },
        { label: 'Color', name: 'color', type: 'text' },
        { label: 'Figura', name: 'figura', type: 'text' }
      ],
      'juste_cochala': [
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Cadera', name: 'cadera', type: 'number' },
        { label: 'Pierna', name: 'pierna', type: 'number' },
        { label: 'Talla', name: 'talla', type: 'text' }
      ],
      'juste_sucreña': [
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Cadera', name: 'cadera', type: 'number' },
        { label: 'Pierna', name: 'pierna', type: 'number' },
        { label: 'Talla', name: 'talla', type: 'text' }
      ],
      'centro_cochala': [
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Talla', name: 'talla', type: 'text' }
      ],
      'centro_sucreña': [
        { label: 'Cintura', name: 'cintura', type: 'number' },
        { label: 'Cadera', name: 'cadera', type: 'number' },
        { label: 'Quebrado', name: 'quebrado', type: 'number' },
        { label: 'Talla', name: 'talla', type: 'text' }
      ]
    };

    for (const [tipo, campos] of Object.entries(bloques)) {
      let card = $('<div>', { class: 'bloque-prenda card-medida', id: `bloque_${tipo}` });
      card.append(`<h5>${tipo.replace('_',' ').toUpperCase()}</h5>`);
      let fila = $('<div class="row"></div>');
      campos.forEach(function(info) {
        let col = $('<div class="col-md-3 mb-2"></div>');
        let grupo = $('<div class="form-group"></div>');
        grupo.append(`<label class="form-label" for="${info.name}">${info.label}</label>`);
        let input = $(`<input type="${info.type}" class="form-control" name="${info.name}" id="${info.name}" ${info.type === 'number' ? 'step="0.01"' : ''}>`);
        grupo.append(input);
        col.append(grupo);
        fila.append(col);
      });
      card.append(fila);
      contenedor.append(card);
    }
  }

  generarBloquesMedida();

  $('#tipo_prenda').on('change', function() {
    let seleccionado = $(this).val();
    $('.bloque-prenda').removeClass('activo');
    if (seleccionado) {
      $(`#bloque_${seleccionado}`).addClass('activo');
      let clienteId = $('#cliente_id').val();
      if (clienteId) {
        cargarMedida(clienteId, seleccionado);
      }
    }
  });

  function cargarMedida(clienteId, tipoPrenda) {
    $.ajax({
      url: `/admin/clientes/${clienteId}/medidas/${tipoPrenda}`,
      method: 'GET',
      success: function(res) {
        if (res.existe) {
          const datos = res.medida;
          Object.keys(datos).forEach(function(campo) {
            if ($('#' + campo).length) {
              $('#' + campo).val(datos[campo]);
              $('#' + campo).prop('readonly', true);
            }
          });
          if (!$('#btnEditarMedidas').length) {
            let btn = $('<button class="btn btn-warning mb-3" id="btnEditarMedidas">Editar medidas</button>');
            btn.on('click', function(e) {
              e.preventDefault();
              $(`#bloque_${tipoPrenda} input`).prop('readonly', false);
              $(this).remove();
            });
            $(`#bloque_${tipoPrenda}`).prepend(btn);
          }
        } else {
          $(`#bloque_${tipoPrenda} input`).val('');
          $(`#btnEditarMedidas`).remove();
        }
      }
    });
  }

  if (EDITANDO && CLIENTE_ID_ACTUAL && TIPO_PRENDA_ACTUAL) {
    $('#autocompleteCliente').on('focus', function() {
      $.ajax({
        url: '/admin/clientes/buscar',
        data: { q: '' },
        success: function(data) {
          const encontrado = data.find(c => c.id === CLIENTE_ID_ACTUAL);
          if (encontrado) {
            $('#autocompleteCliente').val(encontrado.nombre);
            $('#cliente_id').val(encontrado.id);
            $('#infoClienteSeleccionado').html(`<strong>Cliente seleccionado:</strong> ${encontrado.nombre}`);
          }
        }
      });
    }).trigger('focus');
    $('#tipo_prenda').val(TIPO_PRENDA_ACTUAL).trigger('change');
    cargarMedida(CLIENTE_ID_ACTUAL, TIPO_PRENDA_ACTUAL);
  }

  $('#formPedido').on('submit', function(e) {
    let errores = [];
    const clienteId = $('#cliente_id').val();
    if (!clienteId) {
      errores.push('Debe seleccionar un cliente.');
    }
    const tipo = $('#tipo_prenda').val();
    if (!tipo) {
      errores.push('Debe seleccionar un tipo de prenda.');
    }
    const fechaEntrega = new Date($('#fecha_entrega').val());
    const hoy = new Date();
    hoy.setHours(0,0,0,0);
    if (fechaEntrega < hoy || isNaN(fechaEntrega)) {
      errores.push('La fecha de entrega no puede ser anterior a hoy.');
    }
    const adelanto = parseFloat($('#adelanto').val());
    if (isNaN(adelanto) || adelanto < 0) {
      errores.push('El adelanto debe ser numérico y ≥ 0.');
    }
    const camposRequeridos = {
      'blusa_cochala': ['largo_espalda','largo_delantero','cintura','busto','media_cintura','sisa','escote','largo_manga','puño','cuello','abertura','ancho_espalda','figura'],
      'blusa_sucreña': ['largo_espalda','largo_delantero','cintura','busto','media_cintura','sisa','escote','largo_manga','puño','cuello','abertura','ancho_espalda','figura'],
      'pollera_cochala': ['cintura','alforza','paños','wato','corridas','color'],
      'pollera_sucreña': ['cintura','cadera','talla','paños','quebrado','wato','color','figura'],
      'juste_cochala': ['cintura','cadera','pierna','talla'],
      'juste_sucreña': ['cintura','cadera','pierna','talla'],
      'centro_cochala': ['cintura','talla'],
      'centro_sucreña': ['cintura','cadera','quebrado','talla']
    };
    if (tipo && camposRequeridos[tipo]) {
      camposRequeridos[tipo].forEach(function(campo) {
        const val = $('#' + campo).val();
        if (val === undefined || val.trim() === '') {
          errores.push(`El campo ${campo.replace('_',' ').toUpperCase()} es obligatorio.`);
        } else if ($('#' + campo).attr('type') === 'number' && isNaN(parseFloat(val))) {
          errores.push(`El campo ${campo.replace('_',' ').toUpperCase()} debe ser numérico.`);
        }
      });
    }
    if (errores.length) {
      e.preventDefault();
      let html = '<ul>';
      errores.forEach(function(err) {
        html += `<li>${err}</li>`;
      });
      html += '</ul>';
      alert(html);
    }
  });

  window.abrirModalCliente = function(url, titulo) {
    $('#clienteModalTitle').text(titulo);
    $('#clienteModalBody').load(url);
  };

  window.abrirMedidaModal = function(url, titulo) {
    $('#medidaModalTitle').text(titulo);
    $('#medidaModalBody').load(url);
  };
});
