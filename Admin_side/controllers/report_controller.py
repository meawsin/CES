# controllers/report_controller.py
from database.db_manager import DBManager
from models.evaluation_model import Evaluation
from models.evaluation_template_model import EvaluationTemplate
from models.course_model import Course # Import Course model for dropdowns
from models.faculty_model import Faculty # Import Faculty model for dropdowns
import json
import pandas as pd # For CSV/Excel export (requires `pip install pandas openpyxl`)
import os
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt # For graph generation

class ReportController:
    def __init__(self):
        self.db = DBManager()

    def get_aggregated_evaluation_report(self, course_code=None, batch=None, faculty_id=None, template_id=None):
        """
        Generates an aggregated report of evaluation responses.
        Admin can see question answers but CANNOT see who submitted.
        Can filter by course, batch, faculty, template.
        """
        # Base query to get evaluations and their templates
        query = """
        SELECT
            e.feedback,
            e.comment AS general_comment,
            et.title AS template_title,
            et.questions_set,
            et.batch AS template_batch,
            e.course_code AS evaluated_course_code,
            c.name AS evaluated_course_name,
            GROUP_CONCAT(DISTINCT f.faculty_id) AS faculty_ids,
            GROUP_CONCAT(DISTINCT f.name) AS faculty_names
        FROM evaluations e
        JOIN evaluation_templates et ON e.template_id = et.id
        LEFT JOIN courses c ON e.course_code = c.course_code
        LEFT JOIN course_faculty cf ON e.course_code = cf.course_code
        LEFT JOIN faculty f ON cf.faculty_id = f.faculty_id
        WHERE 1=1
        """
        params = []

        # Add filters
        if course_code:
            query += " AND e.course_code = %s"
            params.append(course_code)
        if batch:
            query += " AND et.batch = %s" # Assuming template's batch is the target
            params.append(batch)
        if faculty_id:
            # Filter by faculty assigned to the course where evaluation was made
            query += " AND cf.faculty_id = %s"
            params.append(faculty_id)
        if template_id:
            query += " AND e.template_id = %s"
            params.append(template_id)

        query += " GROUP BY e.id" # Group by evaluation to avoid duplicate rows from GROUP_CONCAT

        all_evaluations_data = self.db.fetch_data(query, tuple(params), fetch_all=True)

        if not all_evaluations_data:
            return {
                "summary": "No evaluations found for the given criteria.",
                "total_submissions": 0,
                "report_data": {}
            }

        aggregated_results = {}
        total_submissions = 0
        rating_sums = {}  # For average calculation
        rating_counts = {}

        # Aggregate feedback
        for eval_row in all_evaluations_data:
            total_submissions += 1
            feedback_json = eval_row['feedback']
            questions_set_json = eval_row['questions_set']

            try:
                feedback = json.loads(feedback_json)
                questions_set = json.loads(questions_set_json)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON for feedback or questions_set in evaluation ID {eval_row.get('id', 'N/A')}")
                continue

            questions_list = questions_set.get('questions', [])

            for question in questions_list:
                question_text = question['text']
                question_type = question['type']
                answer = feedback.get(question_text) # Get answer by question text

                if question_text not in aggregated_results:
                    aggregated_results[question_text] = {
                        "type": question_type,
                        "options": question.get('options'), # Store options for rating/MCQ
                        "data": {} # Will store counts or lists of text answers
                    }

                # Aggregate data based on question type
                if question_type == 'rating':
                    if answer:
                        try:
                            rating_value = int(str(answer).split(' ')[0])
                            rating_sums[question_text] = rating_sums.get(question_text, 0) + rating_value
                            rating_counts[question_text] = rating_counts.get(question_text, 0) + 1
                            aggregated_results[question_text]['data'][str(answer)] = aggregated_results[question_text]['data'].get(str(answer), 0) + 1
                        except (ValueError, IndexError):
                            pass
                elif question_type == 'multiple_choice':
                    if answer:
                        if isinstance(answer, list):
                            for opt in answer:
                                aggregated_results[question_text]['data'][str(opt)] = aggregated_results[question_text]['data'].get(str(opt), 0) + 1
                        else:
                            aggregated_results[question_text]['data'][str(answer)] = aggregated_results[question_text]['data'].get(str(answer), 0) + 1
                elif question_type == 'text':
                    if answer:
                        if 'comments' not in aggregated_results[question_text]['data']:
                            aggregated_results[question_text]['data']['comments'] = []
                        aggregated_results[question_text]['data']['comments'].append(answer)

            # Aggregate general comments
            general_comment = eval_row.get('general_comment') # Use the alias from query
            if general_comment:
                if 'General Comments' not in aggregated_results:
                    aggregated_results['General Comments'] = {"type": "text", "data": {"comments": []}}
                aggregated_results['General Comments']['data']['comments'].append(general_comment)

        # Add average score for rating questions
        for question_text in rating_sums:
            avg = rating_sums[question_text] / rating_counts[question_text] if rating_counts[question_text] > 0 else 0
            aggregated_results[question_text]['average'] = round(avg, 2)

        return {
            "summary": "Report generated successfully.",
            "total_submissions": total_submissions,
            "report_data": aggregated_results
        }

    def get_faculty_evaluation_scores(self, faculty_id):
        """
        Retrieves aggregated rating scores for a specific faculty member across courses for comparison.
        """
        query = """
        SELECT
            e.feedback,
            et.questions_set,
            e.date AS evaluation_date,
            e.course_code,
            c.name AS course_name
        FROM evaluations e
        JOIN evaluation_templates et ON e.template_id = et.id
        JOIN courses c ON e.course_code = c.course_code
        JOIN course_faculty cf ON e.course_code = cf.course_code
        WHERE cf.faculty_id = %s;
        """
        evaluations_for_faculty = self.db.fetch_data(query, (faculty_id,), fetch_all=True)

        if not evaluations_for_faculty:
            return []

        faculty_evaluations_summary = []

        for eval_row in evaluations_for_faculty:
            feedback_json = eval_row['feedback']
            questions_set_json = eval_row['questions_set']

            try:
                feedback = json.loads(feedback_json)
                questions_set = json.loads(questions_set_json)
            except json.JSONDecodeError:
                continue

            questions_list = questions_set.get('questions', [])
            total_rating_sum = 0
            rating_question_count = 0
            course_name = eval_row['course_name']
            evaluation_date = eval_row['evaluation_date']

            for question in questions_list:
                question_text = question['text']
                question_type = question['type']
                answer = feedback.get(question_text)

                if question_type == 'rating' and answer:
                    try:
                        # Extract the numerical rating from "X (Text)"
                        rating_value = int(str(answer).split(' ')[0])
                        total_rating_sum += rating_value
                        rating_question_count += 1
                    except (ValueError, IndexError):
                        pass

            average_rating = total_rating_sum / rating_question_count if rating_question_count > 0 else 0

            faculty_evaluations_summary.append({
                "course_code": eval_row['course_code'],
                "course_name": course_name,
                "evaluation_date": evaluation_date.strftime("%Y-%m-%d"), # Format date for display
                "average_rating": f"{average_rating:.2f}",
                "num_rating_questions": rating_question_count
            })
        return faculty_evaluations_summary

    def export_report_data(self, report_data, file_type):
        """
        Exports aggregated report data to CSV, Excel, or PDF.
        """
        if not report_data:
            messagebox.showwarning("Export Warning", "No data to export.")
            return

        # Prepare data for DataFrame
        data_for_df = []
        for question_text, q_data in report_data.items():
            row = {"Question": question_text, "Type": q_data['type']}
            if q_data['type'] in ['rating', 'multiple_choice']:
                for option, count in q_data['data'].items():
                    row[f"Response: {option}"] = count
            elif q_data['type'] == 'text':
                row["Comments"] = "\n".join(q_data['data'].get('comments', []))
            data_for_df.append(row)

        df = pd.DataFrame(data_for_df)

        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{file_type}",
            filetypes=[(f"{file_type.upper()} files", f"*.{file_type}"), ("All files", "*.*")]
        )

        if not file_path:
            return "Export cancelled."

        try:
            if file_type == "csv":
                df.to_csv(file_path, index=False, encoding='utf-8')
            elif file_type == "xlsx":
                df.to_excel(file_path, index=False, engine='openpyxl')
            elif file_type == "pdf":
                # PDF export is more complex, often requires external libraries like ReportLab or FPDF
                # For simplicity, we'll suggest CSV/Excel for immediate implementation or print a message.
                messagebox.showerror("Export Error", "PDF export requires additional libraries and complex formatting. Please choose CSV or XLSX.")
                return "PDF export not fully implemented."
            else:
                return f"Unsupported file type: {file_type}"

            return f"Report exported successfully to {os.path.basename(file_path)}"
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")
            return f"Error during export: {e}"

    def generate_question_graphs(self, report_data, output_dir="report_graphs"):
        """
        Generates bar or pie charts for each question in the report_data and saves them as images.
        Returns a dict mapping question_text to image file paths.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        image_paths = {}
        for question_text, qdata in report_data.items():
            qtype = qdata.get("type")
            data = qdata.get("data", {})
            if qtype in ["rating", "multiple_choice"] and data:
                labels = list(data.keys())
                values = list(data.values())
                plt.figure(figsize=(6, 4))
                if qtype == "rating" and len(labels) > 1:
                    plt.bar(labels, values, color="#1976d2")
                    plt.title(f"{question_text} (Ratings)")
                    plt.xlabel("Rating")
                    plt.ylabel("Count")
                elif qtype == "multiple_choice":
                    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
                    plt.title(f"{question_text} (MCQ)")
                else:
                    continue
                img_path = os.path.join(output_dir, f"{question_text[:30].replace(' ', '_')}.png")
                plt.tight_layout()
                plt.savefig(img_path)
                plt.close()
                image_paths[question_text] = img_path
        return image_paths