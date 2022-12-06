import MySQLdb.cursors
from app import app
from app import mysql
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import LoginForm

def format(str):
    str = str.replace("(","")
    str = str.replace(")","")
    str = str.replace(",","")
    return str

@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/login', methods = ['GET', 'POST'])
def login():

    msg = ""

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employee WHERE em_login = %s AND em_password = %s', (username, password,))

        account = cursor.fetchone()

        if account:

            session['loggedin'] = True
            session['id'] = account['em_id']
            session['username'] = account['em_name']

            return redirect(url_for('home'))

        else:
            msg = 'Неправильный логин/пароль'


    return render_template('login.html', msg=msg)


@app.route('/users')
def users():
    cur = mysql.connection.cursor()

    users = cur.execute("SELECT * FROM employee")

    if users > 0:
        userDetails = cur.fetchall()

        return render_template('users.html', title='Users', userDetails=userDetails)

    cur.close()


@app.route('/home')
def home():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()

        object = cur.execute(
                                '''
                                SELECT
                                object_of_real_estate.re_id, 
                                object_of_real_estate.re_address,
                                object_of_real_estate.re_amount_rooms,
                                object_of_real_estate.re_loor,
                                layout.lay_name,
                                object_categories.cat_name,
                                material.m_name,
                                district.d_name,
                                client.cl_name,
                                client.cl_surname,
                                client.cl_patronymic,
                                client.cl_ph_number,
                                client.cl_date_of_birth,
                                client.cl_pasport_number,
                                client.cl_pasport_series,
                                client.cl_pasport_date_of_issue,
                                client.cl_papsort_issued_by,
                                client.cl_pasport_registration,
                                deal.d_date,
                                type_of_deal.tod_name
                                FROM object_of_real_estate, layout, object_categories, material, district, client, deal, type_of_deal
                                WHERE object_of_real_estate.cl_id = client.cl_id and 
                                object_of_real_estate.lay_id = layout.lay_id and
                                object_of_real_estate.cat_id = object_categories.cat_id and
                                object_of_real_estate.m_id = material.m_id and 
                                object_of_real_estate.d_id = district.d_id and
                                object_of_real_estate.re_id = deal.re_id and
                                deal.tod_id = type_of_deal.tod_id and
                                object_of_real_estate.em_id = %s;
                                ''',
                                [session['id']]
                            )

        if object > 0:
            objectDetails = cur.fetchall()

            objects = []

            for tuple in objectDetails:
                objects.append([])

            for i in range(len(objectDetails)):
                for elem in objectDetails[i]:
                    objects[i].append(elem)

            for elem in objects:
                elem[12] = str(elem[12])[0:10]
                elem[15] = str(elem[15])[0:10]
                elem[18] = str(elem[18])[0:10]

            return render_template('home.html', title='Главная', username=session['username'], objectDetails=objects)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)

    return redirect(url_for('login'))


@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if 'loggedin' in session:
        if (request.method == 'POST' and
            'cl_name' in request.form and
            'cl_surname' in request.form and
            'cl_patronymic' in request.form and
            'cl_pasport_number' in request.form and
            'cl_date_of_birth' in request.form and
            'cl_papsort_issued_by' in request.form and
            'cl_pasport_registration' in request.form and
            'cl_pasport_date_of_issue' in request.form and
            'cl_ph_number' in request.form and
            'cl_pasport_series' in request.form
        ):

            cl_name = request.form['cl_name']
            cl_surname = request.form['cl_surname']
            cl_patronymic = request.form['cl_patronymic']
            cl_pasport_number = request.form['cl_pasport_number']
            cl_date_of_birth = request.form['cl_date_of_birth']
            cl_papsort_issued_by = request.form['cl_papsort_issued_by']
            cl_pasport_registration = request.form['cl_pasport_registration']
            cl_pasport_date_of_issue = request.form['cl_pasport_date_of_issue']
            cl_ph_number = request.form['cl_ph_number']
            cl_pasport_series = request.form['cl_pasport_series']

            cur = mysql.connection.cursor()

            cur.execute('SELECT MAX(cl_id) AS maximum FROM client')

            max_id = cur.fetchone()

            object = cur.execute("INSERT INTO client values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                 (
                                     max_id[0]+1,
                                    [cl_name],
                                    [cl_surname],
                                    [cl_patronymic],
                                    [cl_pasport_number],
                                    [cl_date_of_birth],
                                    [cl_papsort_issued_by],
                                    [cl_pasport_registration],
                                    [cl_pasport_date_of_issue],
                                    [cl_ph_number],
                                    [cl_pasport_series])
                                 )

            mysql.connection.commit()

            return redirect(url_for('add_client'))

        return render_template('add_client.html', title='Добавить клиента')

    return redirect(url_for('login'))


