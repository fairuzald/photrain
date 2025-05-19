from odoo import models, fields, api

class SurveyRecommendation(models.Model):
    _name = 'survey.recommendation'
    _description = 'Survey-based Recommendations'

    name = fields.Char("Title", required=True)
    recommendation_text = fields.Text("Recommendation")

    @api.model
    def generate_recommendations(self):
        existing = self.search([('name', '=', 'Improve Photography Quality')])
        if not existing:
            records = self.env['survey.analytics'].search([])
            low_scores = [
                r for r in records
                if r.value_number and r.value_number <= 3 and 'photo' in r.question_title.lower()
            ]
            if low_scores:
                self.create({
                    'name': 'Improve Photography Quality',
                    'recommendation_text': (
                        'Customers often rate the photo results below expectations. '
                        'Consider training on composition, lighting, or editing.'
                    )
                })
