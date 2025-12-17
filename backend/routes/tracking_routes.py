from flask import Blueprint, request, send_file, send_from_directory, render_template_string
from database import db
from models import CampaignTarget, ScheduledCampaign, Employee, Campaign
from datetime import datetime
import io
import os

bp = Blueprint('tracking', __name__, url_prefix='/api/track')

# Path to static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')

# 1x1 transparent pixel for tracking email opens
TRACKING_PIXEL = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'

# Email phishing training page HTML
EMAIL_TRAINING_PAGE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Email Phishing Training</title>
  <style>
    :root{
      --bg:#0b1020;
      --panel:#0f172a;
      --panel2:#0b1222;
      --text:#e5e7eb;
      --muted:#a3adc2;
      --border:rgba(255,255,255,.08);
      --brand:#22c55e;
      --warn:#f59e0b;
      --danger:#ef4444;
      --link:#60a5fa;
      --shadow:0 18px 50px rgba(0,0,0,.45);
      --r:18px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      background: radial-gradient(900px 450px at 20% 0%, rgba(34,197,94,.25), transparent),
                  radial-gradient(900px 450px at 90% 10%, rgba(96,165,250,.18), transparent),
                  var(--bg);
      color:var(--text);
    }
    .wrap{max-width:980px;margin:0 auto;padding:18px}
    .topbar{
      display:flex;align-items:center;justify-content:space-between;
      padding:14px 16px;border:1px solid var(--border);
      background:rgba(255,255,255,.03);border-radius:14px;
    }
    .brand{
      display:flex;align-items:center;gap:10px;font-weight:900;letter-spacing:.2px
    }
    .badge{
      font-size:12px;font-weight:800;
      color:#001b0e;background:rgba(34,197,94,.9);
      padding:6px 10px;border-radius:999px;
    }
    .grid{
      display:grid;gap:14px;margin-top:14px;
      grid-template-columns: 1.2fr .8fr;
    }
    @media (max-width: 900px){ .grid{grid-template-columns:1fr} }
    .card{
      border:1px solid var(--border);
      background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border-radius:var(--r);
      box-shadow:var(--shadow);
      overflow:hidden;
    }
    .cardHead{
      padding:14px 16px;border-bottom:1px solid var(--border);
      display:flex;justify-content:space-between;align-items:center;gap:10px
    }
    .title{font-size:18px;font-weight:900;margin:0}
    .sub{font-size:13px;color:var(--muted);margin:0}
    .cardBody{padding:16px}
    .kpiRow{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 2px}
    .kpi{
      padding:10px 12px;border:1px solid var(--border);
      border-radius:14px;background:rgba(255,255,255,.03);
      font-size:13px;color:var(--muted)
    }
    .kpi b{color:var(--text)}
    .mailShell{
      background:var(--panel2);
      border:1px solid var(--border);
      border-radius:16px;
      overflow:hidden;
    }
    .mailTop{
      display:flex;align-items:center;gap:10px;
      padding:12px 14px;border-bottom:1px solid var(--border);
      background:rgba(255,255,255,.02);
    }
    .dot{width:10px;height:10px;border-radius:50%}
    .dot.r{background:#ef4444}
    .dot.y{background:#f59e0b}
    .dot.g{background:#22c55e}
    .mailMeta{padding:14px;border-bottom:1px solid var(--border)}
    .row{display:flex;gap:10px;flex-wrap:wrap}
    .pill{
      font-size:12px;font-weight:700;color:rgba(255,255,255,.8);
      border:1px solid var(--border);background:rgba(255,255,255,.03);
      padding:6px 10px;border-radius:999px;
    }
    .mailSubject{font-size:18px;font-weight:900;margin:10px 0 6px}
    .mailFrom{color:var(--muted);font-size:13px}
    .mailBody{padding:14px;color:rgba(255,255,255,.85);line-height:1.55}
    .phishLink{
      display:inline-block;margin-top:10px;
      color:var(--link);text-decoration:underline;font-weight:800;
      word-break:break-all;
    }
    h3{
      margin:0 0 8px;font-size:15px;font-weight:900;
      color:rgba(255,255,255,.92);
    }
    ul{margin:10px 0 0 18px;color:var(--muted)}
    li{margin:8px 0}
    .warnBox{
      margin-top:12px;
      background:rgba(245,158,11,.12);
      border:1px solid rgba(245,158,11,.25);
      border-radius:16px;padding:12px 14px;color:rgba(255,255,255,.88);
    }
    .dangerTitle{color:#fb7185;font-weight:900;margin-top:12px}
    .actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
    button{
      border:none;cursor:pointer;border-radius:14px;
      padding:12px 14px;font-weight:900;font-size:14px;
    }
    .primary{
      background:linear-gradient(90deg, rgba(34,197,94,1), rgba(96,165,250,1));
      color:#03120a;opacity:.6;
    }
    .primary.enabled{opacity:1}
    .ghost{
      background:rgba(255,255,255,.06);
      border:1px solid var(--border);
      color:rgba(255,255,255,.9);
    }
    .checkRow{display:flex;gap:10px;align-items:flex-start;margin-top:10px;color:var(--muted)}
    input[type="checkbox"]{width:18px;height:18px;margin-top:2px;accent-color:var(--brand)}
    .success{
      display:none;margin-top:12px;
      background:rgba(34,197,94,.12);
      border:1px solid rgba(34,197,94,.25);
      color:rgba(220,255,235,.95);
      padding:12px 14px;border-radius:14px;font-weight:800;
    }
    .note{margin-top:12px;font-size:12px;color:rgba(255,255,255,.6)}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div class="brand">
        <span class="badge">SIMULATION</span>
        <div>
          <div style="font-weight:900">Email Phishing Training</div>
          <div style="font-size:12px;color:var(--muted)">You clicked a link in a simulated phishing email</div>
        </div>
      </div>
    </div>
    <div class="grid">
      <div class="card">
        <div class="cardHead">
          <div>
            <p class="title">What happened</p>
            <p class="sub">Review the email you interacted with</p>
          </div>
          <span class="pill">Vector: Email · Outcome: Link Click</span>
        </div>
        <div class="cardBody">
          <div class="mailShell">
            <div class="mailTop">
              <div class="dot r"></div><div class="dot y"></div><div class="dot g"></div>
              <div style="font-size:12px;color:var(--muted);font-weight:700">Mail Viewer</div>
            </div>
            <div class="mailMeta">
              <div class="row">
                <span class="pill">From: {{from_display}}</span>
                <span class="pill">To: {{employee_email}}</span>
                <span class="pill">Dept: {{department}}</span>
              </div>
              <div class="mailSubject">{{email_subject}}</div>
              <div class="mailFrom">Reply-To: <b>{{reply_to}}</b> · Domain shown: <b>{{from_domain}}</b></div>
            </div>
            <div class="mailBody">
              Hi {{employee_name}},<br/><br/>
              {{email_body_preview}}<br/>
              <a class="phishLink" href="#">{{clicked_url}}</a><br/><br/>
              Thanks,<br/>
              {{signature_name}}
            </div>
          </div>
          <div class="warnBox">
            <b>Why this matters:</b> One phishing click can lead to malware installs, credential theft, or account compromise.
            Attackers often use urgency + official-looking branding to bypass attention.
          </div>
        </div>
      </div>
      <div class="card">
        <div class="cardHead">
          <div>
            <p class="title">How to spot it next time</p>
            <p class="sub">Targeted tips based on this exact email</p>
          </div>
        </div>
        <div class="cardBody">
          <h3>What went wrong in your case</h3>
          <ul>
            <li>The message pushed <b>urgent action</b> (pressure to act fast).</li>
            <li>The sender details could be <b>spoofed</b> (lookalike name/domain).</li>
            <li>The link destination was not verified before clicking.</li>
          </ul>
          <div class="dangerTitle">Red flags to watch</div>
          <ul>
            <li>Unexpected password resets, invoice/payment requests, "account locked" warnings</li>
            <li>Suspicious domains (extra letters, strange TLDs), mismatched Reply-To</li>
            <li>Links that don't match the organization's official domain</li>
            <li>Attachments you didn't request</li>
          </ul>
          <h3 style="margin-top:14px">Safe actions</h3>
          <ul>
            <li>Hover (desktop) or long-press (mobile) to preview links before opening</li>
            <li>Verify via a trusted channel (call IT, open official site manually)</li>
            <li>Report suspicious emails using your company's process</li>
          </ul>
          <div class="checkRow">
            <input id="ack" type="checkbox" />
            <div>
              <div><b>I understand how to identify phishing emails before clicking</b></div>
              <div style="font-size:12px;color:rgba(255,255,255,.6)">Check to enable completion.</div>
            </div>
          </div>
          <div class="actions">
            <button id="completeBtn" class="primary" disabled>Mark Training as Completed</button>
            <button class="ghost" onclick="window.print()">Print / Save PDF</button>
          </div>
          <div id="success" class="success">
            ✅ Completed. You may be re-tested with a similar email to measure improvement.
          </div>
          <div class="note">
            Re-measurement is part of the program: we test again to confirm awareness improved (close the gap).
          </div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const ack = document.getElementById("ack");
    const btn = document.getElementById("completeBtn");
    const success = document.getElementById("success");
    ack.addEventListener("change", () => {
      btn.disabled = !ack.checked;
      btn.classList.toggle("enabled", ack.checked);
    });
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "Recording...";
      try {
        const response = await fetch("/api/training/complete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            employeeId: "{{employee_id}}",
            programId: "{{program_id}}",
            campaignId: "{{campaign_id}}",
            module: "email_link_click",
            completedAt: new Date().toISOString()
          })
        });

        if (response.ok) {
          success.style.display = "block";
          btn.textContent = "Completed";
        } else {
          const error = await response.json().catch(() => ({}));
          alert("Failed to record completion: " + (error.error || response.statusText));
          btn.disabled = false;
          btn.textContent = "Mark Training as Completed";
        }
      } catch (e) {
        console.error("Could not record completion:", e);
        alert("Network error - please check your connection and try again");
        btn.disabled = false;
        btn.textContent = "Mark Training as Completed";
      }
    });
  </script>
