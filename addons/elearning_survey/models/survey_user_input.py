from odoo import models, fields

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    slide_id = fields.Many2one('slide.slide', string="Slide Source")
    score = fields.Float("Score", readonly=True)

    def action_submit(self):
        res = super().action_submit()

        for record in self:
            correct = 0
            total = 0

            for line in record.user_input_line_ids:
                if line.answer_is_correct:
                    correct += 1
                total += 1

            record.score = (correct / total * 100) if total else 0.0

            if record.slide_id:
                progress_line = self.env['slide.partner'].search([
                    ('slide_id', '=', record.slide_id.id),
                    ('partner_id', '=', record.partner_id.id)
                ], limit=1)
                if progress_line and record.score >= 70:
                    progress_line.completed = True

        return res
