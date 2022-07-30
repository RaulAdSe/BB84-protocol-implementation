import random
from prettytable import PrettyTable

def missatge_a_ascii(missatge):
    v=[]
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


def machine_error():
    choice_error = random.choice(range(100))
    if choice_error == 19 or choice_error == 34 or choice_error == 35: # 3% error maquina
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

missatge = input('Message to be sent (only letters): ')
missatge_ascii = missatge_a_ascii(missatge)
missatge_binary = ascii_a_binari(missatge_ascii)

ans = input("Is there an Eve? Answer 'y'(yes) or 'n'(no): " )
if ans.lower() == 'y':
    eve = True
    tolerancia = input("Tolerance in comunication abortion (in %) [consider machine error = 3%] : ")
    tolerancia = int(tolerancia)
else:
    eve = False
    tolerancia = 8

N = len(missatge_binary)*6
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

bob_random_base = []
for i in range(N):
    b_rand_base = random.choice(['vert&hor', 'diagonal'])
    bob_random_base.append(b_rand_base)

# MEASURE OF THE QBITS SENT BY ALICE:
if eve:
    eve_measure_pos = ['-']*N
    eve_random_base = ['-']*N
    eve_percent = input('Fraction of qbits that Eve measures (in %): ')
    quants = int(N*int(eve_percent)/100)
    steps = N//quants
    for n in range(0, len(alice_raw_key), steps):
        eve_measure_pos[n] = n
        eve_base = random.choice(['vert&hor', 'diagonal'])
        eve_random_base[n] = eve_base

    print('eve measures: len ' + str(len(eve_measure_pos)) + ' ' + str(eve_measure_pos))
    print('')
    print('Eve random base: len ' + str(len(eve_random_base)))
    print(eve_random_base)

    #EXTRA PER COMPROVAR ERRORS AL CODI:
    coinc_eve_alice = 0
    coinc_eve_bob = 0
    coinc_alice_bob = 0
    for n in range(len(eve_random_base)):
        if eve_random_base[n] == alice_random_base[n]:
            coinc_eve_alice += 1
        if eve_random_base[n] == bob_random_base[n]:
            coinc_eve_bob += 1
        if alice_random_base[n] == bob_random_base[n]:
            coinc_alice_bob += 1

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

    print('Eve raw key: len ' + str(len(eve_raw_key)))
    print(eve_raw_key)

    encerts = 0
    for n in range(len(eve_raw_key)):
        if eve_raw_key[n] == alice_raw_key[n]:
            encerts += 1
    print('Percentatge de la clau correcta (eve - alice): ' + str(int(encerts)/N * 100) + '%.') # 75% - err%
    print('')



    bob_raw_key = ['-']*N  # it gets different than it would be with no eve. AQUI ESTA EL ERROR!
    for i in range(N):
        error = machine_error()  # aplico error maquina del 3%
        if i == eve_measure_pos[i] and bob_random_base[i] == eve_random_base[i]:  # eve mesura i determina resultat
            if not error:
                bob_raw_key[i] = eve_raw_key[i]
            else:
                if eve_raw_key[i] == '0':
                    bob_raw_key[i] = '1'
                else:
                    bob_raw_key[i] = '0'

        elif i == eve_measure_pos[i] and bob_random_base[i] != eve_random_base[i]:  # eve mesura i no determina
            if bob_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                bob_raw_key[i] = xor(st_qbit[state], '1')
            else:
                bob_raw_key[i] = st_qbit[state]

        elif i != eve_measure_pos[i] and bob_random_base[i] == alice_random_base[i]:  # aqui quan eve no mesura, lo de sempre
            if not error:
                bob_raw_key[i] = alice_raw_key[i]
            else:
                if alice_raw_key[i] == '0':
                    bob_raw_key[i] = '1'
                else:
                    bob_raw_key[i] = '0'

        elif i != eve_measure_pos[i] and bob_random_base[i] != alice_random_base[i]:
            if bob_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                bob_raw_key[i] = xor(st_qbit[state], '1')
            else:
                bob_raw_key[i] = st_qbit[state]

