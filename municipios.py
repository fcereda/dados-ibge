# coding=utf-8

import sys
from urllib.request import urlopen 
import json
import gzip
import csv

def urlGzipToJson (url):
    response = urlopen(url).read()
    #print (response)
    #exit()
    try:
    	tmp = gzip.decompress(response).decode('utf-8')
    except: 
    	tmp = response.decode('utf-8')	
    repo = json.loads(tmp)
    return repo

def urlToJson (url):
	response = urlopen(url).read()
	tmp = response.decode('utf-8')
	repo = json.loads(tmp)
	return repo

def loadUfs ():
	url = 'http://servicodados.ibge.gov.br/api/v1/localidades/estados'
	data = urlGzipToJson(url)
	return data


def loadMunicipios ():
	url = 'http://servicodados.ibge.gov.br/api/v1/localidades/municipios'
	data = urlGzipToJson(url)
	return data

def loadIdh (idMunicipio):
	url = 'http://servicodados.ibge.gov.br/api/v1/pesquisas/37/indicadores/1/resultados/{}'.format(idMunicipio)
	data = urlGzipToJson(url)
	idh = data[0]['res'][0]['res']
	return {
		'idh2000': idh['2000'],
		'idh2010': idh['2010']
	}

def loadPibEPopulacao (fileName = './fontes/pib_populacao.csv'):
	with open(fileName, 'rt', encoding='utf-8') as csvfile:
		fileReader = csv.reader(csvfile, delimiter=',')
		i = 0
		dados = []
		for row in fileReader:
			if (i > 0):
				ano = row[0]
				idMunicipio = int(row[3])
				nomeMunicipio = row[4]
				pib = row[16]
				populacao = row[17]
				pibPerCapita = row[18]
				dados.append({
					'ano': ano,
					'idMunicipio': idMunicipio,
					'pib': pib,
					'populacao': populacao,
					'pibPerCapita': pibPerCapita 
				})
				if (i==10):
					print(dados[9])	
			i+=1		
		return dados				

def adicionarDigitoVerificador (id):
	id = int(id)
	if (id > 999999 or id < 100000):
		return id
	excecoes = {
		220191: 2201919,
		220225: 2202251,
		220198: 2201988,
		261153: 2611533,
		311783: 3117836,
		315213: 3152131,
		430587: 4305871,
		520393: 5203939,
		520396: 5203962
	}	
	if (id in excecoes):
		return excecoes[id]

	tempId = id
	soma = 0
	for peso in [2,1,2,1,2,1]:
		#print('{} {}'.format(peso, tempId % 10))
		digito = (tempId % 10) * peso
		if (digito > 9):
			digito = (digito % 10) + int(digito/10)
		soma += digito
		tempId = int(tempId / 10)

	if (soma % 10):
	    digito = 10 - soma % 10
	else:
		digito = 0
	return id * 10 + digito
			


def loadGini (fileName = './fontes/gini.csv'):
	with open(fileName, 'rt', encoding='utf-8') as csvfile:
		fileReader = csv.reader(csvfile, delimiter=';')
		i = 0
		dados = []
		for row in fileReader:
			if (not row[0].strip()):
				i += 1
				continue
			if (i > 0):
				nomeEId = row[0]
				idMunicipio = int(nomeEId.split(' ')[0])
				gini2000 = row[2].replace(',', '.')
				gini2010 = row[3].replace(',', '.')
				dados.append({
					'idMunicipio': idMunicipio,
					'gini2000': gini2000,
					'gini2010': gini2010
				})
				if (i == 10):
					print ('{}-{}-{}'.format(idMunicipio, gini2000, gini2010))
			i += 1
		return dados	


def loadAreas (fileName = './fontes/area.csv'):
	with open(fileName, 'rt', encoding='utf-8') as csvfile:
		fileReader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		i = 0
		dados = []
		for row in fileReader:
			if (i <= 0):
				i += 1
				continue
			if (not row):
				print('linha vazia')
				continue	

			idMunicipio = row[4]
			if (not idMunicipio):
				continue
			else:
				idMunicipio = int(idMunicipio)
			area = row[6].replace(',', '.')
			dados.append({
				'idMunicipio': idMunicipio,
				'area': area
			})
			if (i == 10):
				print ('{}: {}'.format(idMunicipio, area))
			i += 1
		return dados	
					

