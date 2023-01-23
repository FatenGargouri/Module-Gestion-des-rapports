# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time, timedelta
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from pytz import timezone



class RapportJournalier(models.TransientModel):
    _name = 'rapport.journalier'
    _description = "Rapport journalier des employés"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2many('hr.employee', string="Employee")
    from_date = fields.Date(string='Date début', default=lambda self: fields.Date.to_string(date.today()),
                            required=True)

    to_date = fields.Date(string="Date fin", required=True)

    def print_report(self, data=None):
        # domain le tableau qui va contenir la liste des employés
        domain = []
        #Datas sont les donnés qui sont chargé vers le rapport
        datas = []
        if self.employee_id:
            domain.append(('id', '=', self.employee_id.ids))
        # chercher des employés
        employees = self.env['hr.employee'].search(domain)
        for employee in employees:
            tz = timezone(employee.resource_calendar_id.tz)
            date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.from_date)), time.min))

            date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.to_date)), time.max))
            # il prend la date debut par defaut
            #ajouter les dates dans un tableau
            daterange = []
            curr_date = date_from.date()
            daterange.append(curr_date)
            #Si date_from différent de date_fin  on calcule la différence et on le mettre dans le meme tableau .
            if date_from.date() != date_to.date():
                nb_jours = str(date_to - date_from)
                # Décomposition des jours dans une liste
                li = list(nb_jours.split(" "))
                #transférer l'élement en entier
                nb = int(li[0])
                for i in range(nb):
                    #ancien date + 1
                    new_date = curr_date + timedelta(days=1)
                    curr_date = new_date
                    daterange.append(new_date)

            # Indiquer si l'employé est présent ou absent .
            for rec in daterange:
                attendances = self.env["hr.attendance"].search(
                    [('employee_id', '=', employee.id), ('check_in', '>=', rec),
                     ('check_out', '<=', rec)])
                attendances1 = self.env["hr.attendance"].search(
                    [('employee_id', '=', employee.id), ('check_in', '>=', rec),('check_out','=',False)])
                # Par défaut , l'employé est absent
                etat = "Absent"
                if attendances:
                    etat = "Present"
                elif attendances1:
                    etat = "Present"


                # Indiquer si l'employé est en repos ou non .
                day = rec.weekday()
                if day in [5, 6]:
                    etat = "Repos"


                public = self.env["resource.calendar.leaves"].search([('date_from', '<=', rec), ('date_to', '>=', rec),('name','not ilike', 'Congés')])
                if public:
                    etat = "Repos"


                # Indiquer si l'employé est en congés ou non .
                conges = self.env["hr.leave"].search(
                    [('employee_id', '=', employee.id), ('date_from', '<=', rec),('date_to', '>=', rec),
                     ('state', 'in', ['validate', 'validate1'])])
                if conges:
                    etat = "Congés"
                #Déclarer 2 tableau qui prendre les valeurs check_in et check_out
                entree = []
                sortie = []
                worked_hours = 0
                #si l'employé est présent , il marque son arrivé , sortie et worked_hours
                if attendances:
                    for att in attendances:
                        new_date_time = att.check_in + timedelta(hours=2)
                        entree.insert(0, new_date_time.time())
                        new_date_time = att.check_out + timedelta(hours=2)
                        sortie.insert(0, new_date_time.time())
                        worked_hours += att.worked_hours
                # if attendances1:
                #     for att1 in attendances1:
                #         new_date_time1 = att1.check_in + timedelta(hours=2)
                #         entree.insert(0, new_date_time1.time())


                datas.append({
                    'date': rec,
                    'name': employee.name,
                    'entre': entree,
                    'sortie': sortie,
                    'worked_hours': worked_hours,
                    'etat': etat,
                })
        res = {
            'attendances': datas,
            'start_date': self.from_date,
            'end_date': self.to_date,
        }
        data = {
            'form': res,
        }

        return self.env.ref('employe_rapport.rapport_journalier').report_action([], data=data)

    @api.constrains('from_date', 'to_date')
    def _check_date(self):
        from_date = self.from_date
        to_date = self.to_date
        if from_date > to_date:
            raise ValidationError("Date début doit inférieur à date fin")

    @api.constrains('to_date')
    def _check_date_from(self):
        to_date = self.to_date
        dateToday = datetime.today().date()
        if to_date >= dateToday:
            raise ValidationError("La champ date to doit etre inférieur à date d'aujourd'hui")
