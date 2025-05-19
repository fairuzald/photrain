from odoo import models, fields, api
import statistics
from datetime import timedelta

class ElearningAnalytics(models.Model):
    _name = 'elearning.analytics'
    _description = 'Analytics eLearning'

    course_id                 = fields.Many2one('slide.channel', string='Course')
    total_students            = fields.Integer(compute='_compute_metrics', store=True)
    completion_rate           = fields.Float(string='Completion Rate (%)', compute='_compute_metrics', store=True)
    dropout_rate              = fields.Float(string='Dropout Rate (%)', compute='_compute_metrics', store=True)
    average_score             = fields.Float(string='Average Quiz Score (%)', compute='_compute_metrics', store=True)
    score_std_dev             = fields.Float(string='Score Std Dev', compute='_compute_metrics', store=True)
    pass_rate                 = fields.Float(string='Pass Rate (%)', compute='_compute_metrics', store=True)
    average_attempts_per_quiz = fields.Float(string='Avg Attempts/Quiz', compute='_compute_metrics', store=True)
    median_completion_time    = fields.Float(string='Median Completion Time (hrs)', compute='_compute_metrics', store=True)
    completion_time_std_dev   = fields.Float(string='Completion Time Std Dev (hrs)', compute='_compute_metrics', store=True)
    top_10_percentile_score   = fields.Float(string='Top 10%ile Score', compute='_compute_metrics', store=True)

    @api.depends(
        'course_id.partner_ids',
        'course_id.slide_partner_ids.completed',
        'course_id.slide_ids.question_ids',
        'course_id.slide_partner_ids.quiz_attempts_count',
        'course_id.slide_ids.quiz_first_attempt_reward',
        'course_id.slide_ids.quiz_second_attempt_reward',
        'course_id.slide_ids.quiz_third_attempt_reward',
        'course_id.slide_ids.quiz_fourth_attempt_reward',
        'course_id.slide_partner_ids.create_date', 
        'course_id.slide_partner_ids.write_date',
    )
    def _compute_metrics(self):
        for rec in self:
            course      = rec.course_id
            students    = course.partner_ids
            total       = len(students)
            rec.total_students = total

            # siswa yang menyelesaikan setidaknya 1 slide hingga selesai course
            completed_recs = course.slide_partner_ids.filtered('completed')
            completed_students = completed_recs.mapped('partner_id')
            num_completed = len(completed_students)
            rec.completion_rate = (num_completed/total*100) if total else 0.0
            rec.dropout_rate    = (1 - num_completed/total)*100 if total else 0.0

            # waktu penyelesaian per siswa (jam)
            times = []
            for stud in set(completed_recs.mapped('partner_id')):
                recs = completed_recs.filtered(lambda r: r.partner_id == stud)
                # asumsikan start_date dan completed_date tersimpan di record terakhir
                start = min(r.create_date for r in recs)
                end   = max(r.write_date  for r in recs)
                hours = (end - start).total_seconds() / 3600.0 if start and end else 0.0
                times.append(hours)
            rec.median_completion_time  = statistics.median(times) if times else 0.0
            rec.completion_time_std_dev = statistics.stdev(times) if len(times)>1 else 0.0

            # skor quiz per siswa
            quiz_slides = course.slide_ids.filtered(lambda s: s.question_ids)
            max_rewards = [s.quiz_first_attempt_reward or 0.0 for s in quiz_slides]
            max_total = sum(max_rewards) if max_rewards else 0.0

            scores   = []
            attempts = []
            for stud in students:
                total_reward = 0.0
                total_attempts = 0
                for slide in quiz_slides:
                    cp = self.env['slide.slide.partner'].search([
                        ('slide_id','=', slide.id),
                        ('channel_id','=', course.id),
                        ('partner_id','=', stud.id),
                    ], limit=1)
                    cnt = cp.quiz_attempts_count if cp else 0
                    # hitung reward
                    if   cnt==1: r = slide.quiz_first_attempt_reward
                    elif cnt==2: r = slide.quiz_second_attempt_reward
                    elif cnt==3: r = slide.quiz_third_attempt_reward
                    elif cnt>=4: r = slide.quiz_fourth_attempt_reward
                    else:        r = 0.0
                    total_reward   += (r or 0.0)
                    total_attempts += cnt
                if max_total:
                    pct = total_reward/max_total*100
                    scores.append(pct)
                attempts.append(total_attempts)
            # statistik skor
            rec.average_score             = statistics.mean(scores) if scores else 0.0
            rec.score_std_dev             = statistics.stdev(scores) if len(scores)>1 else 0.0
            # pass rate threshold 60%
            passed = len([s for s in scores if s>=60.0])
            rec.pass_rate                 = (passed/len(scores)*100) if scores else 0.0
            # rata-rata attempts
            rec.average_attempts_per_quiz = statistics.mean(attempts) if attempts else 0.0
            # top 10 percentile
            if scores:
                sorted_scores = sorted(scores)
                idx = max(0, int(len(scores)*0.9) - 1)
                rec.top_10_percentile_score = sorted_scores[idx]
            else:
                rec.top_10_percentile_score = 0.0
