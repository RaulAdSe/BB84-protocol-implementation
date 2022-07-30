import random
from prettytable import PrettyTable
'''
Aquest codi simula una comunicació entre Alice i Bob utilitzant el protocol BB84 però a través d'un satel·lit. Primer
de tot converteix el missatge a enviar a binari i després crea dues claus, una per Alice - Satel·lit i l'altra per 
Satel·lit - Bob que serviran per enviar el missatge encriptat des d'Alice fins a Bob. També ens deixa triar si hi ha Eve
en cada una de la creació de les claus i a més a més ens deixa triar quin percentatge de fotons volem que Eve mesuri i 
quina tolerància en l'error estem disposats a acceptar.
'''

def missatge_a_ascii(missatge):
    v = []
    for i in missatge:
        v.append(ord(i))
    return v


def ascii_a_binari(v):
    binary = []
    for i in v:
        aux = []
        while i > 0:
            aux.insert(0, i % 2)
            i = i // 2
        binary.extend(aux)
    return binary


def binari_a_ascii(v):
    vec_ascii = []
    for x in range(len(v) // 7):
        sumatori = 0
        for i in range(6, -1, -1):
            k = x * (7 - i - 1)
            sumatori = sumatori + v[k] * pow(2, i)
        vec_ascii.append(sumatori)


def binari_a_ascii(v):
    vec_ascii = []
    for x in range(len(v) // 7):
        sumatori = 0
        for i in range(6, -1, -1):
            k = 7 * x + (7 - i) - 1
            sumatori = sumatori + v[k] * pow(2, i)
        vec_ascii.append(sumatori)
    return vec_ascii


def ascii_a_missatge(v):
    missatge_caracters = ""
    for x in v:
        missatge_caracters = missatge_caracters + chr(x)
    return missatge_caracters


def xor_missatge_clau(missatge, clau):
    crypto = []
    i = 0
    for x in missatge:
        crypto.append(xor(x, clau[i]))
        i += 1
    return crypto


def machine_error():
    choice_error = random.choice(range(100))
    if choice_error == 19 or choice_error == 34 or choice_error == 35:  # 3% error maquina
        machine_error = True
    else:
        machine_error = False
    return machine_error


def xor(qbit1, qbit2):
    suma = int(qbit1) + int(qbit2)
    if suma == 2:
        suma = 0
    return suma


st_qbit = {
    'vertical': '0',
    'horizontal': '1',
    '+45': '1',
    '-45': '0'
}

missatge = input('Message to be sent (only letters, spaces must be replaced with ~): ')
missatge_ascii = missatge_a_ascii(missatge)
missatge_binary = ascii_a_binari(missatge_ascii)

ans = input("Is there an Eve? Answer 'y'(yes) or 'n'(no): ")
if ans.lower() == 'y':
    eve = True
    tolerancia = input("Tolerance in comunication abortion (in %) [consider machine error = 3%] : ")
    tolerancia = int(tolerancia)
else:
    eve = False
    tolerancia = 8

N = len(missatge_binary) * 8
alice_raw_key = []
alice_random_base = []  # ho faig separat per denotar que cadascu ho fa de manera separada.
for i in range(N):
    a_rand_base = random.choice(['vert&hor', 'diagonal'])
    alice_random_base.append(a_rand_base)

    if a_rand_base == 'vert&hor':
        state = random.choice(['vertical', 'horizontal'])
        qbit = st_qbit[state]
    else:
        state = random.choice(['+45', '-45'])
        qbit = st_qbit[state]

    alice_raw_key.append(qbit)

satellite_random_base = []
for i in range(N):
    s_rand_base = random.choice(['vert&hor', 'diagonal'])
    satellite_random_base.append(s_rand_base)

# MEASURE OF THE QBITS SENT BY ALICE:
if eve:
    eve_measure_pos = ['-'] * N
    eve_random_base = ['-'] * N
    eve_percent = input('Fraction of qbits that Eve measures (in %): ')
    quants = int(N * int(eve_percent) / 100)
    steps = N // quants
    for n in range(0, len(alice_raw_key), steps):
        eve_measure_pos[n] = n
        eve_base = random.choice(['vert&hor', 'diagonal'])
        eve_random_base[n] = eve_base

    # EXTRA PER COMPROVAR ERRORS AL CODI:
    coinc_eve_alice = 0
    coinc_eve_satellite = 0
    coinc_alice_satellite = 0
    for n in range(len(eve_random_base)):
        if eve_random_base[n] == alice_random_base[n]:
            coinc_eve_alice += 1
        if eve_random_base[n] == satellite_random_base[n]:
            coinc_eve_satellite += 1
        if alice_random_base[n] == satellite_random_base[n]:
            coinc_alice_satellite += 1

    eve_raw_key = ['-'] * N
    for k in range(N):
        if eve_random_base[k] != '-':
            error = machine_error()  # aplico també error maquina del 3%
            if alice_random_base[k] == eve_random_base[k]:
                if not error:
                    eve_raw_key[k] = alice_raw_key[k]
                else:
                    if alice_raw_key[k] == '1':
                        eve_raw_key[k] = '0'
                    else:
                        eve_raw_key[k] = '1'

            else:
                if eve_random_base[k] == 'vert&hor':
                    state = random.choice(['vertical', 'horizontal'])
                else:
                    state = random.choice(['+45', '-45'])

                if error:
                    eve_raw_key[k] = xor(st_qbit[state], '1')
                else:
                    eve_raw_key[k] = st_qbit[state]

    encerts = 0
    for n in range(len(eve_raw_key)):
        if eve_raw_key[n] == alice_raw_key[n]:
            encerts += 1
    print('Percentatge de la clau correcta (eve - alice): ' + str(int(encerts) / N * 100) + '%.')  # 75% - err%
    print('')

    satellite_raw_key = ['-'] * N  # it gets different than it would be with no eve. AQUI ESTA EL ERROR!
    for i in range(N):
        error = machine_error()  # aplico error maquina del 3%
        if i == eve_measure_pos[i] and satellite_random_base[i] == eve_random_base[i]:  # eve mesura i determina resultat
            if not error:
                satellite_raw_key[i] = eve_raw_key[i]
            else:
                if eve_raw_key[i] == '0':
                    satellite_raw_key[i] = '1'
                else:
                    satellite_raw_key[i] = '0'

        elif i == eve_measure_pos[i] and satellite_random_base[i] != eve_random_base[i]:  # eve mesura i no determina
            if satellite_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                satellite_raw_key[i] = xor(st_qbit[state], '1')
            else:
                satellite_raw_key[i] = st_qbit[state]

        elif i != eve_measure_pos[i] and satellite_random_base[i] == alice_random_base[
            i]:  # aqui quan eve no mesura, lo de sempre
            if not error:
                satellite_raw_key[i] = alice_raw_key[i]
            else:
                if alice_raw_key[i] == '0':
                    satellite_raw_key[i] = '1'
                else:
                    satellite_raw_key[i] = '0'

        elif i != eve_measure_pos[i] and satellite_random_base[i] != alice_random_base[i]:
            if satellite_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                satellite_raw_key[i] = xor(st_qbit[state], '1')
            else:
                satellite_raw_key[i] = st_qbit[state]

else:
    satellite_raw_key = []
    for i in range(N):
        error = machine_error()  # aplico error maquina del 3%
        if alice_random_base[i] == satellite_random_base[i]:
            if not error:
                satellite_raw_key.append(alice_raw_key[i])
            else:
                if alice_raw_key[i] == '1':
                    satellite_raw_key.append('0')
                else:
                    satellite_raw_key.append('1')

        else:
            if satellite_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                satellite_raw_key.append(xor(st_qbit[state], '1'))
            else:
                satellite_raw_key.append(st_qbit[state])

x = PrettyTable()
if eve:
    x.field_names = ["QBit Number", "Alice Random Base", "Alice Raw Key", "Satellite Raw Key", "Satellite Random Base",
                     "Eve Raw Key", "Eve Random Base"]
else:
    x.field_names = ["QBit Number", "Alice Random Base", "Alice Raw Key", "Satellite Raw Key", "Satellite Random Base"]
for i in range(len(alice_random_base)):
    if eve:
        x.add_row([i + 1, alice_random_base[i], alice_raw_key[i], satellite_raw_key[i], satellite_random_base[i], eve_raw_key[i],
                   eve_random_base[i]])
    else:
        x.add_row([i + 1, alice_random_base[i], alice_raw_key[i], satellite_raw_key[i], satellite_random_base[i]])
print(x)

input('Seguir: ')

# They discard results where they chose a different base:
if eve:
    print(len(eve_raw_key))
if eve:
    no_coincideixen_eve = []  # when Alice and Satellite match but Eve doesn't: the result won't be discarded. ('-')
    no_coincideixen_alice_satellite = []  # When Alice and Satellite don't match: the result will be discarded. (removed)
    for n in range(N):
        if alice_random_base[n] != satellite_random_base[n]:
            no_coincideixen_alice_satellite.append(n)
        elif alice_random_base[n] == satellite_random_base[n] and alice_random_base[n] != eve_random_base[n]:
            no_coincideixen_eve.append(n)

    no_coincideixen_alice_satellite = sorted(no_coincideixen_alice_satellite)
    no_coincideixen_eve = sorted(no_coincideixen_eve)
    for k in reversed(no_coincideixen_eve):
        eve_raw_key[k] = '-'
    for j in reversed(no_coincideixen_alice_satellite):
        eve_raw_key.pop(j)
    print(len(eve_raw_key))
    eve_sifted_key = eve_raw_key

if eve:
    x.field_names = ["Qbit Number", "Alice Base", "Alice Sifted Key", "Satellite Sifted Key", "Satellite base", "Eve Sifted Key",
                     "Eve Random Base"]
else:
    x.field_names = ["Qbit Number", "Alice Base", "Alice Sifted Key", "Satellite Sifted Key", "Satellite base"]
cont = 0
for i in range(N - 1, -1, -1):
    if alice_random_base[i] != satellite_random_base[i]:
        alice_random_base[i] = '---'
        alice_raw_key[i] = '---'
        satellite_raw_key[i] = '---'
        satellite_random_base[i] = '---'
        x.del_row(i)
        cont += 1
print(x)
print(cont)
input('Seguir: ')

# All lists have --- in the same positions, so:
ns = []
for n in range(len(alice_raw_key)):
    if alice_raw_key[n] == '---':
        ns.append(n)

for pos in reversed(ns):
    alice_random_base.pop(pos)
    alice_raw_key.pop(pos)
    satellite_random_base.pop(pos)
    satellite_raw_key.pop(pos)

alice_sifted_key = alice_raw_key
satellite_sifted_key = satellite_raw_key
print('')
if eve:
    print('Comprovacio error de mida: ' + str(len(alice_sifted_key)) + ' =? ' + str(len(eve_sifted_key)))
    print('')
    encert = 0
    for n in range(len(eve_sifted_key)):
        if eve_sifted_key[n] == alice_sifted_key[n]:
            encert += 1
    print('Informació Eve abans de correccio: ' + str(encert / len(alice_sifted_key) * 100) + '%')

print('The length of the raw key was reduced by aprox. ' + str(int((N - len(alice_sifted_key)) / N * 100)) + '%')

# Ara fem públic el 25% de la sifted key per comprovar si hi ha Eve.
input('Seguir: ')
quants_publico = len(alice_sifted_key) // 4
pos_public = []
qbit_public_alice = []
qbit_public_satellite = []
llista_per_no_repetir = list(range(len(alice_sifted_key)))
while len(pos_public) < quants_publico:
    pos = random.choice(llista_per_no_repetir)
    llista_per_no_repetir.remove(pos)

    pos_public.append(pos)
    qbit_public_alice.append((alice_sifted_key[pos]))

print('Alice publica un percentatge de posicions i Qbits, després Satellite publica'
      'els Qbits de les mateixes posicions per a veure si la communicació és segura:')

for pos in pos_public:
    qbit_public_satellite.append((satellite_sifted_key[pos]))

x = PrettyTable()
x.field_names = ["Positions", "Alice Qbits", "Satellite Qbits"]
for i in range(len(pos_public)):
    x.add_row([pos_public[i], qbit_public_alice[i], qbit_public_satellite[i]])
print(x)
# Ara es comparen els resultats per determinar si la comunicació és segura:
num_err = 0
for n in range(len(qbit_public_alice)):
    if qbit_public_alice[n] != qbit_public_satellite[n]:
        num_err += 1

percent_num_err = int(num_err / quants_publico * 100)
if percent_num_err <= tolerancia:
    print('The communication is safe. Match error of ' + str(percent_num_err) + '%.')
else:
    print('The communication is NOT safe. Match error of ' + str(percent_num_err) + '%.')
    import sys

    sys.exit('COMMUNICATION ABORTED.')

for poses in reversed(sorted(pos_public)):
    alice_sifted_key.pop(poses)
    satellite_sifted_key.pop(poses)

# Eve (si ha passat desapercebuda) també haurà d'eliminar els qbits públics tal com han fet Alice i Satellite.
if eve:
    for poses in reversed(sorted(pos_public)):
        eve_sifted_key.pop(poses)

# ERROR CORRECTION in the resulting key:
indicadors = list(range(len(alice_sifted_key)))
alice_xors = []
llista_xors = []
for i in range(len(alice_sifted_key) // 2):
    num1 = 0;
    num2 = 0
    while num1 == num2:
        num1 = random.choice(indicadors)
        num2 = random.choice(indicadors)
    numeros = [num1, num2]
    llista_xors.append(numeros)
    for n in numeros:
        indicadors.remove(n)

# Ara es fan públics els valors de XOR i les posicions dels bits amb què s'han obtingut.

alice_xors = []
for pair in llista_xors:
    res = xor(alice_sifted_key[pair[0]], alice_sifted_key[pair[1]])
    alice_xors.append(res)

satellite_xors = []
for pair in llista_xors:
    res = xor(satellite_sifted_key[pair[0]], satellite_sifted_key[pair[1]])
    satellite_xors.append(res)

# Eve ha d'efectuar la mateixa operació amb els qbits que tingui disponibles:
if eve:
    eve_xors = []
    for pair in llista_xors:
        if eve_sifted_key[pair[0]] != '-' and eve_sifted_key[pair[1]] != '-':  # Si disposa dels qbits.
            res = xor(eve_sifted_key[pair[0]], eve_sifted_key[pair[1]])
            eve_xors.append(res)
        else:
            eve_xors.append('-')

x = PrettyTable()
if eve:
    x.field_names = ["Pairs", "Alice XOR", "Satellite XOR", "Eve XOR"]
else:
    x.field_names = ["Pairs", "Alice XOR", "Satellite XOR"]
for i in range(len(llista_xors)):
    if eve:
        x.add_row([llista_xors[i], alice_xors[i], satellite_xors[i], eve_xors[i]])
    else:
        x.add_row([llista_xors[i], alice_xors[i], satellite_xors[i]])
print(x)

'''
Es fan públics els resultats i es descarten els bits que provoquen XORs discordants.
Eve efectua en paral·lel la mateixa operació, perque els XORs son publics i les posicions dels qbits
amb què s'han calculat també.
'''

elim = []
elim_eve = []
for n in range(len(llista_xors)):
    if alice_xors[n] != satellite_xors[n]:
        elim.append(llista_xors[n][0])
        elim.append(llista_xors[n][1])
        if eve:
            elim_eve.append(llista_xors[n][0])
            elim_eve.append(llista_xors[n][1])

# Alice and Satellite, privately:
elim = list(reversed(sorted(elim)))
for j in elim:
    alice_sifted_key.pop(int(j))
    satellite_sifted_key.pop(int(j))

# Eve, in parallel:
if eve:
    elim_eve = list(reversed(sorted(elim_eve)))
    for j in elim_eve:
        eve_sifted_key.pop(int(j))

alice_corrected_key = alice_sifted_key
satellite_corrected_key = satellite_sifted_key
if eve:
    eve_corrected_key = eve_sifted_key

# Comprovem nosaltres l'èxit de la correcció d'errors i la repercussió en la informació que posseeix Eve:
num_err_alice_satellite = 0
num_err_eve = 0
for n in range(len(satellite_corrected_key)):
    if alice_corrected_key[n] != satellite_corrected_key[n]:
        num_err_alice_satellite += 1

percent_num_err_alice_satellite = num_err_alice_satellite / len(alice_corrected_key) * 100

if eve:
    for n in range(len(alice_corrected_key)):
        if alice_corrected_key[n] != eve_corrected_key[n]:
            num_err_eve += 1

    percent_num_err_eve = num_err_eve / len(alice_corrected_key) * 100

x = PrettyTable()
if eve:
    x.field_names = ["Alice Corrected", "Satellite Corrected", "Eve Corrected"]
else:
    x.field_names = ["Alice Corrected", "Satellite Corrected"]
for i in range(len(alice_corrected_key)):
    if eve:
        x.add_row([alice_corrected_key[i], satellite_corrected_key[i], eve_corrected_key[i]])
    else:
        x.add_row([alice_corrected_key[i], satellite_corrected_key[i]])
print(x)

print('')
print('Mistakes after correction: ' + str(num_err_alice_satellite) + ' That is ' + str(percent_num_err_alice_satellite) + '%')
if eve:
    print("Eve's information of the key: " + str(100 - percent_num_err_eve) + '%')

# EVE'S INFORMATION REDUCTION:
indicadors = list(range(len(alice_corrected_key)))
alice_xors = []
llista_xors = []
for i in range(len(alice_corrected_key) // 2):
    num1 = 0;
    num2 = 0
    while num1 == num2:
        num1 = random.choice(indicadors)
        num2 = random.choice(indicadors)
    numeros = [num1, num2]
    llista_xors.append(numeros)
    for n in numeros:
        indicadors.remove(n)

# Ara es fa pública NOMÉS LA LLISTA DE POSICIONS.

# Cadascú per la seva banda efectúa les operacions:
alice_xors = []
for pair in llista_xors:
    res = xor(alice_corrected_key[pair[0]], alice_corrected_key[pair[1]])
    alice_xors.append(res)

satellite_xors = []
for pair in llista_xors:
    res = xor(satellite_corrected_key[pair[0]], satellite_corrected_key[pair[1]])
    satellite_xors.append(res)

# Eve ha d'efectuar la mateixa operació amb els qbits que tingui disponibles:
if eve:
    eve_xors = []
    for pair in llista_xors:
        if eve_sifted_key[pair[0]] != '-' and eve_sifted_key[pair[1]] != '-':  # Si disposa dels qbits.
            res = xor(eve_corrected_key[pair[0]], eve_corrected_key[pair[1]])
            eve_xors.append(res)
        else:
            eve_xors.append('-')
alice_final_key = alice_xors
satellite_final_key1 = satellite_xors
# El resultat del producte es la clau definitiva:

if eve:
    eve_final_key = eve_xors
    print('Eve final key: ' + str(len(eve_final_key)) + ' ' + str(eve_final_key))
x = PrettyTable()
if eve:
    x.field_names = ["Pairs", "Alice Final Key", "Satellite Final Key", "Eve Final Key"]
else:
    x.field_names = ["Pairs", "Alice Final Key", "Satellite Final Key"]
for i in range(len(alice_final_key)):
    if eve:
        x.add_row([llista_xors[i], alice_final_key[i], satellite_final_key1[i], eve_final_key[i]])
    else:
        x.add_row([llista_xors[i], alice_final_key[i], satellite_final_key1[i]])
print(x)

# Comprovem que l'operació ha servit per reduir la informació de Eve:
if eve:
    correcte = 0
    for n in range(len(eve_final_key)):
        if eve_final_key[n] == alice_final_key[n]:
            correcte += 1
    print('')
    print('Eve possesses the ' + str(correcte / len(alice_final_key) * 100) + '% of the key.')

# Comprovem que l'error és mínim entre les claus finals de  l'Alice i el Satellite:
error_final = 0
for n in range(len(alice_final_key)):
    if alice_final_key[n] != satellite_final_key1[n]:
        error_final += 1

fin_perc = error_final / len(alice_final_key) * 100
print('')
print('The final keys differ in ' + str(error_final) + ' positions. That is: ' + str(fin_perc) + '% error.')






ans = input("Is there an Eve? Answer 'y'(yes) or 'n'(no): ")
if ans.lower() == 'y':
    eve = True
    tolerancia = input("Tolerance in comunication abortion (in %) [consider machine error = 3%] : ")
    tolerancia = int(tolerancia)
else:
    eve = False
    tolerancia = 8

# N = len(missatge_binary) * 8
bob_raw_key = []
bob_random_base = []  # ho faig separat per denotar que cadascu ho fa de manera separada.
for i in range(N):
    a_rand_base = random.choice(['vert&hor', 'diagonal'])
    bob_random_base.append(a_rand_base)

    if a_rand_base == 'vert&hor':
        state = random.choice(['vertical', 'horizontal'])
        qbit = st_qbit[state]
    else:
        state = random.choice(['+45', '-45'])
        qbit = st_qbit[state]

    bob_raw_key.append(qbit)

satellite_random_base = []
for i in range(N):
    s_rand_base = random.choice(['vert&hor', 'diagonal'])
    satellite_random_base.append(s_rand_base)

# MEASURE OF THE QBITS SENT BY BOB:
if eve:
    eve_measure_pos = ['-'] * N
    eve_random_base = ['-'] * N
    eve_percent = input('Fraction of qbits that Eve measures (in %): ')
    quants = int(N * int(eve_percent) / 100)
    steps = N // quants
    for n in range(0, len(bob_raw_key), steps):
        eve_measure_pos[n] = n
        eve_base = random.choice(['vert&hor', 'diagonal'])
        eve_random_base[n] = eve_base

    # EXTRA PER COMPROVAR ERRORS AL CODI:
    coinc_eve_bob = 0
    coinc_eve_satellite = 0
    coinc_bob_satellite = 0
    for n in range(len(eve_random_base)):
        if eve_random_base[n] == bob_random_base[n]:
            coinc_eve_bob += 1
        if eve_random_base[n] == satellite_random_base[n]:
            coinc_eve_satellite += 1
        if bob_random_base[n] == satellite_random_base[n]:
            coinc_bob_satellite += 1

    eve_raw_key = ['-'] * N
    for k in range(N):
        if eve_random_base[k] != '-':
            error = machine_error()  # aplico també error maquina del 3%
            if bob_random_base[k] == eve_random_base[k]:
                if not error:
                    eve_raw_key[k] = bob_raw_key[k]
                else:
                    if bob_raw_key[k] == '1':
                        eve_raw_key[k] = '0'
                    else:
                        eve_raw_key[k] = '1'

            else:
                if eve_random_base[k] == 'vert&hor':
                    state = random.choice(['vertical', 'horizontal'])
                else:
                    state = random.choice(['+45', '-45'])

                if error:
                    eve_raw_key[k] = xor(st_qbit[state], '1')
                else:
                    eve_raw_key[k] = st_qbit[state]

    encerts = 0
    for n in range(len(eve_raw_key)):
        if eve_raw_key[n] == bob_raw_key[n]:
            encerts += 1
    print('Percentatge de la clau correcta (eve - bob): ' + str(int(encerts) / N * 100) + '%.')  # 75% - err%
    print('')

    satellite_raw_key = ['-'] * N  # it gets different than it would be with no eve. AQUI ESTA EL ERROR!
    for i in range(N):
        error = machine_error()  # aplico error maquina del 3%
        if i == eve_measure_pos[i] and satellite_random_base[i] == eve_random_base[i]:  # eve mesura i determina resultat
            if not error:
                satellite_raw_key[i] = eve_raw_key[i]
            else:
                if eve_raw_key[i] == '0':
                    satellite_raw_key[i] = '1'
                else:
                    satellite_raw_key[i] = '0'

        elif i == eve_measure_pos[i] and satellite_random_base[i] != eve_random_base[i]:  # eve mesura i no determina
            if satellite_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                satellite_raw_key[i] = xor(st_qbit[state], '1')
            else:
                satellite_raw_key[i] = st_qbit[state]

        elif i != eve_measure_pos[i] and satellite_random_base[i] == bob_random_base[
            i]:  # aqui quan eve no mesura, lo de sempre
            if not error:
                satellite_raw_key[i] = bob_raw_key[i]
            else:
                if bob_raw_key[i] == '0':
                    satellite_raw_key[i] = '1'
                else:
                    satellite_raw_key[i] = '0'

        elif i != eve_measure_pos[i] and satellite_random_base[i] != bob_random_base[i]:
            if satellite_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                satellite_raw_key[i] = xor(st_qbit[state], '1')
            else:
                satellite_raw_key[i] = st_qbit[state]

else:
    satellite_raw_key = []
    for i in range(N):
        error = machine_error()  # aplico error maquina del 3%
        if bob_random_base[i] == satellite_random_base[i]:
            if not error:
                satellite_raw_key.append(bob_raw_key[i])
            else:
                if bob_raw_key[i] == '1':
                    satellite_raw_key.append('0')
                else:
                    satellite_raw_key.append('1')

        else:
            if satellite_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                satellite_raw_key.append(xor(st_qbit[state], '1'))
            else:
                satellite_raw_key.append(st_qbit[state])

x = PrettyTable()
if eve:
    x.field_names = ["QBit Number", "Bob Random Base", "Bob Raw Key", "Satellite Raw Key", "Satellite Random Base",
                     "Eve Raw Key", "Eve Random Base"]
else:
    x.field_names = ["QBit Number", "Bob Random Base", "Bob Raw Key", "Satellite Raw Key", "Satellite Random Base"]
for i in range(len(bob_random_base)):
    if eve:
        x.add_row([i + 1, bob_random_base[i], bob_raw_key[i], satellite_raw_key[i], satellite_random_base[i], eve_raw_key[i],
                   eve_random_base[i]])
    else:
        x.add_row([i + 1, bob_random_base[i], bob_raw_key[i], satellite_raw_key[i], satellite_random_base[i]])
print(x)

input('Seguir: ')

# They discard results where they chose a different base:
if eve:
    print(len(eve_raw_key))
if eve:
    no_coincideixen_eve = []  # when Bob and Satellite match but Eve doesn't: the result won't be discarded. ('-')
    no_coincideixen_bob_satellite = []  # When Bob and Satellite don't match: the result will be discarded. (removed)
    for n in range(N):
        if bob_random_base[n] != satellite_random_base[n]:
            no_coincideixen_bob_satellite.append(n)
        elif bob_random_base[n] == satellite_random_base[n] and bob_random_base[n] != eve_random_base[n]:
            no_coincideixen_eve.append(n)

    no_coincideixen_bob_satellite = sorted(no_coincideixen_bob_satellite)
    no_coincideixen_eve = sorted(no_coincideixen_eve)
    for k in reversed(no_coincideixen_eve):
        eve_raw_key[k] = '-'
    for j in reversed(no_coincideixen_bob_satellite):
        eve_raw_key.pop(j)
    print(len(eve_raw_key))
    eve_sifted_key = eve_raw_key

if eve:
    x.field_names = ["Qbit Number", "Bob Base", "Bob Sifted Key", "Satellite Sifted Key", "Satellite base", "Eve Sifted Key",
                     "Eve Random Base"]
else:
    x.field_names = ["Qbit Number", "Bob Base", "Bob Sifted Key", "Satellite Sifted Key", "Satellite base"]
cont = 0
for i in range(N - 1, -1, -1):
    if bob_random_base[i] != satellite_random_base[i]:
        bob_random_base[i] = '---'
        bob_raw_key[i] = '---'
        satellite_raw_key[i] = '---'
        satellite_random_base[i] = '---'
        x.del_row(i)
        cont += 1
print(x)
print(cont)
input('Seguir: ')

# All lists have --- in the same positions, so:
ns = []
for n in range(len(bob_raw_key)):
    if bob_raw_key[n] == '---':
        ns.append(n)

for pos in reversed(ns):
    bob_random_base.pop(pos)
    bob_raw_key.pop(pos)
    satellite_random_base.pop(pos)
    satellite_raw_key.pop(pos)

bob_sifted_key = bob_raw_key
satellite_sifted_key = satellite_raw_key
print('')
if eve:
    print('Comprovacio error de mida: ' + str(len(bob_sifted_key)) + ' =? ' + str(len(eve_sifted_key)))
    print('')
    encert = 0
    for n in range(len(eve_sifted_key)):
        if eve_sifted_key[n] == bob_sifted_key[n]:
            encert += 1
    print('Informació Eve abans de correccio: ' + str(encert / len(bob_sifted_key) * 100) + '%')

print('The length of the raw key was reduced by aprox. ' + str(int((N - len(bob_sifted_key)) / N * 100)) + '%')

# Ara fem públic el 25% de la sifted key per comprovar si hi ha Eve.
input('Seguir: ')
quants_publico = len(bob_sifted_key) // 4
pos_public = []
qbit_public_bob = []
qbit_public_satellite = []
llista_per_no_repetir = list(range(len(bob_sifted_key)))
while len(pos_public) < quants_publico:
    pos = random.choice(llista_per_no_repetir)
    llista_per_no_repetir.remove(pos)

    pos_public.append(pos)
    qbit_public_bob.append((bob_sifted_key[pos]))

print('Bob publica un percentatge de posicions i Qbits, després Satellite publica'
      'els Qbits de les mateixes posicions per a veure si la communicació és segura:')

for pos in pos_public:
    qbit_public_satellite.append((satellite_sifted_key[pos]))

x = PrettyTable()
x.field_names = ["Positions", "Bob Qbits", "Satellite Qbits"]
for i in range(len(pos_public)):
    x.add_row([pos_public[i], qbit_public_bob[i], qbit_public_satellite[i]])
print(x)
# Ara es comparen els resultats per determinar si la comunicació és segura:
num_err = 0
for n in range(len(qbit_public_bob)):
    if qbit_public_bob[n] != qbit_public_satellite[n]:
        num_err += 1

percent_num_err = int(num_err / quants_publico * 100)
if percent_num_err <= tolerancia:
    print('The communication is safe. Match error of ' + str(percent_num_err) + '%.')
else:
    print('The communication is NOT safe. Match error of ' + str(percent_num_err) + '%.')
    import sys

    sys.exit('COMMUNICATION ABORTED.')

for poses in reversed(sorted(pos_public)):
    bob_sifted_key.pop(poses)
    satellite_sifted_key.pop(poses)

# Eve (si ha passat desapercebuda) també haurà d'eliminar els qbits públics tal com han fet Satellite i Bob.
if eve:
    for poses in reversed(sorted(pos_public)):
        eve_sifted_key.pop(poses)

# ERROR CORRECTION in the resulting key:
indicadors = list(range(len(bob_sifted_key)))
bob_xors = []
llista_xors = []
for i in range(len(bob_sifted_key) // 2):
    num1 = 0;
    num2 = 0
    while num1 == num2:
        num1 = random.choice(indicadors)
        num2 = random.choice(indicadors)
    numeros = [num1, num2]
    llista_xors.append(numeros)
    for n in numeros:
        indicadors.remove(n)

# Ara es fan públics els valors de XOR i les posicions dels bits amb què s'han obtingut.

bob_xors = []
for pair in llista_xors:
    res = xor(bob_sifted_key[pair[0]], bob_sifted_key[pair[1]])
    bob_xors.append(res)

satellite_xors = []
for pair in llista_xors:
    res = xor(satellite_sifted_key[pair[0]], satellite_sifted_key[pair[1]])
    satellite_xors.append(res)

# Eve ha d'efectuar la mateixa operació amb els qbits que tingui disponibles:
if eve:
    eve_xors = []
    for pair in llista_xors:
        if eve_sifted_key[pair[0]] != '-' and eve_sifted_key[pair[1]] != '-':  # Si disposa dels qbits.
            res = xor(eve_sifted_key[pair[0]], eve_sifted_key[pair[1]])
            eve_xors.append(res)
        else:
            eve_xors.append('-')

x = PrettyTable()
if eve:
    x.field_names = ["Pairs", "Bob XOR", "Satellite XOR", "Eve XOR"]
else:
    x.field_names = ["Pairs", "Bob XOR", "Satellite XOR"]
for i in range(len(llista_xors)):
    if eve:
        x.add_row([llista_xors[i], bob_xors[i], satellite_xors[i], eve_xors[i]])
    else:
        x.add_row([llista_xors[i], bob_xors[i], satellite_xors[i]])
print(x)

'''
Es fan públics els resultats i es descarten els bits que provoquen XORs discordants.
Eve efectua en paral·lel la mateixa operació, perque els XORs son publics i les posicions dels qbits
amb què s'han calculat també.
'''

elim = []
elim_eve = []
for n in range(len(llista_xors)):
    if bob_xors[n] != satellite_xors[n]:
        elim.append(llista_xors[n][0])
        elim.append(llista_xors[n][1])
        if eve:
            elim_eve.append(llista_xors[n][0])
            elim_eve.append(llista_xors[n][1])

# Satellite and Bob, privately:
elim = list(reversed(sorted(elim)))
for j in elim:
    bob_sifted_key.pop(int(j))
    satellite_sifted_key.pop(int(j))

# Eve, in parallel:
if eve:
    elim_eve = list(reversed(sorted(elim_eve)))
    for j in elim_eve:
        eve_sifted_key.pop(int(j))

bob_corrected_key = bob_sifted_key
satellite_corrected_key = satellite_sifted_key
if eve:
    eve_corrected_key = eve_sifted_key

# Comprovem nosaltres l'èxit de la correcció d'errors i la repercussió en la informació que posseeix Eve:
num_err_bob_satellite = 0
num_err_eve = 0
for n in range(len(satellite_corrected_key)):
    if bob_corrected_key[n] != satellite_corrected_key[n]:
        num_err_bob_satellite += 1

percent_num_err_bob_satellite = num_err_bob_satellite / len(bob_corrected_key) * 100

if eve:
    for n in range(len(bob_corrected_key)):
        if bob_corrected_key[n] != eve_corrected_key[n]:
            num_err_eve += 1

    percent_num_err_eve = num_err_eve / len(bob_corrected_key) * 100

x = PrettyTable()
if eve:
    x.field_names = ["Bob Corrected", "Satellite Corrected", "Eve Corrected"]
else:
    x.field_names = ["Bob Corrected", "Satellite Corrected"]
for i in range(len(bob_corrected_key)):
    if eve:
        x.add_row([bob_corrected_key[i], satellite_corrected_key[i], eve_corrected_key[i]])
    else:
        x.add_row([bob_corrected_key[i], satellite_corrected_key[i]])
print(x)

print('')
print('Mistakes after correction: ' + str(num_err_bob_satellite) + ' That is ' + str(percent_num_err_bob_satellite) + '%')
if eve:
    print("Eve's information of the key: " + str(100 - percent_num_err_eve) + '%')

# EVE'S INFORMATION REDUCTION:
indicadors = list(range(len(bob_corrected_key)))
bob_xors = []
llista_xors = []
for i in range(len(bob_corrected_key) // 2):
    num1 = 0;
    num2 = 0
    while num1 == num2:
        num1 = random.choice(indicadors)
        num2 = random.choice(indicadors)
    numeros = [num1, num2]
    llista_xors.append(numeros)
    for n in numeros:
        indicadors.remove(n)

# Ara es fa pública NOMÉS LA LLISTA DE POSICIONS.

# Cadascú per la seva banda efectúa les operacions:
bob_xors = []
for pair in llista_xors:
    res = xor(bob_corrected_key[pair[0]], bob_corrected_key[pair[1]])
    bob_xors.append(res)

satellite_xors = []
for pair in llista_xors:
    res = xor(satellite_corrected_key[pair[0]], satellite_corrected_key[pair[1]])
    satellite_xors.append(res)

# Eve ha d'efectuar la mateixa operació amb els qbits que tingui disponibles:
if eve:
    eve_xors = []
    for pair in llista_xors:
        if eve_sifted_key[pair[0]] != '-' and eve_sifted_key[pair[1]] != '-':  # Si disposa dels qbits.
            res = xor(eve_corrected_key[pair[0]], eve_corrected_key[pair[1]])
            eve_xors.append(res)
        else:
            eve_xors.append('-')
bob_final_key = bob_xors
satellite_final_key2 = satellite_xors
# El resultat del producte es la clau definitiva:

if eve:
    eve_final_key = eve_xors
    print('Eve final key: ' + str(len(eve_final_key)) + ' ' + str(eve_final_key))
x = PrettyTable()
if eve:
    x.field_names = ["Pairs", "Bob Final Key", "Satellite Final Key", "Eve Final Key"]
else:
    x.field_names = ["Pairs", "Bob Final Key", "Satellite Final Key"]
for i in range(len(bob_final_key)):
    if eve:
        x.add_row([llista_xors[i], bob_final_key[i], satellite_final_key2[i], eve_final_key[i]])
    else:
        x.add_row([llista_xors[i], bob_final_key[i], satellite_final_key2[i]])
print(x)

# Comprovem que l'operació ha servit per reduir la informació de Eve:
if eve:
    correcte = 0
    for n in range(len(eve_final_key)):
        if eve_final_key[n] == bob_final_key[n]:
            correcte += 1
    print('')
    print('Eve possesses the ' + str(correcte / len(bob_final_key) * 100) + '% of the key.')

# Comprovem que l'error és mínim entre les claus finals de  l'Satellite i el Bob:
error_final = 0
for n in range(len(bob_final_key)):
    if bob_final_key[n] != satellite_final_key2[n]:
        error_final += 1

fin_perc = error_final / len(bob_final_key) * 100
print('')
print('The final keys differ in ' + str(error_final) + ' positions. That is: ' + str(fin_perc) + '% error.')

public_key = xor_missatge_clau(satellite_final_key1, satellite_final_key2)
'''
Una vegada generades les dues claus necessàries per a la comunicació (k1 = Alice - Satellite, k2 = Bob - Satellite) el
satel·lit fa públic k1 + k2. Aleshores Alice envia el missatge a Bob encriptat amb la seva clau k1 (que només coneixen
ella i el satel·lit, que hem de suposar segur) i Bob el desencripta amb la clau pública més la seva clau k2 (que només
coneixen ell i el satel·lit) de la següent manera:

M + k1 + (k1 + k2) + k2 = M

on M és el missatge i + és l'addició binària.
'''
missatge_encripted = xor_missatge_clau(missatge_binary, alice_final_key)
missatge_decripted_pas1 = xor_missatge_clau(missatge_encripted, public_key)
missatge_decripted_pas2 = xor_missatge_clau(missatge_decripted_pas1,bob_final_key)
missatge_ascii_again = binari_a_ascii(missatge_decripted_pas2)
missatge_caracters = ascii_a_missatge(missatge_ascii_again)
print(missatge_caracters)