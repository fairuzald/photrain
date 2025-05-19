# elearning_survey/models/slide.py
from odoo import models, fields, api

class Slide(models.Model):
    _inherit = 'slide.slide'

    quiz_survey_id = fields.Many2one(
        'survey.survey', string="Quiz Survey",
        help="Pilih survey yang akan dijadikan kuis untuk slide ini."
    )
    quiz_url = fields.Char(
        string="Survey Link", compute="_compute_quiz_url",
        help="URL start survey untuk kuis slide ini"
    )

    @api.depends('quiz_survey_id')
    def _compute_description(self):
        for s in self:
            base = s.description or ''
            if s.quiz_survey_id:
                link = f'<p><a href="/survey/start/{s.quiz_survey_id.id}?slide_id={s.id}" class="btn btn-primary">Kerjakan Kuis</a></p>'
                # hapus dulu duplikat, lalu append
                base = base.replace(link, '')
                s.description = base + link

    description = fields.Html(compute='_compute_description', store=True)
    @api.depends('quiz_survey_id')
    def _compute_quiz_url(self):
        for rec in self:
            rec.quiz_url = (
                f'/survey/start/{rec.quiz_survey_id.id}?slide_id={rec.id}'
                if rec.quiz_survey_id else
                ''
            )

    @api.model_create_multi
    def create(self, vals_list):
        slides = super().create(vals_list)
        slides._inject_quiz_button()
        return slides

    def write(self, vals):
        res = super().write(vals)
        if 'quiz_survey_id' in vals:
            self._inject_quiz_button()
        return res

    def _inject_quiz_button(self):
        btn_html = (
            '<div class="mt-3">'
            '<a href="{url}" class="btn btn-primary" target="_blank">'
            'Kerjakan Kuis</a>'
            '</div>'
        )
        for slide in self:
            if slide.quiz_survey_id:
                html = btn_html.format(url=slide.quiz_url)
                # pastikan tidak duplikat
                if slide.content and html in slide.content:
                    continue
                slide.content = (slide.content or '') + html