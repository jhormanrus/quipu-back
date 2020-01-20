from flask import Flask, jsonify, json, request, make_response
from jose import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import datetime
from functools import wraps
from flask_mysqldb import MySQL
from decimal import Decimal

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'db.codsit.com'
app.config['MYSQL_USER'] = 'cashflow'
app.config['MYSQL_PASSWORD'] = 'quipucash'
app.config['MYSQL_DB'] = 'cashflow'
app.config['SECRET_KEY'] = 'lallaveestaentucorazon'

mysql = MySQL(app)

### REQUIRE TOKEN TO URLS
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

########################################## MOVIMIENTO METHODS ##########################################

@app.route("/movimiento/readall/", methods=['POST'])
@token_required
def movimiento_readall():
    data = (request.get_json(force=True))

    cashflow = ""
    index = 1
    for i in data['CASHFLOW']:
        if index == len(data['CASHFLOW']):
            cashflow = cashflow + str(i)
        else:
            cashflow = cashflow + str(i) + ", "
        index = index + 1

    usuario = ""
    index = 1
    for i in data['USUARIO']:
        if index == len(data['USUARIO']):
            usuario = usuario + str(i)
        else:
            usuario = usuario + str(i) + ", "
        index = index + 1

    cuenta = ""
    index = 1
    for i in data['CUENTA']:
        if index == len(data['CUENTA']):
            cuenta = cuenta + str(i)
        else:
            cuenta = cuenta + str(i) + ", "
        index = index + 1

    criterio = ""
    index = 1
    for i in data['CRITERIO']:
        if index == len(data['CRITERIO']):
            criterio = criterio + str(i)
        else:
            criterio = criterio + str(i) + ", "
        index = index + 1

    tipo = ""
    index = 1
    for i in data['TIPO']:
        if index == len(data['TIPO']):
            tipo = tipo + str(i)
        else:
            tipo = tipo + str(i) + ", "
        index = index + 1

    cur = mysql.connection.cursor()
    cur.execute("SET @ROWNUMA := 0")
    cur.execute("SET @ROWNUME := 0")
    cur.execute("SELECT M.ID_CASHFLOW, M.ID_CUENTAS, M.ID_CRITERIOS_CF, M.ID_MOVIMIENTOS, M.MONTO, M.GLOSA, M.FECHA_CREACION, M.ID_USU, M.TIPO, A.ID AS ID_A, E.ID AS ID_E FROM MOVIMIENTOS M, CASHFLOW C, (SELECT @ROWNUMA := @ROWNUMA + 1 AS ID, C.* FROM CUENTAS C ORDER BY ID_CASHFLOW) A, (SELECT @ROWNUME := @ROWNUME + 1 AS ID, C.* FROM CRITERIOS_CF C ORDER BY ID_CASHFLOW) E WHERE M.ID_CASHFLOW = C.ID_CASHFLOW AND M.ID_CASHFLOW = A.ID_CASHFLOW AND M.ID_CUENTAS = A.ID_CUENTAS AND M.ID_CASHFLOW = E.ID_CASHFLOW AND M.ID_CRITERIOS_CF = E.ID_CRITERIOS_CF AND M.ID_CASHFLOW IN (" + cashflow + ") AND M.ID_USU IN (" + usuario + ") AND A.ID IN (" + cuenta + ") AND E.ID IN (" + criterio + ") AND M.TIPO IN ("+tipo+") ORDER BY FECHA_CREACION DESC")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        lineL = list(line)
        lineL[4] = float(lineL[4])
        lineL[6] = lineL[6].strftime('%Y-%m-%d %H:%M:%S')
        line = tuple(lineL)
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    return jsonify(json_data)

