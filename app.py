import os
from datetime import datetime, date
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, SubmitField, IntegerField, FileField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import func

# -------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# -------------------------------------------------
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    return app

# Instancias globales
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'


# -------------------------------------------------
# MODELOS
# -------------------------------------------------
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id              = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    telefono        = db.Column(db.String(50), nullable=False)
    whatsapp        = db.Column(db.String(50), nullable=True)

    medidas = db.relationship('Medida', backref='cliente', lazy=True)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

    def __repr__(self):
        return f"<Cliente {self.nombre_completo}>"


class Medida(db.Model):
    __tablename__ = 'medidas'
    id                 = db.Column(db.Integer, primary_key=True)
    cliente_id         = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tipo_prenda        = db.Column(db.Enum(
        'blusa_cochala', 'blusa_sucreña',
        'pollera_cochala', 'pollera_sucreña',
        'juste_cochala', 'juste_sucreña',
        'centro_cochala', 'centro_sucreña',
        'inagua_cochala', 'inagua_sucreña',
        name='tipo_prenda_enum'
    ), nullable=False)

    # Campos de medida para todas las prendas (null si no aplica)
    largo_espalda     = db.Column(db.Numeric, nullable=True)
    largo_delantero   = db.Column(db.Numeric, nullable=True)
    cintura           = db.Column(db.Numeric, nullable=True)
    busto             = db.Column(db.Numeric, nullable=True)
    media_cintura     = db.Column(db.Numeric, nullable=True)
    sisa              = db.Column(db.Numeric, nullable=True)
    escote            = db.Column(db.Numeric, nullable=True)
    largo_manga       = db.Column(db.Numeric, nullable=True)
    puño             = db.Column(db.Numeric, nullable=True)
    cuello            = db.Column(db.Numeric, nullable=True)
    abertura          = db.Column(db.Numeric, nullable=True)
    ancho_espalda     = db.Column(db.Numeric, nullable=True)
    figura            = db.Column(db.String(100), nullable=True)

    alforza           = db.Column(db.Numeric, nullable=True)
    paños             = db.Column(db.Integer, nullable=True)
    wato              = db.Column(db.Numeric, nullable=True)
    corridas          = db.Column(db.Numeric, nullable=True)
    color             = db.Column(db.String(50), nullable=True)
    cadera            = db.Column(db.Numeric, nullable=True)
    talla             = db.Column(db.String(30), nullable=True)
    quebrado          = db.Column(db.Numeric, nullable=True)
    pierna            = db.Column(db.Numeric, nullable=True)

    fotos             = db.Column(db.String(200), nullable=True)  # Ruta o nombre de archivo con fotos

    pedidos           = db.relationship('Pedido', backref='medida', lazy=True)

    fecha_creacion     = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion= db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Medida {self.tipo_prenda} de Cliente {self.cliente_id}>"


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id              = db.Column(db.Integer, primary_key=True)
    numero_orden    = db.Column(db.String(20), unique=True, nullable=False)
    cliente_id      = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tipo_prenda     = db.Column(db.Enum(
        'blusa_cochala', 'blusa_sucreña',
        'pollera_cochala', 'pollera_sucreña',
        'juste_cochala', 'juste_sucreña',
        'centro_cochala', 'centro_sucreña',
        'inagua_cochala', 'inagua_sucreña',
        name='tipo_prenda_enum'
    ), nullable=False)
    medida_id       = db.Column(db.Integer, db.ForeignKey('medidas.id'), nullable=False)

    fecha_entrega    = db.Column(db.Date, nullable=False)
    adelanto         = db.Column(db.Numeric(scale=2), nullable=False)
    total            = db.Column(db.Numeric(scale=2), nullable=True)

    estado           = db.Column(db.Enum(
        'pendiente', 'en_proceso', 'listo_para_recoger', 'entregado',
        name='estado_pedido_enum'
    ), default='pendiente', nullable=False)

    fecha_creacion     = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion= db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Pedido {self.numero_orden} - Cliente {self.cliente_id}>"


class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nombre        = db.Column(db.String(150), nullable=False)
    rol           = db.Column(db.String(50), nullable=False, default='usuario')  # “administrador” o “usuario”

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------------------------------
# FORMULARIOS (Flask-WTF)
# -------------------------------------------------
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit   = SubmitField('Ingresar')


