"""
Campaign Awareness Report Routes
API endpoints for generating and viewing campaign awareness reports
"""

from flask import Blueprint, request, jsonify, send_file
from services.campaign_report_service import CampaignReportService
from models import Campaign
from datetime import datetime
import io
import os

bp = Blueprint('campaign_reports', __name__, url_prefix='/api/campaigns')


@bp.route('/<campaign_id>/report', methods=['GET'])
def get_campaign_report(campaign_id):
    """
    Generate and return awareness report for a campaign

    Returns comprehensive analysis including:
    - Campaign overview
    - Company-level awareness summary
    - Individual employee results
    - Department risk breakdown
    - Identified security gaps
    """
    try:
        # Verify campaign exists
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404

        # Generate report
        report = CampaignReportService.generate_report(campaign_id)

        if 'error' in report:
            return jsonify(report), 400

        return jsonify(report), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<campaign_id>/report/summary', methods=['GET'])
def get_campaign_report_summary(campaign_id):
    """Get quick summary of campaign report (for dashboard/list view)"""
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404

        # Generate full report
        report = CampaignReportService.generate_report(campaign_id)

        if 'error' in report:
            return jsonify(report), 400

        # Return summary only
        summary = {
            'campaign_id': campaign_id,
            'campaign_name': report['overview']['campaign_name'],
            'awareness_score': report['awareness_summary']['awareness_score'],
            'awareness_level': report['awareness_summary']['awareness_level'],
            'level_color': report['awareness_summary']['level_color'],
            'total_employees': report['awareness_summary']['total_employees'],
            'clicked_percent': report['awareness_summary']['clicked_percent'],
            'submitted_credentials_count': report['awareness_summary']['submitted_credentials_count'],
            'overall_risk_level': report['security_gaps']['overall_risk_level'],
            'high_risk_departments': len([d for d in report['department_breakdown'] if d['risk_level'] in ['critical', 'high']]),
            'generated_at': report['generated_at']
        }

        return jsonify(summary), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<campaign_id>/report/export', methods=['GET'])