@app.route("/movimiento/read/", methods=['POST'])
@token_required
def movimiento_read():
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT R.NOMBRE AS R_NOMBRE, M.MONTO AS M_MONTO, U.NOMBRES, U.APELLIDOS, U.AVATAR, U.USERNAME, F.NOMBRE AS F_NOMBRE, M.TIPO AS M_TIPO, C.ID_TIPO AS C_TIPO, C.NOMBRE, C.INT_BANCARIA, C.MONTO AS C_MONTO, M.FECHA_CREACION, M.FECHA_MOV, M.GLOSA  FROM CASHFLOW F, CUENTAS C, CRITERIOS_CF R, MOVIMIENTOS M, USUARIO U WHERE M.ID_CASHFLOW = F.ID_CASHFLOW AND M.ID_CUENTAS = C.ID_CUENTAS AND M.ID_CRITERIOS_CF = R.ID_CRITERIOS_CF AND M.ID_USU = U.ID_USUARIO AND M.ID_CASHFLOW = C.ID_CASHFLOW AND M.ID_CASHFLOW = R.ID_CASHFLOW AND M.ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"' AND M.ID_CUENTAS = '"+str(data['ID_CUENTAS'])+"' AND M.ID_CRITERIOS_CF = '"+str(data['ID_CRITERIOS_CF'])+"' AND M.ID_MOVIMIENTOS = '"+str(data['ID_MOVIMIENTOS'])+"'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        print(line)
        lineL = list(line)
        lineL[1] = float(lineL[1])
        lineL[11] = float(lineL[11])
        line = tuple(lineL)
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    return jsonify(json_data)

########################################### CRITERIO METHODS ###########################################

@app.route("/criterio/create/", methods=['POST'])
@token_required
def criterio_create():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT IFNULL(MAX(ID_CRITERIOS_CF)+1,0) AS ID_CRITERIOS_CF FROM CRITERIOS_CF WHERE ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    cur0 = mysql.connection.cursor()
    sql0 = 'INSERT INTO CRITERIOS_CF (ID_CASHFLOW, ID_CRITERIOS_CF, ID_CRITERIOS, NOMBRE, DESCRIPCION, TIPO, ID_USUARIO, ESTADO) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
    cur0.execute(sql0, (data['ID_CASHFLOW'], json_data[0]['ID_CRITERIOS_CF'], data['ID_CRITERIOS'], data['NOMBRE'], data['DESCRIPCION'], data['TIPO'], response['id_usuario'], 1))
    mysql.connection.commit()
    cur0.close()

    cur2 = mysql.connection.cursor()
    sql2 = 'INSERT INTO PRESUPUESTO (ID_CASHFLOW, ID_CRITERIOS_CF, ID_ANIO_MES, MONTO) VALUES (%s, %s, %s, %s)'
    cur2.execute(sql2, (data['ID_CASHFLOW'], json_data[0]['ID_CRITERIOS_CF'], date.today().strftime("%Y%m"), data['MONTO']))
    mysql.connection.commit()
    cur2.close()

    return jsonify({'success': True, 'message': 'Criterio creado correctamente'})