else:
    bob_raw_key = []
    for i in range(N):
        error = machine_error()  # aplico error maquina del 3%
        if alice_random_base[i] == bob_random_base[i]:
            if not error:
                bob_raw_key.append(alice_raw_key[i])
            else:
                if alice_raw_key[i] == '1':
                    bob_raw_key.append('0')
                else:
                    bob_raw_key.append('1')

        else:
            if bob_random_base[i] == 'vert&hor':
                state = random.choice(['vertical', 'horizontal'])
            else:
                state = random.choice(['+45', '-45'])

            if error:
                bob_raw_key.append(xor(st_qbit[state], '1'))
            else:
                bob_raw_key.append(st_qbit[state])


# ara represento amb pandas la base de cadascu.
x = PrettyTable()
x.field_names = ["QBit Number", "Alice Random Base", "Alice Raw Key", "Bob Raw Key", "Bob Random Base"]
for i in range(len(alice_random_base)):
    x.add_row([i + 1, alice_random_base[i], alice_raw_key[i], bob_raw_key[i], bob_random_base[i]])
print(x)

input('Seguir: ')

# They discard results where they chose a different base:
if eve:
    no_coincideixen_eve = []  # when Alice and Bob match but Eve doesn't: the result won't be discarded. ('-')
    no_coincideixen_alice_bob = []  # When Alice and Bob don't match: the result will be discarded. (removed)
    for n in range(N):
        if alice_random_base[n] != bob_random_base[n]:
            no_coincideixen_alice_bob.append(n)
        elif alice_random_base[n] == bob_random_base[n] and alice_random_base[n] != eve_random_base[n]:
            no_coincideixen_eve.append(n)

    no_coincideixen_alice_bob = sorted(no_coincideixen_alice_bob)
    no_coincideixen_eve = sorted(no_coincideixen_eve)
    for k in reversed(no_coincideixen_eve):
        eve_raw_key[k] = '-'
    for j in reversed(no_coincideixen_alice_bob):
        eve_raw_key.pop(j)

    eve_sifted_key = eve_raw_key

print('alice_random_base' + 'alice_raw_key' + 'bob_raw_key' + 'bob_random_base')
x = PrettyTable()
x.field_names= ["Qbit Number", "Alice Base", "Alice Raw Key", "Bob Raw Key", "Bob base"]
for i in range(N):
    x.add_row([i + 1, alice_random_base[i], alice_raw_key[i], bob_raw_key[i], bob_random_base[i]])
print(x)
x.field_names= ["Qbit Number", "Alice Base", "Alice Sifted Key", "Bob Sifted Key", "Bob base"]
for i in range(N-1, 0, -1):
    if alice_random_base[i] != bob_random_base[i]:
        alice_random_base[i] = '---'
        alice_raw_key[i] = '---'
        bob_raw_key[i] = '---'
        bob_random_base[i] = '---'
        x.del_row(i)
print(x)
input('Seguir: ')

# All lists have --- in the same positions, so:
ns = []
for n in range(len(alice_raw_key)):
    if alice_raw_key[n] == '---':
        ns.append(n)

for pos in reversed(ns):
    alice_random_base.pop(pos)
    alice_raw_key.pop(pos)
    bob_random_base.pop(pos)
    bob_raw_key.pop(pos)

alice_sifted_key = alice_raw_key
bob_sifted_key = bob_raw_key
print('')
if eve:
    print('eve_sifted_key ' + str(len(eve_sifted_key)))
    print(eve_sifted_key)
    print('Comprovacio error de mida: ' + str(len(alice_sifted_key)) + ' =? ' + str(len(eve_sifted_key)))
    print('')
    encert = 0
    for n in range(len(eve_sifted_key)):
        if eve_sifted_key[n] == alice_sifted_key[n]:
            encert += 1
    print('Informació Eve abans de correccio: ' + str(encert/len(alice_sifted_key)*100) + '%')

#print('alice_sifted_key ' + str(len(alice_sifted_key)))
#print(alice_sifted_key)
#print('bob_sifted_key ' + str(len(bob_sifted_key)))
#print(bob_sifted_key)
print('The length of the raw key was reduced by aprox. ' + str(int((N - len(alice_sifted_key))/N*100)) + '%')