def export_campaign_report(campaign_id):
    """
    Export campaign report in various formats (JSON, PDF)
    """
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404

        # Get export format (default: json)
        export_format = request.args.get('format', 'json').lower()

        # Generate report
        report = CampaignReportService.generate_report(campaign_id)

        if 'error' in report:
            return jsonify(report), 400

        if export_format == 'json':
            return jsonify(report), 200

        elif export_format == 'pdf':
            # Generate professional PDF report from structured data
            try:
                from xhtml2pdf import pisa

                overview = report['overview']
                summary = report['awareness_summary']
                gaps = report['security_gaps']
                departments = report['department_breakdown'][:5]
                employees = report['employee_results']

                # Helper function for risk badge styling
                def get_risk_badge(level):
                    colors = {
                        'critical': '#dc2626',
                        'high': '#f97316',
                        'medium': '#f59e0b',
                        'low': '#10b981'
                    }
                    color = colors.get(level.lower(), '#6b7280')
                    return f'<span style="background:{color};color:white;padding:2px 8px;font-size:9pt;font-weight:bold;border-radius:3px;">{level.upper()}</span>'

                # Build HTML content
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Security Awareness Campaign Report</title>
    <style>
        @page {{ size: A4; margin: 25mm; }}
        body {{ font-family: 'Helvetica', 'Arial', sans-serif; font-size: 11pt; line-height: 1.4; color: #1f2937; }}

        /* Header */
        .report-header {{ text-align: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #2563eb; }}
        .report-title {{ font-size: 24pt; font-weight: bold; color: #1e40af; margin: 8px 0; }}
        .campaign-name {{ font-size: 14pt; color: #4b5563; margin: 5px 0; font-style: italic; }}
        .report-date {{ font-size: 9pt; color: #6b7280; margin-top: 5px; }}

        /* Sections */
        h2 {{ font-size: 14pt; font-weight: bold; color: #1f2937; margin: 25px 0 10px 0; padding-bottom: 4px; border-bottom: 2px solid #e5e7eb; }}
        h2:first-of-type {{ margin-top: 15px; }}
        h3 {{ font-size: 12pt; font-weight: bold; color: #374151; margin: 15px 0 8px 0; }}
        p {{ margin: 5px 0; }}

        /* Score Display */
        .score-box {{ text-align: center; background: #eff6ff; border: 2px solid #2563eb; padding: 12px; margin: 10px 0; }}
        .score-number {{ font-size: 36pt; font-weight: bold; color: #1e40af; }}
        .score-label {{ font-size: 11pt; color: #6b7280; margin-top: 3px; }}

        /* Behavior List */
        .behavior-list {{ margin: 8px 0; }}
        .behavior-item {{ padding: 4px 0; border-bottom: 1px solid #e5e7eb; }}
        .behavior-label {{ display: inline-block; width: 160px; font-weight: bold; color: #374151; }}

        /* Tables */
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background: #1e40af; color: white; font-weight: bold; text-align: left; padding: 8px; font-size: 10pt; }}
        td {{ padding: 6px 8px; border-bottom: 1px solid #e5e7eb; font-size: 9pt; }}
        tr:nth-child(even) {{ background: #f9fafb; }}

        /* Security Gaps */
        .gap-item {{ margin: 8px 0; padding: 8px; border-left: 4px solid #f59e0b; background: #fef3c7; }}
        .gap-title {{ font-weight: bold; color: #92400e; margin-bottom: 3px; }}
        .gap-desc {{ font-size: 9pt; color: #78350f; }}

        /* Page Break */
        .page-break {{ page-break-before: always; }}

        /* Footer */
        .footer {{ margin-top: 20px; padding-top: 10px; border-top: 2px solid #e5e7eb; text-align: center; font-size: 8pt; color: #6b7280; }}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="report-header">
        <div style="font-size:11pt;font-weight:bold;color:#2563eb;">PhishVision Security Awareness Platform</div>
        <div class="report-title">Security Awareness Campaign Report</div>
        <div class="campaign-name">{overview['campaign_name']}</div>
        <div class="report-date">Generated on {datetime.fromisoformat(report['generated_at']).strftime('%B %d, %Y at %I:%M %p')}</div>
    </div>

    <!-- Campaign Overview -->
    <h2>Campaign Overview</h2>
    <p><strong>Campaign Type:</strong> {overview['campaign_type']}</p>
    <p><strong>Status:</strong> {overview['status']}</p>
    <p><strong>Total Targets:</strong> {overview['total_targets']} employees</p>
    <p><strong>Open Rate:</strong> {overview['open_rate']}%</p>
    <p><strong>Click Rate:</strong> {overview['click_rate']}%</p>

    <!-- Company Awareness Score -->
    <h2>Company-Level Awareness Summary</h2>
    <div class="score-box">
        <div class="score-number">{summary['awareness_score']}/100</div>
        <div class="score-label">Awareness Level: <strong>{summary['awareness_level']}</strong></div>
    </div>

    <h3>Employee Behavior Breakdown</h3>
    <div class="behavior-list">
        <div class="behavior-item">
            <span class="behavior-label">No Interaction:</span>
            <span>{summary['no_interaction_count']} ({summary['no_interaction_percent']}%)</span>
        </div>
        <div class="behavior-item">
            <span class="behavior-label">Opened Only:</span>
            <span>{summary['opened_only_count']} ({summary['opened_only_percent']}%)</span>
        </div>
        <div class="behavior-item">
            <span class="behavior-label">Clicked Link:</span>
            <span>{summary['clicked_count']} ({summary['clicked_percent']}%)</span>
        </div>
        <div class="behavior-item">
            <span class="behavior-label">Submitted Credentials:</span>
            <span>{summary['submitted_credentials_count']} employees</span>
        </div>
    </div>

    <!-- Department Risk Breakdown -->
    <h2>Department Risk Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Department</th>
                <th>Employees</th>
                <th>Click Rate</th>
                <th>Risk Level</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
            <tr>
                <td>{dept['department']}</td>
                <td>{dept['total_employees']}</td>
                <td>{dept['click_rate']}%</td>
                <td>{get_risk_badge(dept['risk_level'])}</td>
            </tr>
            ''' for dept in departments])}
        </tbody>
    </table>

    <!-- Individual Employee Results -->
    <h2>Individual Employee Results</h2>
    <table>
        <thead>
            <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Outcome</th>
                <th>Risk Level</th>
                <th>Training</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
            <tr>
                <td>{emp['name']}</td>
                <td>{emp['department']}</td>
                <td>{emp.get('outcome_label', emp.get('outcome', 'Unknown'))}</td>
                <td>{get_risk_badge(emp['risk_level'])}</td>
                <td>{'Yes' if emp.get('training_recommended', False) else 'No'}</td>
            </tr>
            ''' for emp in employees[:20]])}
        </tbody>
    </table>

    <!-- Identified Security Gaps -->
    <h2>Identified Security Gaps</h2>
    <p>{gaps.get('summary', 'Security gap analysis completed.')}</p>

    <h3>Detailed Findings & Recommendations</h3>
    {''.join([f'''
    <div class="gap-item">
        <div class="gap-title">{gap['category']}: {gap['finding']}</div>
        <div class="gap-desc"><strong>Recommendation:</strong> {gap['recommendation']}</div>
    </div>
    ''' for gap in gaps.get('gaps', [])[:5]])}

    <!-- Footer -->
    <div class="footer">
        Generated by PhishVision Security Awareness Platform<br>
        Confidential - For Internal Use Only
    </div>
</body>
</html>
"""

                # Generate PDF from HTML using xhtml2pdf
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

        else:
            return jsonify({'error': f'Export format "{export_format}" not supported. Use: json, pdf'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