@app.route("/criterio/readall/", methods=['POST'])
@token_required
def criterio_readall():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SET @ROWNUM := 0")
    cur.execute("SELECT @ROWNUM := @ROWNUM + 1 AS ID, C.*, P.ID_ANIO_MES, P.MONTO FROM CRITERIOS_CF C, PRESUPUESTO P WHERE C.ID_CASHFLOW = P.ID_CASHFLOW AND C.ID_CRITERIOS_CF = P.ID_CRITERIOS_CF AND C.ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"' AND P.ID_ANIO_MES = '"+ date.today().strftime("%Y%m") +"' AND ESTADO = 1")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        lineL = list(line)
        lineL[10] = float(lineL[10])
        line = tuple(lineL)
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    return jsonify(json_data)

@app.route("/criterio/add/", methods=['POST'])
@token_required
def criterio_add():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    sql0 = 'INSERT INTO PRESUPUESTO (ID_CASHFLOW, ID_CRITERIOS_CF, ID_ANIO_MES, MONTO) VALUES (%s, %s, %s, %s)'
    cur0.execute(sql0, (data['ID_CASHFLOW'], data['ID_CRITERIOS_CF'], date.today().strftime("%Y%m"), data['MONTO']))
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Presupuesto añadido correctamente'})

#delete criterio
@app.route("/criterio/delete/", methods=['POST'])
@token_required
def criterio_delete():
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    cur0.execute("UPDATE CASHFLOW SET ESTADO = 0 WHERE ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Cashflow eliminado correctamente'})

#update presupuesto
#update criterio

########################################### CASHFLOW METHODS ###########################################

@app.route("/cashflow/create/", methods=['POST'])
@token_required
def cashflow_create():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    sql0 = 'INSERT INTO CASHFLOW (F_CREACION, NOMBRE, ID_TCONSUMO, ESTADO) VALUES (%s, %s, %s, %s)'
    cur0.execute(sql0, (datetime.datetime.now(), data['NOMBRE'], data['ID_TCONSUMO'], 1))
    mysql.connection.commit()
    cur0.close()

    cur1 = mysql.connection.cursor()
    cur1.execute('SELECT MAX(ID_CASHFLOW) AS ID FROM CASHFLOW')
    row_headers=[x[0] for x in cur1.description]
    rv1 = cur1.fetchall()
    json_data1=[]
    for line in rv1:
        json_data1.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur1.close()

    cur3 = mysql.connection.cursor()
    sql3 = 'INSERT INTO USU_CFLOW (ID_USUARIO, ID_CASHFLOW, ID_TIPO_REL, PRIORIDAD) VALUES (%s, %s, %s, %s)'
    cur3.execute(sql3, (response['id_usuario'], json_data1[0]['ID'], 5, 1))
    mysql.connection.commit()
    cur3.close()

    return jsonify({'success': True, 'ID_CASHFLOW': json_data1[0]['ID']})

@app.route("/cashflow/delete/", methods=['POST'])
@token_required
def cashflow_delete():
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    cur0.execute("UPDATE CASHFLOW SET ESTADO = 0 WHERE ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Cashflow eliminado correctamente'})

@app.route("/cashflow/readall/", methods=['GET'])
@token_required
def cashflow_readall():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])

    cur = mysql.connection.cursor()
    cur.execute("SELECT C.ID_CASHFLOW, C.NOMBRE AS CNOMBRE, T.NOMBRE AS TNOMBRE, K.NOMBRES AS KNOMBRE FROM CASHFLOW C, USU_CFLOW U, TIPO_RELACION T, TIPO_CONSUMO K WHERE C.ID_CASHFLOW = U.ID_CASHFLOW AND U.ID_TIPO_REL = T.ID_TIPO_REL AND C.ID_TCONSUMO = K.ID_TCONSUMO AND U.ID_USUARIO = '"+str(response['id_usuario'])+"' AND C.ESTADO = 1")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    return jsonify(json_data)

@app.route("/cashflow/read/", methods=['POST'])
@token_required
def cashflow_read():
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT U.ID_USUARIO, NOMBRES, APELLIDOS, USERNAME, AVATAR, OCUPACION, ID_CASHFLOW, C.ID_TIPO_REL, NOMBRE FROM USU_CFLOW C, USUARIO U, TIPO_RELACION T WHERE C.ID_USUARIO = U.ID_USUARIO AND C.ID_TIPO_REL = T.ID_TIPO_REL AND ID_CASHFLOW = '"+data['ID_CASHFLOW']+"'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    return jsonify(json_data)

@app.route("/cashflow/add/", methods=['POST'])
@token_required
def cashflow_add():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT ID_USUARIO FROM USU_CFLOW WHERE ID_USUARIO = '"+str(data['ID_USUARIO'])+"' AND ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    row_headers=[x[0] for x in cur1.description]
    rv1 = cur1.fetchall()
    json_data1=[]
    for line in rv1:
        json_data1.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur1.close()

    if json_data1 != []:
        return jsonify({'success': False, 'message': 'El usuario ya está en el cashflow'})

    cur0 = mysql.connection.cursor()
    sql0 = 'INSERT INTO USU_CFLOW (ID_USUARIO, ID_CASHFLOW, ID_TIPO_REL, PRIORIDAD) VALUES (%s, %s, %s, %s)'
    cur0.execute(sql0, (data['ID_USUARIO'], data['ID_CASHFLOW'], data['ID_TIPO_REL'], 1))
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Usuario añadido correctamente'})

@app.route("/cashflow/drop/", methods=['POST'])
@token_required
def cashflow_drop():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    cur0.execute("DELETE FROM USU_CFLOW WHERE ID_USUARIO = '"+str(data['ID_USUARIO'])+"' AND ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Usuario removido correctamente'})

@app.route("/cashflow/default/", methods=['POST'])
@token_required
def cashflow_default():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    cur0.execute("UPDATE USUARIO SET CASHFLOW_DEFAUT = '"+str(data["ID_CASHFLOW"])+"' WHERE ID_USUARIO = '"+str(response['id_usuario'])+"'")
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Cashflow por default definido'})

############################################ CUENTA METHODS ############################################

@app.route("/cuenta/create/", methods=['POST'])
@token_required
def cuenta_create():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])

    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT IFNULL(MAX(ID_CUENTAS)+1,0) AS ID_CUENTAS FROM CUENTAS WHERE ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    cur0 = mysql.connection.cursor()
    sql0 = 'INSERT INTO CUENTAS (ID_CASHFLOW, ID_CUENTAS, ID_TIPO, NOMBRE, DESCRIPCION, ID_USU, MONTO, NRO_CUENTA, INT_BANCARIA, ESTADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cur0.execute(sql0, (data['ID_CASHFLOW'], json_data[0]['ID_CUENTAS'], str(data['ID_TIPO']), data['NOMBRE'], data['DESCRIPCION'], response['id_usuario'], str(data['MONTO']), data['NRO_CUENTA'], data['INT_BANCARIA'], 1))
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Cuenta creada correctamente'})

