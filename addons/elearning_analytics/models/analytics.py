from odoo import models, fields, api

class ElearningAnalytics(models.Model):
    _name = 'elearning.analytics'
    _description = 'Analytics eLearning'

    course_id       = fields.Many2one('slide.channel', string='Course')
    total_students  = fields.Integer(string='Total Students', compute='_compute_metrics', store=True)
    completion_rate = fields.Float(string='Completion Rate (%)', compute='_compute_metrics', store=True)
    average_score   = fields.Float(string='Average Quiz Score (%)', compute='_compute_metrics', store=True)

    @api.depends(
  'course_id.partner_ids',
  'course_id.slide_partner_ids.completed',
  'course_id.slide_ids.question_ids',
  'course_id.slide_partner_ids.quiz_attempts_count',
  'course_id.slide_ids.quiz_first_attempt_reward',
  'course_id.slide_ids.quiz_second_attempt_reward',
  'course_id.slide_ids.quiz_third_attempt_reward',
  'course_id.slide_ids.quiz_fourth_attempt_reward',
)
    def _compute_metrics(self):
        for rec in self:
            Course   = rec.course_id
            students = Course.partner_ids
            rec.total_students = len(students)
            completed = Course.slide_partner_ids.filtered('completed').mapped('partner_id')
            rec.completion_rate = (len(completed) / len(students) * 100) if students else 0.0

            # Deteksi quiz slide via question_ids
            quiz_slides = Course.slide_ids.filtered(lambda s: s.question_ids)
            student_scores = []
            max_rewards = [s.quiz_first_attempt_reward or 0.0 for s in quiz_slides]

            for stud in students:
                total_reward = 0.0
                for slide in quiz_slides:
                    cp = self.env['slide.slide.partner'].search([
                        ('slide_id',   '=', slide.id),
                        ('channel_id', '=', Course.id),
                        ('partner_id','=', stud.id),
                    ], limit=1)
                    cnt = cp.quiz_attempts_count if cp else 0
                    if   cnt == 1: r = slide.quiz_first_attempt_reward
                    elif cnt == 2: r = slide.quiz_second_attempt_reward
                    elif cnt == 3: r = slide.quiz_third_attempt_reward
                    elif cnt >=4:  r = slide.quiz_fourth_attempt_reward
                    else:          r = 0.0
                    total_reward += (r or 0.0)
                max_total = sum(max_rewards) if max_rewards else 0.0
                student_scores.append((total_reward / max_total * 100) if max_total else 0.0)

            rec.average_score = (sum(student_scores) / len(student_scores)) if student_scores else 0.0
