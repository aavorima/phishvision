# This is the clean PDF generation code to replace in campaign_report_routes.py

# Put this code after line 100 "elif export_format == 'pdf':"

            # Generate AI-powered professional PDF report
            try:
                from xhtml2pdf import pisa
                from services.gemini_analyzer import GeminiAnalyzer
                import json
                import re

                overview = report['overview']
                summary = report['awareness_summary']
                gaps = report['security_gaps']

                # Find highest risk department
                highest_risk_dept = max(report['department_breakdown'][:10], key=lambda d: d['click_rate']) if report['department_breakdown'] else None

                # Prepare data for AI
                report_data = {
                    'campaign_name': overview['campaign_name'],
                    'campaign_type': overview['campaign_type'],
                    'total_targets': overview['total_targets'],
                    'open_rate': overview['open_rate'],
                    'click_rate': overview['click_rate'],
                    'awareness_score': summary['awareness_score'],
                    'awareness_level': summary['awareness_level'],
                    'clicked_percent': summary['clicked_percent'],
                    'submitted_credentials_count': summary['submitted_credentials_count'],
                    'highest_risk_department': highest_risk_dept['department'] if highest_risk_dept else 'N/A',
                    'highest_risk_click_rate': highest_risk_dept['click_rate'] if highest_risk_dept else 0,
                    'high_risk_employees_count': len([e for e in report['employee_results'] if e['risk_level'] in ['critical', 'high']])
                }

                # Generate professional report using AI
                gemini = GeminiAnalyzer()
                ai_prompt = f"""You are a cybersecurity analyst writing an executive security awareness campaign report.

Based on this phishing simulation data, write a professional, well-structured report:

**Data:**
{json.dumps(report_data, indent=2)}

**Instructions:**
Write a comprehensive security report with these sections:
1. Executive Summary (2-3 paragraphs)
2. Campaign Overview (brief)
3. Performance Analysis (discuss awareness score, behavior patterns, click rates)
4. Risk Assessment (discuss high-risk departments and vulnerabilities)
5. Recommendations (4-5 specific, actionable items)
6. Conclusion (1 paragraph with next steps)

**Tone:** Professional, objective, data-driven
**Format:** Use section headers. Write in complete paragraphs.
**Style:** Like a professional security consulting report

Write the full report now:"""

                ai_response = gemini.analyze_email(
                    from_address="report@phishvision.com",
                    subject="Security Report Generation",
                    body=ai_prompt,
                    headers=""
                )

                # Extract AI-generated report text
                ai_report_text = ai_response.get('explanation', 'Report generation failed.')

                # Convert to paragraphs
                paragraphs = [p.strip() for p in ai_report_text.split('\n\n') if p.strip()]

                report_body = ''
                for para in paragraphs:
                    # Check if header
                    if ':' in para and len(para) < 100:
                        report_body += f'<h2>{para.replace(":", "").strip()}</h2>\n'
                    else:
                        report_body += f'<p>{para}</p>\n'

                # Build HTML
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PhishVision Security Awareness Report</title>
    <style>
        @page {{ margin: 1in; }}
        body {{
            font-family: 'Georgia', serif;
            font-size: 11pt;
            line-height: 1.7;
            color: #000;
        }}
        .doc-header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #000;
        }}
        .company {{ font-size: 12pt; font-weight: bold; color: #2563eb; }}
        .title {{ font-size: 20pt; font-weight: bold; margin: 10px 0; }}
        .subtitle {{ font-size: 12pt; color: #555; }}
        .date {{ font-size: 10pt; color: #666; margin-top: 5px; }}
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            margin: 25px 0 10px 0;
        }}
        p {{ margin: 10px 0; text-align: justify; }}
    </style>
</head>
<body>
    <div class="doc-header">
        <div class="company">PhishVision</div>
        <div class="title">Security Awareness Campaign Report</div>
        <div class="subtitle">{overview['campaign_name']}</div>
        <div class="date">Generated: {datetime.fromisoformat(report['generated_at']).strftime('%B %d, %Y')}</div>
    </div>
    {report_body}
</body>
</html>"""

                # Generate PDF
                pdf_file = io.BytesIO()
                pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

                if pisa_status.err:
                    return jsonify({'error': 'Error generating PDF'}), 500

                pdf_file.seek(0)

                # Generate filename
                campaign_name_clean = "".join(c for c in campaign.name if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"Campaign_Report_{campaign_name_clean}_{datetime.now().strftime('%Y%m%d')}.pdf"

                # Return PDF file
                return send_file(
                    pdf_file,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename
                )

            except ImportError:
                return jsonify({'error': 'xhtml2pdf library not installed. Run: pip install xhtml2pdf'}), 500
            except Exception as pdf_error:
                import traceback
                return jsonify({'error': f'Error generating PDF document: {str(pdf_error)}', 'traceback': traceback.format_exc()}), 500