@app.route("/cuenta/delete/", methods=['POST'])
@token_required
def cuenta_delete():
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    cur0.execute("UPDATE CUENTAS SET ESTADO = 0 WHERE ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"' AND ID_CUENTAS = '"+str(data['ID_CUENTAS'])+"'")
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Cuenta eliminada correctamente'})

@app.route("/cuenta/readall/", methods=['POST'])
@token_required
def cuenta_readall():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SET @ROWNUM := 0")
    cur.execute("SELECT @ROWNUM := @ROWNUM + 1 AS ID, C.* FROM CUENTAS C WHERE ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"' AND ID_USU = '"+str(response['id_usuario'])+"' AND ESTADO = 1")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        lineL = list(line)
        lineL[7] = float(lineL[7])
        line = tuple(lineL)
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    return jsonify(json_data)

@app.route("/cuenta/add/", methods=['POST'])
@token_required
def cuenta_add():
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT MONTO FROM CUENTAS WHERE ID_CUENTAS = '"+str(data['ID_CUENTAS'])+"' AND ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    if data['TIPO'] == 1:
        monto = json_data[0]['MONTO'] + Decimal(data['MONTO'])
    if data['TIPO'] == 2:
        if Decimal(data['MONTO']) > Decimal(json_data[0]['MONTO']):
            return jsonify({'success': False, 'message': 'El monto a restar es mayor al monto actual'})
        monto = json_data[0]['MONTO'] - Decimal(data['MONTO'])

    cur0 = mysql.connection.cursor()
    cur0.execute("UPDATE CUENTAS SET MONTO = '"+str(monto)+"' WHERE ID_CUENTAS = '"+str(data['ID_CUENTAS'])+"' AND ID_CASHFLOW = '"+str(data['ID_CASHFLOW'])+"'")
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Monto actualizado'})

############################################# USER METHODS #############################################

@app.route("/user/create/", methods=['POST'])
def user_create():
    data = (request.get_json(force=True))

    cur00 = mysql.connection.cursor()
    cur00.execute("SELECT USERNAME FROM USUARIO WHERE USERNAME = '"+data['USERNAME']+"'")
    row_headers=[x[0] for x in cur00.description]
    rv00 = cur00.fetchall()
    json_data00=[]
    for line in rv00:
        json_data00.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur00.close()

    if json_data00 != []:
        return jsonify({'success': False, 'message': 'Usuario ya registrado'})

    cur11 = mysql.connection.cursor()
    cur11.execute("SELECT EMAIL FROM USUARIO WHERE EMAIL = '"+data['EMAIL']+"'")
    row_headers=[x[0] for x in cur11.description]
    rv11 = cur11.fetchall()
    json_data11=[]
    for line in rv11:
        json_data11.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur11.close()

    if json_data11 != []:
        return jsonify({'success': False, 'message': 'Correo ya registrado'})


    cur0 = mysql.connection.cursor()
    hashed_password = generate_password_hash(data['PASSWORD'], method='sha256')
    sql0 = 'INSERT INTO USUARIO (USERNAME, PASSWORD, NOMBRES, APELLIDOS, EMAIL, FECHA_CREACION, SEXO, TOKEN_SOCIAL, ID_SOCIAL, AVATAR, ESTADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cur0.execute(sql0, (data['USERNAME'], hashed_password, data['NOMBRES'], data['APELLIDOS'], data['EMAIL'], datetime.datetime.now(), data['SEXO'], data['TOKEN_SOCIAL'], data['ID_SOCIAL'], data['AVATAR'], 1))
    mysql.connection.commit()
    cur0.close()

    cur1 = mysql.connection.cursor()
    cur1.execute('SELECT LAST_INSERT_ID() AS ID')
    row_headers=[x[0] for x in cur1.description]
    rv1 = cur1.fetchall()
    json_data1=[]
    for line in rv1:
        json_data1.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur1.close()

    cur2 = mysql.connection.cursor()
    sql2 = 'INSERT INTO CASHFLOW (F_CREACION, NOMBRE, ID_TCONSUMO, ESTADO) VALUES (%s, %s, %s, %s)'
    cur2.execute(sql2, (datetime.datetime.now(), 'Flujo de caja', 1, 1))
    mysql.connection.commit()
    cur2.close()

    cur3 = mysql.connection.cursor()
    cur3.execute('SELECT LAST_INSERT_ID() AS ID')
    row_headers=[x[0] for x in cur3.description]
    rv3 = cur3.fetchall()
    json_data3=[]
    for line in rv3:
        json_data3.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur3.close()

    cur4 = mysql.connection.cursor()
    sql4 = 'INSERT INTO USU_CFLOW (ID_USUARIO, ID_CASHFLOW, ID_TIPO_REL, PRIORIDAD) VALUES (%s, %s, %s, %s)'
    cur4.execute(sql4, (json_data1[0]['ID'], json_data3[0]['ID'], 5, 1))
    mysql.connection.commit()
    cur4.close()

    cur5 = mysql.connection.cursor()
    cur5.execute('UPDATE USUARIO SET CASHFLOW_DEFAUT = %s WHERE ID_USUARIO = %s', (json_data3[0]['ID'], json_data1[0]['ID']))
    mysql.connection.commit()
    cur5.close()

    return jsonify({'success': True, 'message': 'Usuario registrado correctamente'})

@app.route("/user/update/", methods=['POST'])
@token_required
def user_update():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur0 = mysql.connection.cursor()
    cur0.execute("UPDATE USUARIO SET NOMBRES = '"+data['NOMBRES']+"', APELLIDOS = '"+data['APELLIDOS']+"', SEXO = '"+data['SEXO']+"', AVATAR = '"+data['AVATAR']+"' WHERE ID_USUARIO = '"+str(response['id_usuario'])+"'")
    mysql.connection.commit()
    cur0.close()

    return jsonify({'success': True, 'message': 'Datos de usuario actualizado'})

@app.route("/user/delete/", methods=['POST'])
@token_required
def user_delete():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT PASSWORD FROM USUARIO WHERE ID_USUARIO = '" + str(response['id_usuario']) + "'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    if check_password_hash(json_data[0]['PASSWORD'], data['PASSWORD']):
        cur0 = mysql.connection.cursor()
        cur0.execute("UPDATE USUARIO SET ESTADO = 0, TOKEN = '' WHERE ID_USUARIO = '"+str(response['id_usuario'])+"'")
        mysql.connection.commit()
        cur0.close()

        return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})

    return jsonify({'success': False, 'message': 'Contraseña incorrecta'})