# Ara fem públic el 25% de la sifted key per comprovar si hi ha Eve.
input('Seguir: ')
quants_publico = len(alice_sifted_key)//4
print('Fem públic uns determinats bits: ')
pos_public = []
qbit_public_alice = []
qbit_public_bob = []
llista_per_no_repetir = list(range(len(alice_sifted_key)))
while len(pos_public) < quants_publico:
    pos = random.choice(llista_per_no_repetir)
    llista_per_no_repetir.remove(pos)

    pos_public.append(pos)
    qbit_public_alice.append((alice_sifted_key[pos]))

print('Alice publica un percentatge de posicions i Qbits per a veure si la communicació és segura:')
print('Posicions: ' + str(pos_public))
print('Alice qbits: ' + str(qbit_public_alice))

# Ara Bob publica els seus qbits corresponents a les mateixes posicions que Alice:
for pos in pos_public:
    qbit_public_bob.append((bob_sifted_key[pos]))

print('Bob publica qbits obtinguts: ')
print('Bob qbits: ' + str(qbit_public_bob))
print('')

# Ara es comparen els resultats per determinar si la comunicació és segura:
num_err = 0
for n in range(len(qbit_public_alice)):
    if qbit_public_alice[n] != qbit_public_bob[n]:
        num_err += 1

percent_num_err = int(num_err/quants_publico * 100)
if percent_num_err <= tolerancia:
    print('The communication is safe. Match error of ' + str(percent_num_err) + '%.')
else:
    print('The communication is NOT safe. Match error of ' + str(percent_num_err) + '%.')
    import sys
    sys.exit('COMMUNICATION ABORTED.')

for poses in reversed(sorted(pos_public)):
    alice_sifted_key.pop(poses)
    bob_sifted_key.pop(poses)

# Eve (si ha passat desapercebuda) també haurà d'eliminar els qbits públics tal com han fet Alice i Bob.
if eve:
    for poses in reversed(sorted(pos_public)):
        eve_sifted_key.pop(poses)