def saveAsCSV (fileName, items, headers):
	with open(fileName, 'w', encoding='utf-8') as csvfile:
		fileWriter = csv.writer(csvfile, delimiter=';', quotechar='¨', quoting=csv.QUOTE_MINIMAL)
		fileWriter.writerow(headers)
		for item in items:
			try:
				row = []
				for field in headers:
					if (field in items[item]):
						row.append(items[item][field])
					else:
						row.append('')	
				fileWriter.writerow(row)
			except:
				print('Erro tentando gravar a seguinte linha:')
				print(items[item])
				exit()	


ufs = loadUfs()
print('{} ufs foram carregadas'.format(len(ufs)))
			
municipiosArr = loadMunicipios()
# Create a dictionary from the array
municipios = {}
#print(municipiosArr[0]['microrregiao']['mesorregiao']['UF']['sigla'])
for municipio in municipiosArr:
	municipios[municipio['id']] = {
		'id': municipio['id'],
		'uf': municipio['microrregiao']['mesorregiao']['UF']['sigla'],
		'nome': municipio['nome']
	}
print('{} municipios foram carregados'.format(len(municipios)))
#for uf in ufs:
	#print('{}: {}'.format(uf['sigla'], uf['id']))

for municipio in municipiosArr:
	id = int(municipio['id'])
	newId = int(id / 10)
	if (id != adicionarDigitoVerificador(newId)):
		print('Erro em adicionarDigitoVerificador. id = {}, newId = {}'.format(id, adicionarDigitoVerificador(newId)))
		exit()

print('Carregando PIB e população...')
pibPop = loadPibEPopulacao()
print('{} registros foram carregados'.format(len(pibPop)))

print('Carregando Gini...')
ginis = loadGini()
print('{} registros foram encontrados'.format(len(ginis)))


print('Carregando áreas...')
areas = loadAreas()
print('{} registros foram encontrados'.format(len(areas)))

for key,municipio in municipios.items():
	if (int(key/10) == 355030):
		print(key)

for pib in pibPop:
	id = pib['idMunicipio']
	ano = pib['ano']
	municipios[id]['pib'+ano] = pib['pib']
	municipios[id]['populacao'+ano] = pib['populacao']
	municipios[id]['pibPerCapita'+ano] = pib['pibPerCapita']

for gini in ginis:
	if (gini['idMunicipio']):
		id = adicionarDigitoVerificador(int(gini['idMunicipio']))
		municipios[id]['gini2000'] = gini['gini2000']
		municipios[id]['gini2010'] = gini['gini2010']

for area in areas:
	id = area['idMunicipio']
	if (id in municipios):
		# Há duas lagoas que aparecem nessa base e que são independentes de quaisquer municípios,
		# portanto não integram a base de dados de municípios
		municipios[id]['area'] = area['area']

#print(municipios)
#print(municipios[adicionarDigitoVerificador(530010)])	

saveAsCSV('./municipios.csv', municipios, ['id', 'uf', 'nome', 'populacao2010', 'pib2010', 'pibPerCapita2010', 'populacao2012', 'pib2012', 'pibPerCapita2012', 'populacao2014', 'pib2014', 'pibPerCapita2014', 'gini2000', 'gini2010'])

print('Carregando IDH via API do IBGE...')
#for id, municipio in municipios.items():
contador = 0
for municipio in municipiosArr:
	id = municipio['id']
	sys.stdout.write('Carregando IDH para município {} ({:0.2f})%\r'.format(id, contador / len(municipiosArr) * 100))
	sys.stdout.flush()
	idhObj = loadIdh (id)
	municipios[id]['idh2000'] = idhObj['idh2000']
	municipios[id]['idh2010'] = idhObj['idh2010']
	contador += 1

print('{} IDHs foram carregados'.format(contador))

saveAsCSV ('./municipios_idh.csv', municipios, ['id', 'uf', 'nome', 'populacao2010', 'pib2010', 'pibPerCapita2010', 'populacao2012', 'pib2012', 'pibPerCapita2012', 'populacao2014', 'pib2014', 'pibPerCapita2014', 'gini2000', 'gini2010', 'idh2000', 'idh2010'])