@app.route("/user/password/", methods=['POST'])
@token_required
def user_password():
    response = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'])
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT PASSWORD FROM USUARIO WHERE ID_USUARIO = '" + str(response['id_usuario']) + "'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()

    if check_password_hash(json_data[0]['PASSWORD'], data['ACTUAL']):
        hashed_password = generate_password_hash(data['NUEVO'], method='sha256')
        cur0 = mysql.connection.cursor()
        cur0.execute("UPDATE USUARIO SET PASSWORD = '"+hashed_password+"' WHERE ID_USUARIO = '"+str(response['id_usuario'])+"'")
        mysql.connection.commit()
        cur0.close()
        return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})

    return jsonify({'success': False, 'message': 'Contraseña actual incorrecta'})

@app.route('/user/find/', methods=['POST'])
@token_required
def user_find():
    data = (request.get_json(force=True))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM USUARIO WHERE USERNAME LIKE '%"+data['USERNAME']+"%'")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for line in rv:
        json_data.append(dict(zip(row_headers,line)))
    mysql.connection.commit()
    cur.close()
    return jsonify(json_data)

@app.route('/user/validate/', methods=['POST'])
def user_validate():
    data = (request.get_json(force=True))
    try:
        response = jwt.decode(data['TOKEN'], app.config['SECRET_KEY'])
    except:
        return jsonify({'message' : 'Token is invalid!'}), 401
        
    try: 
        cur = mysql.connection.cursor()
        cur.execute("SELECT ID_USUARIO, USERNAME, NOMBRES, APELLIDOS, EMAIL, SEXO, TOKEN_SOCIAL, ID_SOCIAL, AVATAR, CASHFLOW_DEFAUT FROM USUARIO WHERE USERNAME = '"+response['usuario']+"' AND TOKEN = '"+data['TOKEN']+"'")
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data=[]
        for line in rv:
            json_data.append(dict(zip(row_headers,line)))
        mysql.connection.commit()
        cur.close()

        if json_data[0]['USERNAME'] == response['usuario']:
            return jsonify(json_data[0])
        else:
            return jsonify({'message' : 'Token is invalid!'}), 401
    except:
        return jsonify({'message' : 'Token is invalid!'}), 401