# ERROR CORRECTION in the resulting key:
indicadors = list(range(len(alice_sifted_key)))
alice_xors = []
llista_xors = []
for i in range(len(alice_sifted_key)//2):
    num1 = 0; num2 = 0
    while num1 == num2:
        num1 = random.choice(indicadors)
        num2 = random.choice(indicadors)
    numeros = [num1, num2]
    llista_xors.append(numeros)
    for n in numeros:
        indicadors.remove(n)

# Ara es fan públics els valors de XOR i les posicions dels bits amb què s'han obtingut.
print('')
print('PÚBLIC:')
print(llista_xors)

alice_xors = []
for pair in llista_xors:
    res = xor(alice_sifted_key[pair[0]], alice_sifted_key[pair[1]])
    alice_xors.append(res)

bob_xors = []
for pair in llista_xors:
    res = xor(bob_sifted_key[pair[0]], bob_sifted_key[pair[1]])
    bob_xors.append(res)

# Eve ha d'efectuar la mateixa operació amb els qbits que tingui disponibles:
if eve:
    eve_xors = []
    for pair in llista_xors:
        if eve_sifted_key[pair[0]] != '-' and eve_sifted_key[pair[1]] != '-': # Si disposa dels qbits.
            res = xor(eve_sifted_key[pair[0]], eve_sifted_key[pair[1]])
            eve_xors.append(res)
        else:
            eve_xors.append('-')

'''
Es fan públics els resultats i es descarten els bits que provoquen XORs discordants.
Eve efectua en paral·lel la mateixa operació, perque els XORs son publics i les posicions dels qbits
amb què s'han calculat també.
'''
print('alice_xors' + str(alice_xors))
print('bob_xors' + str(bob_xors))
elim = []
elim_eve = []
for n in range(len(llista_xors)):
    if alice_xors[n] != bob_xors[n]:
        elim.append(llista_xors[n][0])
        elim.append(llista_xors[n][1])
        if eve:
            elim_eve.append(llista_xors[n][0])
            elim_eve.append(llista_xors[n][1])

# Alice and Bob, privately:
elim = list(reversed(sorted(elim)))
for j in elim:
    alice_sifted_key.pop(int(j))
    bob_sifted_key.pop(int(j))

# Eve, in parallel:
if eve:
    elim_eve = list(reversed(sorted(elim_eve)))
    for j in elim_eve:
        eve_sifted_key.pop(int(j))

alice_corrected_key = alice_sifted_key
bob_corrected_key = bob_sifted_key
if eve:
    eve_corrected_key = eve_sifted_key

# Comprovem nosaltres l'èxit de la correcció d'errors i la repercussió en la informació que posseeix Eve:
num_err_alice_bob = 0
num_err_eve = 0
for n in range(len(bob_corrected_key)):
    if alice_corrected_key[n] != bob_corrected_key[n]:
        num_err_alice_bob += 1

percent_num_err_alice_bob = num_err_alice_bob/len(alice_corrected_key) * 100

if eve:
    for n in range(len(alice_corrected_key)):
        if alice_corrected_key[n] != eve_corrected_key[n]:
            num_err_eve += 1

    percent_num_err_eve = num_err_eve / len(alice_corrected_key) * 100

print('')
print('Mistakes after correction: ' + str(num_err_alice_bob) + ' That is ' + str(percent_num_err_alice_bob) + '%')
if eve:
    print("Eve's information of the key: " + str(100 - percent_num_err_eve) + '%')

print('')
print('Alice corrected: ' + str(len(alice_corrected_key)) + ' ' + str(alice_corrected_key))
print('Bob corrected: ' + str(len(bob_corrected_key)) + ' ' + str(bob_corrected_key))
if eve:
    print('Eve corrected: ' + str(len(eve_corrected_key)) + ' ' + str(eve_corrected_key))

# EVE'S INFORMATION REDUCTION:
indicadors = list(range(len(alice_corrected_key)))
alice_xors = []
llista_xors = []
for i in range(len(alice_corrected_key)//2):
    num1 = 0; num2 = 0
    while num1 == num2:
        num1 = random.choice(indicadors)
        num2 = random.choice(indicadors)
    numeros = [num1, num2]
    llista_xors.append(numeros)
    for n in numeros:
        indicadors.remove(n)

# Ara es fa pública NOMÉS LA LLISTA DE POSICIONS.
print('')
print('PÚBLIC:')
print(llista_xors)

# Cadascú per la seva banda efectúa les operacions:
alice_xors = []
for pair in llista_xors:
    res = xor(alice_corrected_key[pair[0]], alice_corrected_key[pair[1]])
    alice_xors.append(res)

bob_xors = []
for pair in llista_xors:
    res = xor(bob_corrected_key[pair[0]], bob_corrected_key[pair[1]])
    bob_xors.append(res)

# Eve ha d'efectuar la mateixa operació amb els qbits que tingui disponibles:
if eve:
    eve_xors = []
    for pair in llista_xors:
        if eve_sifted_key[pair[0]] != '-' and eve_sifted_key[pair[1]] != '-': # Si disposa dels qbits.
            res = xor(eve_corrected_key[pair[0]], eve_corrected_key[pair[1]])
            eve_xors.append(res)
        else:
            eve_xors.append('-')

# El resultat del producte es la clau definitiva:
alice_final_key = alice_xors
print('Alice final key: ' + str(len(alice_final_key)) + ' ' + str(alice_final_key))
bob_final_key = bob_xors
print('Bob final key: ' + str(len(bob_final_key)) + ' ' + str(bob_final_key))
if eve:
    eve_final_key = eve_xors
    print('Eve final key: ' + str(len(eve_final_key)) + ' ' + str(eve_final_key))

# Comprovem que l'operació ha servit per reduir la informació de Eve:
if eve:
    correcte = 0
    for n in range(len(eve_final_key)):
        if eve_final_key[n] == alice_final_key[n]:
            correcte += 1
    print('')
    print('Eve possesses the ' + str(correcte/len(alice_final_key) * 100) + '% of the key.')

# Comprovem que l'error és mínim entre les claus finals de  l'Alice i el Bob:
error_final = 0
for n in range(len(alice_final_key)):
    if alice_final_key[n] != bob_final_key[n]:
        error_final += 1

fin_perc = error_final/len(alice_final_key) * 100
print('')
print('The final keys differ in ' + str(error_final) + ' positions. That is: ' + str(fin_perc) + '% error.')