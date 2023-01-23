# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time, timedelta
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from pytz import timezone
from calendar import calendar


class RapportSynthese(models.TransientModel):
    _name = 'rapport.synthese'
    _description = "Rapport synthèses des employés"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2many('hr.employee', string="Employee")
    from_date = fields.Date(string= 'Date début', default=lambda self: fields.Date.to_string(date.today()),required=True)
    to_date = fields.Date(string="Date fin",required=True)

    def print_report(self):
        # domain le tableau qui va contenir la liste des employés
        domain = []
        # Datas sont les donnés qui sont chargé vers le rapport
        datas = []
        if self.employee_id:
            domain.append(('id', '=', self.employee_id.ids))
        # chercher des employés
        employees = self.env['hr.employee'].search(domain)
        for employee in employees:
            present = 0
            absent = 0
            #la différence entre date to et date from
            tz = timezone(employee.resource_calendar_id.tz)
            date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.from_date)), time.min))
            date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.to_date)), time.max))
            #La fonction list_work_time_per_day donne juste les jours de travails
            intervals = employee.list_work_time_per_day(date_from, date_to, calendar=employee.resource_calendar_id)
            for rec in intervals:
                #Le nombre de jours présents et absents
                attendances = self.env["hr.attendance"].search(
                    [('employee_id', '=', employee.id), ('check_in', '>=', rec[0]),
                     ('check_in', '<=', rec[0])])
                if attendances:
                    present += 1
                else:
                    absent += 1





                #Le nombre de congés pris
                conges = self.env["hr.leave"].search([('employee_id', '=', employee.id),('date_from','>=',date_from),('date_to','<=',date_to),('state', 'in', ['validate', 'validate1'])])
                # conges_pris=0
                diff_days = 0
                for line in conges:
                    date_start = line.date_from
                    date_end = line.date_to
                    diff_days = (date_end - date_start).days
                    # conges_pris +=1
                    diff_days +=1











            datas.append({
                'id': employee.id,
                'name': employee.name,
                'conges_pris': diff_days,
                'present': present,
                'absent': absent,
            })
        res = {
            'attendances': datas,
            'start_date': self.from_date,
            'end_date': self.to_date,
        }
        data = {
            'form': res,
        }







        return self.env.ref('employe_rapport.rapport_synthese').report_action([],data=data)

    @api.constrains('date_from','to_date')
    def _check_date(self):
        from_date = self.from_date
        to_date = self.to_date
        if from_date >= to_date:
            raise ValidationError("Date début doit inférieur à date fin")

    @api.constrains('to_date')
    def _check_date_from(self):
        to_date = self.to_date
        dateToday = datetime.today().date()
        if to_date >= dateToday:
            raise ValidationError("La champ (date fin) doit etre inférieur à date d'aujourd'hui")