@app.route('/add_object_of_real_estate', methods=['GET', 'POST'])
def add_building():
    if 'loggedin' in session:

        if request.method == 'GET':

            cur = mysql.connection.cursor()

            cur.execute('SELECT cl_id, cl_surname, cl_name, cl_patronymic, cl_ph_number FROM client')

            clients = cur.fetchall()

            cur.execute('SELECT * FROM material')

            materials = cur.fetchall()

            cur.execute('SELECT * FROM layout')

            layouts = cur.fetchall()

            cur.execute('SELECT * FROM district')

            districts = cur.fetchall()

            cur.execute('SELECT * FROM object_categories')

            categories = cur.fetchall()

            return render_template('add_object_of_real_estate.html',
                                   title='Добавить объект недвижимости',
                                   clients=clients,
                                   materials=materials,
                                   layouts=layouts,
                                   districts=districts,
                                   categories=categories
                                   )

        if (request.method == 'POST' and
            're_address' in request.form and
            'clients' in request.form and
            'districts' in request.form and
            'layouts' in request.form and
            're_amount_rooms' in request.form and
            're_floor' in request.form and
            'categories' in request.form and
            'materials' in request.form
        ):
            print(format(request.form['clients']))
            re_address = request.form['re_address']
            clients_id = format(request.form['clients']).split(" ")
            districts_id = format(request.form['districts']).split(" ")
            lay_id = format(request.form['layouts']).split(" ")
            re_amount_rooms = request.form['re_amount_rooms']
            re_floor = request.form['re_floor']
            cat_id = format(request.form['categories']).split(" ")
            material_id = format(request.form['materials']).split(" ")

            cur = mysql.connection.cursor()

            cur.execute('SELECT MAX(re_id) AS maximum FROM object_of_real_estate')

            max_id = cur.fetchone()

            cur.execute("INSERT INTO object_of_real_estate values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            max_id[0]+1,
                            [re_address],
                            [re_amount_rooms],
                            [re_floor],
                            [lay_id[0]],
                            [cat_id[0]],
                            [material_id[0]],
                            [session['id']],
                            [clients_id[0]],
                            [districts_id[0]])
                        )

            mysql.connection.commit()

            return redirect(url_for('add_building'))

    return redirect(url_for('login'))


@app.route('/add_deal', methods=['GET', 'POST'])
def add_deal():
    if 'loggedin' in session:

        if request.method == 'GET':

            cur = mysql.connection.cursor()

            cur.execute(
                        '''
                        SELECT 
                        object_of_real_estate.re_id, 
                        object_of_real_estate.re_address, 
                        client.cl_id, 
                        client.cl_name, 
                        client.cl_surname, 
                        client.cl_patronymic, 
                        client.cl_ph_number 
                        FROM object_of_real_estate, client 
                        WHERE object_of_real_estate.cl_id = client.cl_id and object_of_real_estate.em_id = %s;
                        ''',
                            [session['id']]
                        )

            object_of_real_estate = cur.fetchall()

            cur.execute('SELECT * FROM type_of_deal')

            type_of_deal = cur.fetchall()

            return render_template('add_deal.html',
                                   title='Добавить сделку',
                                   object_of_real_estate=object_of_real_estate,
                                   type_of_deal=type_of_deal
                                   )

        if (
                request.method == 'POST' and
                'object_of_real_estate' in request.form and
                'type_of_deal' in request.form and
                'd_date' in request.form
        ):
            object_of_real_estate = format(request.form['object_of_real_estate']).split(" ")
            type_of_deal = format(request.form['type_of_deal']).split(" ")
            d_date = request.form['d_date']

            cur = mysql.connection.cursor()

            cur.execute(
                '''
                INSERT INTO
                deal
                VALUES(
                %s, %s, %s
                )
                ''',
                (
                    [object_of_real_estate[0]],
                    [type_of_deal[0]],
                    [d_date]
                )
            )

            mysql.connection.commit()

            return redirect(url_for('add_deal'))

    return redirect(url_for('login'))


@app.route('/remove_client', methods=['GET', 'POST'])
def remove_client():
    if 'loggedin' in session:

        if request.method == 'GET':

            cur = mysql.connection.cursor()

            cur.execute('SELECT cl_id, cl_surname, cl_name, cl_patronymic, cl_ph_number FROM client')

            clients = cur.fetchall()

            return render_template('remove_client.html',
                                   title='Удалить клиента',
                                   clients=clients)

        if (
            request.method == 'POST' and
            'clients' in request.form
        ):
            clients_id = format(request.form['clients']).split(" ")

            cur = mysql.connection.cursor()

            cur.execute('DELETE FROM client WHERE cl_id = %s', [clients_id[0]])

            mysql.connection.commit()

            return redirect(url_for('remove_client'))

    return redirect(url_for('login'))


@app.route('/remove_building', methods=['GET', 'POST'])
def remove_building():
    if 'loggedin' in session:
        if request.method == 'GET':

            cur = mysql.connection.cursor()

            cur.execute('SELECT re_id, re_address FROM object_of_real_estate WHERE em_id=%s', [session['id']])

            buildings = cur.fetchall()

            return render_template(
                                    'remove_buildings.html',
                                    title='Удалить объект',
                                    buildings=buildings
                                    )

        if (
            request.method == 'POST' and
            'buildings' in request.form
        ):
            build_id = format(request.form['buildings']).split(" ")

            cur = mysql.connection.cursor()

            cur.execute('DELETE FROM object_of_real_estate WHERE re_id=%s', [build_id[0]])

            mysql.connection.commit()

            return redirect(url_for('remove_building'))

    return redirect(url_for('login'))