class ClienteForm(FlaskForm):
    nombre_completo = StringField('Nombre completo', validators=[DataRequired()])
    telefono        = StringField('Teléfono', validators=[DataRequired()])
    whatsapp        = StringField('WhatsApp', validators=[Optional()])
    submit          = SubmitField('Guardar Cliente')


class MedidaForm(FlaskForm):
    tipo_prenda = SelectField('Tipo de prenda', choices=[
        ('blusa_cochala',  'Blusa Cochala'),
        ('blusa_sucreña',  'Blusa Sucreña'),
        ('pollera_cochala','Pollera Cochala'),
        ('pollera_sucreña','Pollera Sucreña'),
        ('juste_cochala',  'Juste Cochala'),
        ('juste_sucreña',  'Juste Sucreña'),
        ('centro_cochala', 'Centro Cochala'),
        ('centro_sucreña', 'Centro Sucreña'),
        ('inagua_cochala', 'Inagua Cochala'),
        ('inagua_sucreña', 'Inagua Sucreña'),
    ], validators=[DataRequired()])

    # Campos para blusas
    largo_espalda   = DecimalField('Largo espalda',    validators=[Optional(), NumberRange(min=0)])
    largo_delantero = DecimalField('Largo delantero', validators=[Optional(), NumberRange(min=0)])
    cintura         = DecimalField('Cintura',         validators=[Optional(), NumberRange(min=0)])
    busto           = DecimalField('Busto',           validators=[Optional(), NumberRange(min=0)])
    media_cintura   = DecimalField('Media cintura',   validators=[Optional(), NumberRange(min=0)])
    sisa            = DecimalField('Sisa',            validators=[Optional(), NumberRange(min=0)])
    escote          = DecimalField('Escote',          validators=[Optional(), NumberRange(min=0)])
    largo_manga     = DecimalField('Largo manga',     validators=[Optional(), NumberRange(min=0)])
    puño            = DecimalField('Puño',            validators=[Optional(), NumberRange(min=0)])
    cuello          = DecimalField('Cuello',          validators=[Optional(), NumberRange(min=0)])
    abertura        = DecimalField('Abertura',        validators=[Optional(), NumberRange(min=0)])
    ancho_espalda   = DecimalField('Ancho espalda',   validators=[Optional(), NumberRange(min=0)])
    figura          = StringField('Figura',           validators=[Optional()])
    fotos           = FileField('Fotos (jpg/png)',   validators=[Optional()])

    # Campos para polleras
    alforza = DecimalField('Alforza',      validators=[Optional(), NumberRange(min=0)])
    paños   = IntegerField('Paños',        validators=[Optional(), NumberRange(min=0)])
    wato    = DecimalField('Wato',         validators=[Optional(), NumberRange(min=0)])
    corridas= DecimalField('Corridas',     validators=[Optional(), NumberRange(min=0)])
    color   = StringField('Color',         validators=[Optional()])
    cadera  = DecimalField('Cadera',       validators=[Optional(), NumberRange(min=0)])
    talla   = StringField('Talla',         validators=[Optional()])
    quebrado= DecimalField('Quebrado',     validators=[Optional(), NumberRange(min=0)])
    pierna  = DecimalField('Pierna',       validators=[Optional(), NumberRange(min=0)])

    submit = SubmitField('Guardar Medida')


class PedidoForm(FlaskForm):
    # Este formulario se usa para la parte "datos generales" (cliente_id, fecha, adelanto, total)
    cliente_id   = IntegerField('Cliente ID', validators=[Optional()])
    tipo_prenda  = SelectField('Tipo de prenda', choices=[
        ('', '--- Seleccionar ---'),
        ('blusa_cochala',  'Blusa Cochala'),
        ('blusa_sucreña',  'Blusa Sucreña'),
        ('pollera_cochala','Pollera Cochola'),
        ('pollera_sucreña','Pollera Sucreña'),
        ('juste_cochala',  'Juste Cochola'),
        ('juste_sucreña',  'Juste Sucreña'),
        ('centro_cochala', 'Centro Cochola'),
        ('centro_sucreña', 'Centro Sucreña'),
        ('inagua_cochala', 'Inagua Cochola'),
        ('inagua_sucreña', 'Inagua Sucreña'),
    ], validators=[DataRequired()])

    fecha_entrega = DateField('Fecha de entrega', validators=[DataRequired()])
    adelanto      = DecimalField('Adelanto (Bs)', validators=[DataRequired(), NumberRange(min=0)])
    total         = DecimalField('Total (Bs)',    validators=[Optional(), NumberRange(min=0)])
    submit        = SubmitField('Guardar Pedido')