</body>
</html>
'''


def _detect_device_type(user_agent: str) -> str:
    """Detect device type from user agent string"""
    ua_lower = user_agent.lower()
    if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
        return 'mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        return 'tablet'
    return 'desktop'


def _update_vulnerability_profile(tracking_token: str, interaction_type: str, device_type: str = None):
    """Update vulnerability profile if this is from a campaign program"""
    try:
        # Check if this target is linked to a scheduled campaign (profiling program)
        target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()
        if not target:
            return

        scheduled = ScheduledCampaign.query.filter_by(target_id=target.id).first()
        if not scheduled:
            return  # Not a profiling program campaign

        # Import here to avoid circular imports
        from services.campaign_program_service import CampaignProgramService
        program_service = CampaignProgramService()

        program_service.record_interaction(
            tracking_token=tracking_token,
            interaction_type=interaction_type,
            device_type=device_type
        )
    except Exception as e:
        # Log but don't fail the tracking
        print(f"[TRACKING] Error updating vulnerability profile: {e}")


@bp.route('/open/<tracking_token>')
def track_open(tracking_token):
    """Track email open via pixel"""
    target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()

    if target and not target.opened_at:
        target.opened_at = datetime.utcnow()
        target.ip_address = request.remote_addr
        target.user_agent = request.headers.get('User-Agent', '')

        # Update HVS score for email open
        employee = Employee.query.filter_by(email=target.email).first()
        if employee:
            employee.update_hvs('opened_email')

        db.session.commit()

        # Update vulnerability profile if from a program
        device_type = _detect_device_type(target.user_agent or '')
        _update_vulnerability_profile(tracking_token, 'open', device_type)

    # Return 1x1 transparent GIF
    return send_file(
        io.BytesIO(TRACKING_PIXEL),
        mimetype='image/gif',
        as_attachment=False,
        download_name='pixel.gif'
    )

@bp.route('/click/<tracking_token>')
def track_click(tracking_token):
    """Track link click and show training page"""
    target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()

    if not target:
        return "Link expired or invalid", 404

    # Record click (clicking implies opening, so set both)
    if not target.clicked_at:
        target.clicked_at = datetime.utcnow()

    # If they clicked, they must have opened the email
    if not target.opened_at:
        target.opened_at = datetime.utcnow()

    # Update IP and user agent if not already set
    if not target.ip_address:
        target.ip_address = request.remote_addr
        target.user_agent = request.headers.get('User-Agent', '')

    # Update HVS score for link click
    employee = Employee.query.filter_by(email=target.email).first()
    if employee:
        employee.update_hvs('clicked_link')

    db.session.commit()

    # Update vulnerability profile if from a program
    device_type = _detect_device_type(target.user_agent or request.headers.get('User-Agent', ''))
    _update_vulnerability_profile(tracking_token, 'click', device_type)

    # Get campaign details for the training page
    campaign = target.campaign
    employee_name = target.name or (target.email.split('@')[0] if target.email else 'Employee')

    # Use safe defaults - Campaign model has limited fields
    from_display = "Security Team"
    reply_to = "security@company.com"
    from_domain = "company.com"
    email_body_preview = "This is a simulated phishing email designed to test your awareness."
    signature_name = "Security Team"

    # Serve the training page with employee context
    return render_template_string(
        EMAIL_TRAINING_PAGE,
        employee_name=employee_name,
        employee_email=target.email or 'unknown@example.com',
        employee_id=target.id,
        department=employee.department if employee else 'Unknown',
        from_display=from_display,
        reply_to=reply_to,
        from_domain=from_domain,
        email_subject=campaign.subject or 'Phishing Simulation',
        email_body_preview=email_body_preview,
        signature_name=signature_name,
        clicked_url=request.url,
        program_id=campaign.program_id or '',
        campaign_id=campaign.id
    )


@bp.route('/c/<tracking_token>')
def track_click_short(tracking_token):
    """Short URL for click tracking - redirects to main click handler"""
    return track_click(tracking_token)

@bp.route('/stats/<campaign_id>')
def get_campaign_stats(campaign_id):
    """Get tracking stats for a campaign"""
    from models import Campaign
    campaign = Campaign.query.get_or_404(campaign_id)

    targets = campaign.targets
    total = len(targets)
    opened = sum(1 for t in targets if t.opened_at)
    clicked = sum(1 for t in targets if t.clicked_at)

    return {
        'campaign_id': campaign_id,
        'total_sent': total,
        'opened': opened,
        'clicked': clicked,
        'open_rate': round((opened / total * 100) if total > 0 else 0, 2),
        'click_rate': round((clicked / total * 100) if total > 0 else 0, 2)
    }
