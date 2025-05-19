from odoo import models, fields

class SurveyAnalytics(models.Model):
    _name = 'survey.analytics'
    _description = 'Survey Analytics'
    _auto = False

    survey_title = fields.Char("Survey")
    question_title = fields.Char("Question")
    answer_text = fields.Text("Answer")
    value_number = fields.Float("Numeric Value")
    session_date = fields.Datetime("Submitted On")

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW survey_analytics AS (
                SELECT
                    line.id as id,
                    s.title as survey_title,
                    q.title as question_title,
                    COALESCE(line.value_text_box, line.value_char_box, q_ans.value::text) AS answer_text,
                    line.value_numerical_box as value_number,
                    input.create_date as session_date
                FROM
                    survey_user_input_line line
                JOIN survey_user_input input ON line.user_input_id = input.id
                JOIN survey_question q ON line.question_id = q.id
                JOIN survey_survey s ON input.survey_id = s.id
                LEFT JOIN survey_question_answer q_ans ON line.suggested_answer_id = q_ans.id
                WHERE input.state = 'done'
            )
        """)