@app.route('/user/login/', methods=['POST'])
def user_login():
    data = (request.get_json(force=True))

    try:
        data['ID_SOCIAL']
        data['TOKEN_SOCIAL']

        cur = mysql.connection.cursor()
        cur.execute("SELECT ID_USUARIO, PASSWORD, CASHFLOW_DEFAUT, ID_SOCIAL, TOKEN_SOCIAL FROM USUARIO WHERE ID_SOCIAL = '" + data['ID_SOCIAL'] + "' AND ESTADO = 1")
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data=[]
        for line in rv:
            json_data.append(dict(zip(row_headers,line)))
        mysql.connection.commit()
        cur.close()

        try:
            json_data[0]['TOKEN_SOCIAL']
            if json_data[0]['TOKEN_SOCIAL'] != data['TOKEN_SOCIAL']:
                return jsonify({'success': False, 'TOKEN': ''})
        except:
            return jsonify({'success': False, 'TOKEN': ''})
        
    except:
        cur = mysql.connection.cursor()
        cur.execute("SELECT ID_USUARIO, PASSWORD, CASHFLOW_DEFAUT, ID_SOCIAL, TOKEN_SOCIAL FROM USUARIO WHERE USERNAME = '" + data['USUARIO'] + "' AND ESTADO = 1")
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data=[]
        for line in rv:
            json_data.append(dict(zip(row_headers,line)))
        mysql.connection.commit()
        cur.close()

    try:
        json_data[0]['PASSWORD']
    except:
        return jsonify({'success': False, 'TOKEN': ''})

    if check_password_hash(json_data[0]['PASSWORD'], data['CLAVE']):
        token = jwt.encode({'usuario' : data['USUARIO'], 'id_usuario': json_data[0]['ID_USUARIO'], 'cashflow_default': json_data[0]['CASHFLOW_DEFAUT'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])

        cur0 = mysql.connection.cursor()
        cur0.execute("UPDATE USUARIO SET TOKEN = '" + token + "' WHERE USERNAME = '" + data['USUARIO'] + "'")
        mysql.connection.commit()
        cur0.close()

        cur1 = mysql.connection.cursor()
        cur1.execute("UPDATE USUARIO SET TOKEN_FCM = '" + str(data['TOKEN_FCM']) + "' WHERE USERNAME = '" + data['USUARIO'] + "'")
        mysql.connection.commit()
        cur1.close()

        return jsonify({'success': True, 'TOKEN': token})
    return jsonify({'success': False, 'TOKEN': ''})

########################################################################################################

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 