class RastrearForm(FlaskForm):
    numero_orden = StringField('Número de orden', validators=[DataRequired()])
    submit       = SubmitField('Buscar')


# -------------------------------------------------
# APLICACIÓN FLASK
# -------------------------------------------------
app = create_app()


# Decorador para restringir solo a usuarios con rol “administrador”
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'administrador':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# -------------------------------------------------
# RUTA LOGIN / LOGOUT
# -------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # A modo de ejemplo, si el usuario no existe lo creamos con rol administrador
        usuario = User.query.filter_by(username=form.username.data).first()
        if not usuario:
            usuario = User(
                username=form.username.data,
                password_hash='dummy',  # Password no validado aquí
                nombre=form.username.data,
                rol='administrador'
            )
            db.session.add(usuario)
            db.session.commit()

        login_user(usuario)
        return redirect(request.args.get('next') or url_for('dashboard'))

    return render_template('admin/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# -------------------------------------------------
# DASHBOARD / MÉTRICAS
# -------------------------------------------------
@app.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    hoy = date.today()
    hace_30 = hoy.replace(day=1)
    total_30 = Pedido.query.filter(Pedido.fecha_creacion >= hace_30).count()

    # Conteo por estado
    estados = db.session.query(Pedido.estado, func.count(Pedido.id)) \
        .group_by(Pedido.estado).all()

    pendientes_hoy = Pedido.query.filter(
        Pedido.estado == 'pendiente',
        Pedido.fecha_entrega == hoy
    ).all()

    hace_7 = date.fromordinal(hoy.toordinal() - 7)
    clientes_semana = Cliente.query.filter(Cliente.id.in_(
        db.session.query(Medida.cliente_id).filter(Medida.fecha_creacion >= hace_7)
    )).count()

    ultimos_5 = Pedido.query.order_by(Pedido.fecha_creacion.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_30=total_30,
                           estados=estados,
                           pendientes_hoy=pendientes_hoy,
                           clientes_semana=clientes_semana,
                           ultimos_5=ultimos_5)


# -------------------------------------------------
# RUTAS DE CLIENTES
# -------------------------------------------------
@app.route('/admin/clientes')
@login_required
@admin_required
def clientes_list():
    clientes = Cliente.query.order_by(Cliente.nombre_completo).all()
    return render_template('admin/clientes_list.html', clientes=clientes)


@app.route('/admin/clientes/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def cliente_nuevo():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = Cliente(
            nombre_completo=form.nombre_completo.data.strip(),
            telefono=form.telefono.data.strip(),
            whatsapp=form.whatsapp.data.strip() if form.whatsapp.data else None
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado exitosamente.', 'success')
        return redirect(url_for('clientes_list'))
    return render_template('admin/cliente_modal.html',
                           form=form,
                           action_url=url_for('cliente_nuevo'),
                           titulo='Nuevo Cliente')


@app.route('/admin/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def cliente_editar(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = ClienteForm(obj=cliente)
    if form.validate_on_submit():
        cliente.nombre_completo = form.nombre_completo.data.strip()
        cliente.telefono = form.telefono.data.strip()
        cliente.whatsapp = form.whatsapp.data.strip() if form.whatsapp.data else None
        db.session.commit()
        flash('Cliente actualizado.', 'success')
        return redirect(url_for('clientes_list'))
    return render_template('admin/cliente_modal.html',
                           form=form,
                           action_url=url_for('cliente_editar', cliente_id=cliente.id),
                           titulo='Editar Cliente')


@app.route('/admin/clientes/buscar')
@login_required
@admin_required
def buscar_cliente():
    """
    Búsqueda de clientes para autocompletar (AJAX).
    ?q=texto
    """
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    resultados = Cliente.query.filter(
        Cliente.nombre_completo.ilike(f'%{q}%')
    ).limit(10).all()

    lista = [{'id': c.id, 'nombre': c.nombre_completo} for c in resultados]
    return jsonify(lista)


# -------------------------------------------------
# RUTAS DE MEDIDAS
# -------------------------------------------------
@app.route('/admin/clientes/<int:cliente_id>/medidas/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def agregar_medida(cliente_id):
    form = MedidaForm()
    if form.validate_on_submit():
        nueva = Medida(
            cliente_id=cliente_id,
            tipo_prenda=form.tipo_prenda.data
        )
        for campo in form:
            nombre = campo.name
            if nombre not in ['csrf_token', 'tipo_prenda', 'submit']:
                valor = getattr(form, nombre).data
                if valor:
                    setattr(nueva, nombre, valor)
        db.session.add(nueva)
        db.session.commit()
        flash('Medida agregada.', 'success')
        return redirect(url_for('clientes_list'))

    return render_template('admin/medida_form.html',
                           form=form,
                           action_url=url_for('agregar_medida', cliente_id=cliente_id),
                           editar=False,
                           cliente_id=cliente_id)


@app.route('/admin/medidas/<int:medida_id>/json')
@login_required
@admin_required
def json_medida(medida_id):
    """
    Devuelve JSON con los valores de una Medida específica (para precargar en formulario).
    """
    m = Medida.query.get_or_404(medida_id)
    data = {
        'largo_espalda':    str(m.largo_espalda or ''),
        'largo_delantero':  str(m.largo_delantero or ''),
        'cintura':          str(m.cintura or ''),
        'busto':            str(m.busto or ''),
        'media_cintura':    str(m.media_cintura or ''),
        'sisa':             str(m.sisa or ''),
        'escote':           str(m.escote or ''),
        'largo_manga':      str(m.largo_manga or ''),
        'puño':             str(m.puño or ''),
        'cuello':           str(m.cuello or ''),
        'abertura':         str(m.abertura or ''),
        'ancho_espalda':    str(m.ancho_espalda or ''),
        'figura':           m.figura or '',
        'alforza':          str(m.alforza or ''),
        'paños':            m.paños or '',
        'wato':             str(m.wato or ''),
        'corridas':         str(m.corridas or ''),
        'color':            m.color or '',
        'cadera':           str(m.cadera or ''),
        'talla':            m.talla or '',
        'quebrado':         str(m.quebrado or ''),
        'pierna':           str(m.pierna or ''),
        'fotos':            m.fotos or ''
    }
    return jsonify({'medida': data})


@app.route('/admin/medidas/<int:medida_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_medida(medida_id):
    medida = Medida.query.get_or_404(medida_id)
    form = MedidaForm(obj=medida)
    if form.validate_on_submit():
        medida.tipo_prenda = form.tipo_prenda.data
        for campo in form:
            nombre = campo.name
            if nombre not in ['csrf_token', 'tipo_prenda', 'submit']:
                valor = getattr(form, nombre).data
                setattr(medida, nombre, valor)
        db.session.commit()
        flash('Medida actualizada.', 'success')
        return redirect(url_for('clientes_list'))

    return render_template('admin/medida_form.html',
                           form=form,
                           action_url=url_for('editar_medida', medida_id=medida.id),
                           editar=True,
                           medida=medida)


@app.route('/admin/clientes/<int:cliente_id>/medidas/<tipo_prenda>')
@login_required
@admin_required
def obtener_medida(cliente_id, tipo_prenda):
    """
    RUTA AJAX: Devuelve JSON con la última Medida registrada para el cliente y tipo_prenda dado.
    """
    medida = Medida.query.filter_by(
        cliente_id=cliente_id,
        tipo_prenda=tipo_prenda
    ).order_by(Medida.fecha_creacion.desc()).first()

    if medida:
        data = {
            'id': medida.id,
            'tipo_prenda': medida.tipo_prenda,
            'largo_espalda':    str(medida.largo_espalda or ''),
            'largo_delantero':  str(medida.largo_delantero or ''),
            'cintura':          str(medida.cintura or ''),
            'busto':            str(medida.busto or ''),
            'media_cintura':    str(medida.media_cintura or ''),
            'sisa':             str(medida.sisa or ''),
            'escote':           str(medida.escote or ''),
            'largo_manga':      str(medida.largo_manga or ''),
            'puño':             str(medida.puño or ''),
            'cuello':           str(medida.cuello or ''),
            'abertura':         str(medida.abertura or ''),
            'ancho_espalda':    str(medida.ancho_espalda or ''),
            'figura':           medida.figura or '',
            'alforza':          str(medida.alforza or ''),
            'paños':            medida.paños or '',
            'wato':             str(medida.wato or ''),
            'corridas':         str(medida.corridas or ''),
            'color':            medida.color or '',
            'cadera':           str(medida.cadera or ''),
            'talla':            medida.talla or '',
            'quebrado':         str(medida.quebrado or ''),
            'pierna':           str(medida.pierna or '')
        }
        return jsonify({'existe': True, 'medida': data})
    else:
        return jsonify({'existe': False})


# -------------------------------------------------
# RUTAS DE PEDIDOS
# -------------------------------------------------
@app.route('/admin/pedidos')
@login_required
@admin_required
def pedidos_list():
    pedidos = Pedido.query.order_by(Pedido.fecha_creacion.desc()).all()
    return render_template('admin/pedidos_list.html', pedidos=pedidos)


@app.route('/admin/pedidos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def pedido_nuevo():
    """
    Ruta para crear uno o varios pedidos en un solo envío.
    """
    form = PedidoForm()  # ✅ Importante: para CSRF y validaciones
    tipos_prenda = [
        'blusa_cochala', 'blusa_sucreña',
        'pollera_cochala', 'pollera_sucreña',
        'juste_cochala', 'juste_sucreña',
        'centro_cochala', 'centro_sucreña',
        'inagua_cochala', 'inagua_sucreña'
    ]
    if request.method == 'POST':
        # 1) Datos generales
        cliente_id = request.form.get('cliente_id')
        fecha_entrega = request.form.get('fecha_entrega')
        adelanto = request.form.get('adelanto')
        total = request.form.get('total') or None

        errores = []
        if not cliente_id:
            errores.append('Debe seleccionar un cliente válido.')
        else:
            cliente = Cliente.query.get(int(cliente_id))
            if not cliente:
                errores.append('El cliente seleccionado no existe.')

        # Validar fecha_entrega
        try:
            fecha_entrega_date = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
            if fecha_entrega_date < date.today():
                errores.append('La fecha de entrega no puede ser anterior a hoy.')
        except:
            errores.append('Formato de fecha inválido.')

        # Validar adelanto
        try:
            adelanto_val = float(adelanto)
            if adelanto_val < 0:
                errores.append('El adelanto debe ser mayor o igual a 0.')
        except:
            errores.append('El adelanto debe ser un número válido.')

        # Validar total
        total_val = None
        if total:
            try:
                total_val = float(total)
                if total_val < 0:
                    errores.append('El total debe ser mayor o igual a 0.')
            except:
                errores.append('El total debe ser un número válido.')

        # 2) Recopilar todos los bloques prenda[i]
        indices = set()
        for key in request.form.keys():
            if key.startswith('prenda['):
                parte = key.split(']')[0]
                idx = parte.replace('prenda[', '')
                try:
                    indices.add(int(idx))
                except:
                    pass

        if not indices:
            errores.append('Debe agregar al menos una prenda al pedido.')

        # 3) Validar cada bloque de prenda
        bloques_info = []
        for i in sorted(indices):
            tipo_prenda = request.form.get(f'prenda[{i}][tipo_prenda]')
            medida_id   = request.form.get(f'prenda[{i}][medida_id]')
            crear_med   = request.form.get(f'prenda[{i}][crear_medidas]')

            if not tipo_prenda:
                errores.append(f'En la prenda #{i+1} debe seleccionar un tipo de prenda.')
                continue

            medida_campos = {}
            for campo in [
                'largo_espalda','largo_delantero','cintura','busto','media_cintura','sisa',
                'escote','largo_manga','puño','cuello','abertura','ancho_espalda','figura',
                'alforza','paños','wato','corridas','color','cadera','talla','quebrado','pierna'
            ]:
                valor = request.form.get(f'prenda[{i}][{campo}]')
                if valor and valor.strip() != '':
                    medida_campos[campo] = valor.strip()

            obligatorios = []
            if tipo_prenda in ['blusa_cochala', 'blusa_sucreña']:
                obligatorios = [
                    'largo_espalda','largo_delantero','cintura','busto','media_cintura',
                    'sisa','escote','largo_manga','puño','cuello','abertura','ancho_espalda','figura'
                ]
            elif tipo_prenda == 'pollera_cochala':
                obligatorios = ['cintura','alforza','paños','wato','corridas','color']
            elif tipo_prenda == 'pollera_sucreña':
                obligatorios = ['cintura','cadera','talla','paños','quebrado','wato','color','figura']
            elif tipo_prenda in ['juste_cochala', 'juste_sucreña', 'inagua_cochala', 'inagua_sucreña']:
                obligatorios = ['cintura','cadera','pierna','talla']
            elif tipo_prenda == 'centro_cochala':
                obligatorios = ['cintura','talla']
            elif tipo_prenda == 'centro_sucreña':
                obligatorios = ['cintura','cadera','quebrado','talla']

            if crear_med == 'on':
                for campo in obligatorios:
                    if campo not in medida_campos:
                        errores.append(f'Prenda #{i+1}: falta el campo de medida "{campo.replace("_"," ").title()}".')
            else:
                if not medida_id:
                    errores.append(f'Prenda #{i+1}: debe elegir una medida existente o editar para crear nuevas.')
                else:
                    if not Medida.query.get(int(medida_id)):
                        errores.append(f'Prenda #{i+1}: la medida seleccionada no existe.')

            bloques_info.append({
                'tipo_prenda': tipo_prenda,
                'medida_id': medida_id,
                'crear_med': crear_med,
                'campos': medida_campos
            })

        # Si hay errores
        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('admin/pedido_form.html', form=form, hoy=datetime.today())

        # 4) Crear medidas y pedidos
        for bloque in bloques_info:
            tipo_prenda = bloque['tipo_prenda']
            medida_id   = bloque['medida_id']
            crear_med   = bloque['crear_med']
            campos      = bloque['campos']

            if crear_med == 'off':
                medida_id_final = int(medida_id)
            else:
                nueva = Medida(
                    cliente_id=int(cliente_id),
                    tipo_prenda=tipo_prenda
                )
                for campo, valor in campos.items():
                    if campo == 'paños':
                        setattr(nueva, campo, int(valor))
                    elif campo in ['figura', 'color', 'talla', 'fotos']:
                        setattr(nueva, campo, valor)
                    else:
                        setattr(nueva, campo, float(valor))
                db.session.add(nueva)
                db.session.flush()
                medida_id_final = nueva.id

            año = datetime.now().year
            conteo = Pedido.query.filter(
                func.strftime('%Y', Pedido.fecha_creacion) == str(año)
            ).count()
            secuencial = conteo + 1
            numero = f"MP-{año}-{secuencial:04d}"
            while Pedido.query.filter_by(numero_orden=numero).first():
                secuencial += 1
                numero = f"MP-{año}-{secuencial:04d}"

            nuevo_pedido = Pedido(
                numero_orden = numero,
                cliente_id   = int(cliente_id),
                tipo_prenda  = tipo_prenda,
                medida_id    = medida_id_final,
                fecha_entrega= fecha_entrega_date,
                adelanto     = float(adelanto),
                total        = total_val,
                estado       = 'pendiente'
            )
            db.session.add(nuevo_pedido)

        # 5) Guardar todo
        db.session.commit()
        flash('Pedido(s) creado(s) exitosamente.', 'success')
        return redirect(url_for('pedidos_list'))
    

    # GET: formulario vacío con protección CSRF
    return render_template('admin/pedido_form.html', form=form, hoy=datetime.today(), tipos_prenda=tipos_prenda)




@app.route('/admin/pedidos/<int:pedido_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def pedido_editar(pedido_id):
    """
    Edición de un pedido individual.
    (No está contemplada la edición de múltiples ítems; se edita uno por uno.)
    """
    pedido = Pedido.query.get_or_404(pedido_id)
    form = PedidoForm(
        tipo_prenda=pedido.tipo_prenda,
        fecha_entrega=pedido.fecha_entrega,
        adelanto=pedido.adelanto,
        total=pedido.total
    )
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        tipo_prenda = request.form.get('tipo_prenda')
        fecha_entrega = form.fecha_entrega.data
        adelanto = form.adelanto.data
        total = form.total.data if form.total.data else None

        errores = []
        if not cliente_id:
            errores.append('Debe seleccionar un cliente válido.')
        else:
            cliente = Cliente.query.get(int(cliente_id))
            if not cliente:
                errores.append('El cliente seleccionado no existe.')

        if not tipo_prenda:
            errores.append('Debe seleccionar un tipo de prenda.')

        if fecha_entrega < date.today():
            errores.append('La fecha de entrega no puede ser anterior a hoy.')

        if adelanto is None or adelanto < 0:
            errores.append('El adelanto debe ser numérico y mayor o igual a 0.')

        # Validación de campos de medida (idéntica a nuevo, pero solo un bloque)
        medida_campos = {}
        for campo in [
            'largo_espalda','largo_delantero','cintura','busto','media_cintura','sisa',
            'escote','largo_manga','puño','cuello','abertura','ancho_espalda','figura',
            'alforza','paños','wato','corridas','color','cadera','talla','quebrado','pierna'
        ]:
            valor = request.form.get(campo)
            if valor and valor.strip() != '':
                medida_campos[campo] = valor.strip()

        obligatorios = []
        if tipo_prenda in ['blusa_cochala', 'blusa_sucreña']:
            obligatorios = [
                'largo_espalda','largo_delantero','cintura','busto','media_cintura',
                'sisa','escote','largo_manga','puño','cuello','abertura','ancho_espalda','figura'
            ]
        elif tipo_prenda == 'pollera_cochala':
            obligatorios = ['cintura','alforza','paños','wato','corridas','color']
        elif tipo_prenda == 'pollera_sucreña':
            obligatorios = ['cintura','cadera','talla','paños','quebrado','wato','color','figura']
        elif tipo_prenda in ['juste_cochala', 'juste_sucreña', 'inagua_cochala', 'inagua_sucreña']:
            obligatorios = ['cintura','cadera','pierna','talla']
        elif tipo_prenda == 'centro_cochala':
            obligatorios = ['cintura','talla']
        elif tipo_prenda == 'centro_sucreña':
            obligatorios = ['cintura','cadera','quebrado','talla']

        for campo in obligatorios:
            if campo not in medida_campos:
                errores.append(f'Falta el campo de medida: {campo.replace("_", " ").title()}.')

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('admin/pedido_form.html', form=form, editar=True, pedido=pedido)

        # Actualizar o crear medida
        medida_existente = Medida.query.filter_by(
            cliente_id=int(cliente_id),
            tipo_prenda=tipo_prenda
        ).order_by(Medida.fecha_creacion.desc()).first()

        if medida_existente:
            for campo, valor in medida_campos.items():
                if campo == 'paños':
                    setattr(medida_existente, campo, int(valor))
                elif campo in ['figura', 'color', 'talla', 'fotos']:
                    setattr(medida_existente, campo, valor)
                else:
                    setattr(medida_existente, campo, float(valor))
            db.session.commit()
            medida_id_final = medida_existente.id
        else:
            nueva = Medida(cliente_id=int(cliente_id), tipo_prenda=tipo_prenda)
            for campo, valor in medida_campos.items():
                if campo == 'paños':
                    setattr(nueva, campo, int(valor))
                elif campo in ['figura', 'color', 'talla', 'fotos']:
                    setattr(nueva, campo, valor)
                else:
                    setattr(nueva, campo, float(valor))
            db.session.add(nueva)
            db.session.flush()
            medida_id_final = nueva.id

        # Actualizar pedido
        pedido.cliente_id    = int(cliente_id)
        pedido.tipo_prenda   = tipo_prenda
        pedido.medida_id     = medida_id_final
        pedido.fecha_entrega = fecha_entrega
        pedido.adelanto      = adelanto
        pedido.total         = total
        db.session.commit()

        flash(f'Pedido {pedido.numero_orden} actualizado.', 'success')
        return redirect(url_for('pedidos_list'))

    return render_template('admin/pedido_form.html', form=form, hoy=datetime.today())


@app.route('/admin/pedidos/<int:pedido_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def pedido_eliminar(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    numero = pedido.numero_orden
    db.session.delete(pedido)
    db.session.commit()
    flash(f'Pedido {numero} eliminado.', 'success')
    return redirect(url_for('pedidos_list'))


# -------------------------------------------------
# RUTAS PÚBLICAS
# -------------------------------------------------
@app.route('/public/rastrear', methods=['GET', 'POST'])
def rastrear_pedido():
    form = RastrearForm()
    if form.validate_on_submit():
        numero = form.numero_orden.data.strip()
        pedido = Pedido.query.filter_by(numero_orden=numero).first()
        if pedido:
            return render_template('public/rastrear_resultado.html', pedido=pedido)
        else:
            flash('No existe ningún pedido con ese número.', 'warning')
            return redirect(url_for('rastrear_pedido'))
    return render_template('public/rastrear_pedido.html', form=form)


# -------------------------------------------------
# MANEJO DE ERRORES
# -------------------------------------------------
@app.errorhandler(403)
def acceso_denegado(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
