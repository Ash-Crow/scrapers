#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv

depts = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
         '12', '13', '14', '15', '16', '17', '18', '19', '2A', '2B', '21',
         '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32',
         '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43',
         '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54',
         '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65',
         '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76',
         '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87',
         '88', '89', '90', '91', '92', '93', '94', '95', '97', '98']

fieldnames = ['CLASSEMENT', 'MAIRIE', 'ADRES1 MAIRIE', 'ADRES2 MAIRIE',
              'CODE POSTAL', 'COMMUNE', 'CIVILITE MAIRE', 'PRENOM MAIRE',
              'NOM MAIRE', 'TEL', 'FAX', 'POPULATION 2016', 'EMAIL 1',
              'EMAIL 2', 'EMAIL 3', 'EMAIL 4', 'EMAIL 5', 'Site internet',
              'CODES INSEE', 'CANTONS 2015 (Nouvelles délimitations)',
              'CANTONS 2014 (Anciennes délimitations)', 'CODES SIREN',
              'RÉGIONS']

writers = {}
for dept in depts:
    with open("mairies-du-{}.csv".format(dept), 'w') as csv_output:
        writers[dept] = csv.DictWriter(csv_output,
                                       fieldnames=fieldnames,
                                       extrasaction='ignore')
        writers[dept].writeheader()

        csv_input = "Mairies de France - 06 avril 2016.csv"
with open(csv_input, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        dept = row['CODES INSEE'][0:2]
        with open("mairies-du-{}.csv".format(dept), 'a') as csv_output:
            writer = csv.DictWriter(csv_output,
                                    fieldnames=fieldnames,
                                    extrasaction='ignore')
            writer.writerow(row)
print(depts)