@app.route('/remove_deal', methods=['GET', 'POST'])
def remove_deal():

    if 'loggedin' in session:

        if request.method == 'GET':

            cur = mysql.connection.cursor()

            cur.execute('''
                        SELECT 
                        deal.re_id, 
                        deal.tod_id,
                        deal.d_date,
                        type_of_deal.tod_name,
                        object_of_real_estate.re_address,
                        client.cl_name,
                        client.cl_surname,
                        client.cl_patronymic,
                        client.cl_ph_number
                        FROM deal, type_of_deal, object_of_real_estate, client
                        WHERE
                        deal.re_id = object_of_real_estate.re_id and
                        deal.tod_id = type_of_deal.tod_id and
                        object_of_real_estate.cl_id = client.cl_id;
                        '''
                        )

            deals = cur.fetchall()

            return render_template(
                'remove_deal.html',
                title='Удалить сделку',
                deals=deals
            )

        if request.method == 'POST' and 'deals' in request.form:

            deal_id = format(request.form['deals']).split(" ")

            cur = mysql.connection.cursor()

            cur.execute('''
                        DELETE
                        FROM deal
                        WHERE re_id=%s, tod_id=%s
                        ''',
                        ([deal_id[0], deal_id[1]])
                        )
            mysql.connection.commit()

            return redirect(url_for('remove_deal'))

        return redirect(url_for('login'))


@app.route('/add_contract', methods=['GET', 'POST'])
def add_contract():

    if 'loggedin' in session:

        if request.method == 'GET':

            cur = mysql.connection.cursor()

            cur.execute('SELECT cl_id, cl_surname, cl_name, cl_patronymic, cl_ph_number FROM client')

            clients = cur.fetchall()

            return render_template(
                                    'add_contract.html',
                                    title='Добавить договор',
                                    clients=clients
                                )

        if (
            request.method == 'POST' and
            'clients' in request.form and
            'c_date_of_start' in request.form and
            'c_date_of_end' in request.form
        ):
            clients = format(request.form['clients']).split(" ")
            c_date_of_start = request.form['c_date_of_start']
            c_date_of_end = request.form['c_date_of_end']

            cur = mysql.connection.cursor()

            cur.execute('INSERT INTO contract values (%s, %s, %s, %s)',
                        (
                            [clients[0]],
                            [session['id']],
                            [c_date_of_start],
                            [c_date_of_end]
                        )
                        )

            mysql.connection.commit()

            return redirect(url_for('add_contract'))

        return redirect(url_for('login'))


@app.route('/remove_contract', methods=['GET', 'POST'])
def remove_contract():
    if 'loggedin' in session:

        if request.method == 'GET':

            cur = mysql.connection.cursor()

            cur.execute(
                '''
                SELECT
                contract.cl_id,
                contract.re_id,
                object_of_real_estate.re_address,
                client.cl_name,
                client.cl_surname,
                client.cl_patronymic,
                client.cl_ph_number
                FROM
                contract,
                object_of_real_estate,
                client,
                employee
                WHERE
                contract.cl_id = client.cl_id and
                contract.re_id = object_of_real_estate.re_id and
                employee.em_id = object_of_real_estate.em_id
                '''
            )

            contarcts = cur.fetchall()

            return render_template(
                'remove_contract.html',
                title='Удалить договор',
                contarcts=contarcts
            )

        if (
                request.method == 'POST' and
                'contarcts' in request.form
        ):
            contracts = format(request.form['contracts']).split(" ")

            cur = mysql.connection.cursor()

            cur.execute(
                '''
                DELETE 
                FROM contract
                WHERE 
                cl_id=%s,
                re_id=%s
                ''',
                (
                    [
                        contracts[0],
                        contracts[1]
                     ]
                )
            )

            mysql.connection.commit()

            return redirect(url_for('remove_contract'))

        return redirect(url_for('login'))


@app.route('/clients')
def clients():

    cur = mysql.connection.cursor()

    cur.execute('''
        SELECT
        cl_id,
        cl_name,
        cl_surname,
        cl_patronymic,
        cl_ph_number,
        cl_date_of_birth,
        cl_pasport_number,
        cl_pasport_series,
        cl_papsort_issued_by,
        cl_pasport_date_of_issue,
        cl_pasport_registration
        FROM client;
    '''
    )

    clients = cur.fetchall()

    clientsDetails = []

    for tuple in clients:
        clientsDetails.append([])

    for i in range(len(clients)):
        for elem in clients[i]:
            clientsDetails[i].append(elem)

    for elem in clientsDetails:
        elem[5] = str(elem[5])[0:10]
        elem[9] = str(elem[9])[0:10]

    return render_template('clients.html', title='Клиенты', clients=clientsDetails)

