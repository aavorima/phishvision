import os

def get_template(template_type, tracking_token, base_url):
    """
    Get HTML email template based on type
    """
    templates = {
        'bank_alert': generate_bank_alert_template(tracking_token, base_url),
        'package_delivery': generate_package_delivery_template(tracking_token, base_url),
        'trendyol_discount': generate_trendyol_discount_template(tracking_token, base_url),
        'trendyol_delivery': generate_trendyol_delivery_template(tracking_token, base_url),
        'birbank_cashback': generate_birbank_cashback_template(tracking_token, base_url),
        'akm_exam_invite': generate_akm_exam_invite_template(tracking_token, base_url),
        'akm_interview_invite': generate_akm_interview_invite_template(tracking_token, base_url),
        'akm_exam_invite_az': generate_akm_exam_invite_az_template(tracking_token, base_url),
        'akm_interview_invite_az': generate_akm_interview_invite_az_template(tracking_token, base_url),
        'akm_careers': generate_akm_careers_template(tracking_token, base_url),
        'pulse_traffic': generate_pulse_traffic_template(tracking_token, base_url),
        'pulse_demo': generate_pulse_demo_template(tracking_token, base_url),
        'coinspaid': generate_coinspaid_template(tracking_token, base_url)
    }

    return templates.get(template_type, templates['bank_alert'])

def generate_bank_alert_template(tracking_token, base_url):
    """
    Template 1: Fake bank security alert
    """
    return {
        'subject': '🔒 Urgent: Suspicious Activity Detected on Your Account',
        'html': f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ background-color: #003d82; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
        .alert {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .button {{ display: inline-block; background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        .urgent {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 SecureBank Security Center</h1>
        </div>

        <h2 class="urgent">⚠️ Immediate Action Required</h2>

        <div class="alert">
            <strong>Security Alert:</strong> We detected unusual login attempts from an unrecognized device in Nigeria.
        </div>

        <p>Dear Valued Customer,</p>

        <p>We have detected suspicious activity on your account. For your protection, we have temporarily limited access to your account.</p>

        <p><strong>Suspicious Activity Details:</strong></p>
        <ul>
            <li>Location: Lagos, Nigeria</li>
            <li>Device: Unknown Android Device</li>
            <li>Time: Today at 3:42 AM</li>
            <li>Failed login attempts: 5</li>
        </ul>

        <p class="urgent">Your account will be permanently locked in 24 hours unless you verify your identity.</p>

        <center>
            <a href="{base_url}/api/track/click/{tracking_token}" class="button">
                Verify My Account Now
            </a>
        </center>

        <p>If you don't recognize this activity, please click the button above immediately to secure your account.</p>

        <div class="footer">
            <p>SecureBank Security Team<br>
            This is an automated security alert. Please do not reply to this email.<br>
            © 2024 SecureBank. All rights reserved.</p>
        </div>
    </div>

    <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_package_delivery_template(tracking_token, base_url):
    """
    Template 2: Fake package delivery notification
    """
    return {
        'subject': '📦 Your Package Delivery Failed - Action Required',
        'html': f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ background-color: #ff9900; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
        .tracking {{ background-color: #f0f0f0; padding: 15px; margin: 20px 0; border-radius: 5px; font-family: monospace; }}
        .button {{ display: inline-block; background-color: #ff9900; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        .warning {{ color: #dc3545; font-weight: bold; }}
        .package-info {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📦 FastShip Delivery Service</h1>
        </div>

        <h2>Delivery Attempt Failed</h2>

        <p>Dear Customer,</p>

        <p>We attempted to deliver your package today, but no one was available to receive it at the delivery address.</p>

        <div class="package-info">
            <strong>Package Information:</strong><br>
            <strong>Tracking Number:</strong> <span class="tracking">FS-{tracking_token[:8].upper()}</span><br>
            <strong>Delivery Attempt:</strong> Today at 2:15 PM<br>
            <strong>Warehouse Location:</strong> Distribution Center #45<br>
            <strong>Package Weight:</strong> 2.3 lbs
        </div>

        <p class="warning">⚠️ Important: Your package will be returned to sender if not claimed within 48 hours.</p>

        <p>To reschedule your delivery or arrange for pickup, please confirm your delivery preferences and pay the small redelivery fee of $2.99.</p>

        <center>
            <a href="{base_url}/api/track/click/{tracking_token}" class="button">
                Reschedule Delivery Now
            </a>
        </center>

        <p>You can also track your package status using the tracking number above.</p>

        <div class="footer">
            <p>FastShip Delivery Service<br>
            Customer Support: 1-800-FAST-SHIP<br>
            © 2024 FastShip. All rights reserved.</p>
        </div>
    </div>

    <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_trendyol_discount_template(tracking_token, base_url):
    """
    Template 3: Trendyol discount coupon (Azerbaijani)
    """
    return {
        'subject': '🎁 Trendyol Endirim Kuponu - Müddət Bitmək Üzrə!',
        'html': f'''
<!DOCTYPE html>
<html lang="az">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trendyol Endirim Kuponu</title>
</head>
<body style="margin:0; padding:0; background:#f6f6f6; font-family:Arial, sans-serif;">
  <table width="100%" cellspacing="0" cellpadding="0" bgcolor="#f6f6f6">
    <tr>
      <td align="center" style="padding:20px;">
        <table width="600" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="border-radius:10px; padding:20px;">

          <!-- Header -->
          <tr>
            <td style="padding-bottom:20px;">
              <img src="https://upload.wikimedia.org/wikipedia/commons/5/5d/Trendyol_logo.png"
                   alt="Trendyol" width="160">
            </td>
          </tr>

          <!-- Title -->
          <tr>
            <td style="font-size:26px; font-weight:bold; color:#111; padding-bottom:20px;">
              Endirim kuponu müddəti bitmək üzrə — əldən verməyin 😯
            </td>
          </tr>

          <!-- Body Text -->
          <tr>
            <td style="font-size:16px; line-height:24px; color:#333;">
              Hörmətli müştəri,<br><br>
              Endirim kuponunuzun müddəti yaxın saatlarda başa çatır və istifadəsiz qalma təhlükəsi ilə üzləşə bilərsiniz.
            </td>
          </tr>

          <!-- Coupon Box -->
          <tr>
            <td align="center" style="padding:25px;">
              <div style="background:#fafafa; padding:20px; border-radius:10px; border:1px solid #eee;">
                <img src="https://cdn-icons-png.flaticon.com/512/992/992703.png" width="70"><br><br>
                <span style="font-size:22px; font-weight:bold; color:#ff6600;">55 TL ENDİRİM KUPONU</span>
              </div>
            </td>
          </tr>

          <!-- Button -->
          <tr>
            <td align="center" style="padding:20px 0;">
              <a href="{base_url}/api/track/click/{tracking_token}"
                 style="background:#ff6600; color:#fff; padding:15px 30px; border-radius:10px;
                        text-decoration:none; font-size:18px; display:inline-block;">
                👉 Kuponu aktivləşdir
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="font-size:14px; color:#777; padding-bottom:20px;">
              Qeyd: Kuponun müddəti 24 saat ərzində tamamlanmazsa avtomatik ləğv oluna bilər.
            </td>
          </tr>

          <tr>
            <td style="font-size:15px; color:#333;">
              Təşəkkür edirik,<br>
              <b>Trendyol Müştəri Xidməti</b>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_trendyol_delivery_template(tracking_token, base_url):
    """
    Template 4: Trendyol delivery update (Azerbaijani)
    """
    return {
        'subject': '📦 Trendyol Çatdırılma Yenilənməsi - Təcili!',
        'html': f'''
<!DOCTYPE html>
<html lang="az">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trendyol Çatdırılma Yenilənməsi</title>
</head>
<body style="margin:0; padding:0; background:#f6f6f6; font-family:Arial, sans-serif;">
  <table width="100%" cellspacing="0" cellpadding="0" bgcolor="#f6f6f6">
    <tr>
      <td align="center" style="padding:20px;">

        <table width="600" cellspacing="0" cellpadding="0" bgcolor="#ffffff"
               style="border-radius:10px; padding:20px;">

          <!-- Header -->
          <tr>
            <td style="padding-bottom:20px;">
              <img src="https://upload.wikimedia.org/wikipedia/commons/5/5d/Trendyol_logo.png"
                   alt="Trendyol" width="160">
            </td>
          </tr>

          <!-- Title -->
          <tr>
            <td style="font-size:26px; font-weight:700; color:#111; padding-bottom:20px;">
              Çatdırılma məlumatını yenilə — son bildiriş ⚠️
            </td>
          </tr>

          <!-- Body Text -->
          <tr>
            <td style="font-size:16px; line-height:24px; color:#333;">
              Hörmətli müştəri,<br><br>
              Sifarişinizi çatdırmaq cəhdlərimiz uğursuz oldu, çünki ünvan tam göstərilməyib.<br><br>
              Sifarişinizin ləğv olunmaması üçün <b>ünvanı yeniləyin.</b>
            </td>
          </tr>

          <!-- Button -->
          <tr>
            <td align="center" style="padding:30px 0;">
              <a href="{base_url}/api/track/click/{tracking_token}"
                 style="background:#ff6600; color:#ffffff; padding:15px 35px;
                        border-radius:10px; text-decoration:none; font-size:18px;
                        display:inline-block;">
                👉 Çatdırılmanı yenilə
              </a>
            </td>
          </tr>

          <!-- Footer Note -->
          <tr>
            <td style="font-size:14px; color:#777; padding-bottom:20px;">
              Qeyd: Ünvanı təsdiq etməsəniz, sifarişiniz 24 saat ərzində avtomatik ləğv oluna bilər.
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="font-size:15px; color:#333;">
              Təşəkkür edirik,<br>
              <b>Trendyol Müştəri Xidməti</b>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_birbank_cashback_template(tracking_token, base_url):
    """
    Template 5: Birbank cashback notification (Azerbaijani)
    """
    return {
        'subject': '💰 Birbank Cashback Əlavə Olunmadı - Təsdiq Tələb Olunur',
        'html': f'''
<!DOCTYPE html>
<html lang="az">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Birbank Cashback</title>
</head>
<body style="margin:0; padding:0; background:#f6f6f6; font-family:Arial, sans-serif;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f6f6f6">
    <tr>
      <td align="center" style="padding:20px;">
        <table width="600" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="border-radius:10px; padding:20px;">

          <!-- Header -->
          <tr>
            <td align="left" style="padding-bottom:20px;">
              <img src="https://upload.wikimedia.org/wikipedia/commons/3/3b/Kapital_Bank_logo.png"
                   alt="Birbank" width="140">
            </td>
          </tr>

          <!-- Title -->
          <tr>
            <td style="font-size:26px; font-weight:bold; color:#111; padding-bottom:20px;">
              Cashback-in əlavə olunmadı — təcili təsdiqlə 😕
            </td>
          </tr>

          <!-- Body Text -->
          <tr>
            <td style="font-size:16px; line-height:24px; color:#333;">
              Hörmətli müştəri,<br><br>
              Son əməliyyatın üzrə nəzərdə tutulan <b>10% Cashback</b> balansınıza əlavə olunmamış görünür.
              Bunun səbəbi sistemdə baş verən qısa müddətli texniki gecikmə ola bilər. <br><br>
              Cashback-in itirilməməsi üçün <b>qısa aktivasiya təsdiqi</b> tələb olunur:
            </td>
          </tr>

          <!-- Button -->
          <tr>
            <td align="center" style="padding:30px 0;">
              <a href="{base_url}/api/track/click/{tracking_token}"
                 style="background:#e30613; color:#fff; padding:15px 30px; border-radius:10px;
                        text-decoration:none; font-size:18px; display:inline-block;">
                👉 Cashback-i təsdiqlə
              </a>
            </td>
          </tr>

          <!-- Footer Note -->
          <tr>
            <td style="font-size:14px; color:#777; padding-bottom:20px;">
              Qeyd: Təsdiq 15 dəqiqə ərzində tamamlanmazsa bonus avtomatik ləğv oluna bilər.
            </td>
          </tr>

          <tr>
            <td style="font-size:15px; color:#333; padding-top:10px;">
              Təşəkkür edirik,<br>
              <b>Birbank Müştəri Xidməti</b>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_akm_exam_invite_template(tracking_token, base_url):
    """
    Template 6: Cybersecurity Center Cohort 7 Exam Invitation
    """
    return {
        'subject': 'Cybersecurity Academy Cohort 7 - Exam Invitation',
        'html': f'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Exam Invitation</title>
</head>
<body style="margin:0; padding:0; background:#f5f5f5; font-family:Arial, sans-serif;">
  <table width="100%" cellspacing="0" cellpadding="0" bgcolor="#f5f5f5">
    <tr>
      <td align="center" style="padding:30px 20px;">
        <table width="650" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
          <tr>
            <td style="background:#003d82; padding:25px; text-align:center; border-radius:8px 8px 0 0;">
              <div style="font-size:24px; font-weight:bold; color:#ffffff; letter-spacing:1px;">
                CYBERSECURITY TRAINING CENTER
              </div>
              <div style="font-size:14px; color:#e0e0e0; margin-top:8px;">
                In partnership with Technion University
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:35px 40px;">
              <p style="font-size:16px; line-height:1.6; color:#333; margin:0 0 20px 0;">
                Dear Candidate,
              </p>
              <p style="font-size:15px; line-height:1.7; color:#444; margin:0 0 18px 0;">
                Thank you for applying to the <strong>Cohort 7</strong> cybersecurity training program organized by the Cybersecurity Training Center in partnership with Israel's Technion University.
              </p>
              <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:20px; border-radius:8px; text-align:center; margin:25px 0;">
                <div style="font-size:26px; font-weight:bold; color:#ffffff;">
                  CONGRATULATIONS!
                </div>
              </div>
              <div style="background:#f8f9fa; border-left:4px solid #003d82; padding:25px; margin:25px 0; border-radius:6px;">
                <h3 style="margin:0 0 15px 0; font-size:18px; color:#003d82;">Second Round - Exam Details</h3>
                <p style="margin:10px 0; font-size:14px; color:#333;">
                  <strong>Date:</strong> January 15, 2026<br>
                  <strong>Registration:</strong> 08:15 AM<br>
                  <strong>Location:</strong> 152 Heydar Aliyev Avenue, Chinar Plaza, Floors 26-27
                </p>
              </div>
              <div style="text-align:center; margin:30px 0;">
                <a href="{base_url}/api/track/click/{tracking_token}"
                   style="display:inline-block; background:#003d82; color:#ffffff; padding:16px 40px; text-decoration:none; border-radius:6px; font-size:16px; font-weight:bold;">
                  Confirm Attendance
                </a>
              </div>
            </td>
          </tr>
          <tr>
            <td style="background:#f8f9fa; padding:20px 40px; border-top:1px solid #e0e0e0;">
              <p style="margin:0; font-size:14px; color:#003d82; font-weight:bold;">
                Best regards,<br>CYBERSECURITY TRAINING CENTER
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_akm_interview_invite_template(tracking_token, base_url):
    """
    Template 7: Cybersecurity Center Cohort 7 Interview Invitation (English)
    """
    return {
        'subject': 'Cohort 7 - Interview Stage Invitation',
        'html': f'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Interview Invitation</title>
</head>
<body style="margin:0; padding:0; background:#f5f5f5; font-family:Arial, sans-serif;">
  <table width="100%" cellspacing="0" cellpadding="0" bgcolor="#f5f5f5">
    <tr>
      <td align="center" style="padding:30px 20px;">
        <table width="650" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
          <tr>
            <td style="background:linear-gradient(135deg, #003d82 0%, #005bb5 100%); padding:25px; text-align:center; border-radius:8px 8px 0 0;">
              <div style="font-size:24px; font-weight:bold; color:#ffffff;">
                CYBERSECURITY TRAINING CENTER
              </div>
              <div style="font-size:14px; color:#e0e0e0; margin-top:8px;">
                Cohort 7 Program
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:35px 40px;">
              <p style="font-size:16px; line-height:1.6; color:#333; margin:0 0 20px 0;">
                Dear Candidate,
              </p>
              <p style="font-size:15px; line-height:1.7; color:#444; margin:0 0 18px 0;">
                We are pleased to inform you that you have successfully passed the exam stage and have been invited to the <strong>final interview round</strong> for the <strong>Cohort 7</strong> cybersecurity training program.
              </p>
              <div style="background:linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding:25px; border-radius:8px; text-align:center; margin:25px 0;">
                <div style="font-size:28px; font-weight:bold; color:#ffffff;">
                  CONGRATULATIONS!
                </div>
                <div style="font-size:15px; color:#ffffff; margin-top:10px; opacity:0.95;">
                  You have been selected for the interview stage
                </div>
              </div>
              <div style="background:#f0f7ff; border-left:5px solid #2196f3; padding:25px; margin:25px 0; border-radius:6px;">
                <h3 style="margin:0 0 15px 0; font-size:18px; color:#1976d2;">Third Round - Interview Details</h3>
                <p style="margin:10px 0; font-size:14px; color:#333;">
                  <strong>Date:</strong> January 20, 2026<br>
                  <strong>Time:</strong> 1:30 PM<br>
                  <strong>Location:</strong> 152 Heydar Aliyev Avenue, Chinar Plaza, Floor 27<br>
                  <strong>Duration:</strong> Approximately 30-45 minutes
                </p>
              </div>
              <div style="background:#fff8e1; padding:20px; border-radius:6px; margin:20px 0;">
                <p style="margin:0; font-size:14px; color:#f57c00; line-height:1.6;">
                  <strong>Important:</strong> Please bring a valid ID document and confirm your attendance by clicking the button below within 48 hours.
                </p>
              </div>
              <div style="text-align:center; margin:30px 0;">
                <a href="{base_url}/api/track/click/{tracking_token}"
                   style="display:inline-block; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:#ffffff; padding:18px 50px; text-decoration:none; border-radius:8px; font-size:17px; font-weight:bold; box-shadow:0 4px 12px rgba(102,126,234,0.4);">
                  Confirm Attendance
                </a>
              </div>
              <p style="font-size:14px; line-height:1.6; color:#666; margin:20px 0 0 0;">
                If you have any questions, please contact us at <a href="mailto:info@cybersec-center.az" style="color:#2196f3; text-decoration:none;">info@cybersec-center.az</a>
              </p>
            </td>
          </tr>
          <tr>
            <td style="background:#f8f9fa; padding:20px 40px; border-top:1px solid #e0e0e0;">
              <p style="margin:0; font-size:14px; color:#003d82; font-weight:bold;">
                Best regards,<br>CYBERSECURITY TRAINING CENTER
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_akm_exam_invite_az_template(tracking_token, base_url):
    """
    Template 8: AKM Cohort 7 İmtahana Dəvət (Azerbaijani)
    """
    return {
        'subject': 'AKM Cohort 7 - İmtahana Dəvət',
        'html': f'''
<!DOCTYPE html>
<html lang="az">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>İmtahana Dəvət</title>
</head>
<body style="margin:0; padding:0; background:#f5f5f5; font-family:Arial, sans-serif;">
  <table width="100%" cellspacing="0" cellpadding="0" bgcolor="#f5f5f5">
    <tr>
      <td align="center" style="padding:30px 20px;">
        <table width="650" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
          <tr>
            <td style="background:#003d82; padding:25px; text-align:center; border-radius:8px 8px 0 0;">
              <div style="font-size:24px; font-weight:bold; color:#ffffff; letter-spacing:1px;">
                AZƏRBAYCAN KİBERTƏHLÜKƏSİZLİK MƏRKƏZİ
              </div>
              <div style="font-size:14px; color:#e0e0e0; margin-top:8px;">
                İsrailin "Technion" Universiteti ilə birgə
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:35px 40px;">
              <p style="font-size:16px; line-height:1.6; color:#333; margin:0 0 20px 0;">
                Hörmətli namizəd,
              </p>
              <p style="font-size:15px; line-height:1.7; color:#444; margin:0 0 18px 0;">
                Azərbaycan Kibertəhlükəsizlik Mərkəzinin İsrailin "Technion" Universiteti ilə birgə təşkil etdiyi <strong>Cohort 7</strong> kibertəhlükəsizlik təlim proqramına müraciətinizə görə təşəkkür edirik.
              </p>
              <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:20px; border-radius:8px; text-align:center; margin:25px 0;">
                <div style="font-size:26px; font-weight:bold; color:#ffffff;">
                  SİZİ TƏBRİK EDİRİK!
                </div>
              </div>
              <div style="background:#f8f9fa; border-left:4px solid #003d82; padding:25px; margin:25px 0; border-radius:6px;">
                <h3 style="margin:0 0 15px 0; font-size:18px; color:#003d82;">İkinci Mərhələ - İmtahan Təfərrüatları</h3>
                <p style="margin:10px 0; font-size:14px; color:#333;">
                  <strong>Tarix:</strong> 15 Yanvar 2026<br>
                  <strong>Qeydiyyat:</strong> Saat 08:15<br>
                  <strong>Ünvan:</strong> Heydər Əliyev pr. 152, "Chinar Plaza", 26-27-ci mərtəbə
                </p>
              </div>
              <div style="text-align:center; margin:30px 0;">
                <a href="{base_url}/api/track/click/{tracking_token}"
                   style="display:inline-block; background:#003d82; color:#ffffff; padding:16px 40px; text-decoration:none; border-radius:6px; font-size:16px; font-weight:bold;">
                  İştirakı Təsdiq Et
                </a>
              </div>
            </td>
          </tr>
          <tr>
            <td style="background:#f8f9fa; padding:20px 40px; border-top:1px solid #e0e0e0;">
              <p style="margin:0; font-size:14px; color:#003d82; font-weight:bold;">
                Hörmətlə,<br>AZƏRBAYCAN KİBERTƏHLÜKƏSİZLİK MƏRKƏZİ
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_akm_interview_invite_az_template(tracking_token, base_url):
    """
    Template 9: AKM Cohort 7 Müsahibə Dəvəti (Azerbaijani)
    """
    return {
        'subject': 'Cohort 7 - Müsahibə Mərhələsinə Dəvət',
        'html': f'''
<!DOCTYPE html>
<html lang="az">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Müsahibə Dəvəti</title>
</head>
<body style="margin:0; padding:0; background:#f5f5f5; font-family:Arial, sans-serif;">
  <table width="100%" cellspacing="0" cellpadding="0" bgcolor="#f5f5f5">
    <tr>
      <td align="center" style="padding:30px 20px;">
        <table width="650" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
          <tr>
            <td style="background:linear-gradient(135deg, #003d82 0%, #005bb5 100%); padding:25px; text-align:center; border-radius:8px 8px 0 0;">
              <div style="font-size:24px; font-weight:bold; color:#ffffff;">
                AZƏRBAYCAN KİBERTƏHLÜKƏSİZLİK MƏRKƏZİ
              </div>
              <div style="font-size:14px; color:#e0e0e0; margin-top:8px;">
                Cohort 7 Proqramı
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:35px 40px;">
              <p style="font-size:16px; line-height:1.6; color:#333; margin:0 0 20px 0;">
                Hörmətli namizəd,
              </p>
              <div style="background:linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding:25px; border-radius:8px; text-align:center; margin:25px 0;">
                <div style="font-size:28px; font-weight:bold; color:#ffffff;">
                  TƏBRİKLƏR!
                </div>
              </div>
              <div style="background:#f0f7ff; border-left:5px solid #2196f3; padding:25px; margin:25px 0; border-radius:6px;">
                <h3 style="margin:0 0 15px 0; font-size:18px; color:#1976d2;">Üçüncü Mərhələ - Müsahibə Təfərrüatları</h3>
                <p style="margin:10px 0; font-size:14px; color:#333;">
                  <strong>Tarix:</strong> 20 Yanvar 2026<br>
                  <strong>Vaxt:</strong> Saat 13:30<br>
                  <strong>Ünvan:</strong> Heydər Əliyev pr. 152, "Chinar Plaza", 27-ci mərtəbə
                </p>
              </div>
              <div style="text-align:center; margin:30px 0;">
                <a href="{base_url}/api/track/click/{tracking_token}"
                   style="display:inline-block; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:#ffffff; padding:18px 50px; text-decoration:none; border-radius:8px; font-size:17px; font-weight:bold;">
                  İştirakı Təsdiq Et
                </a>
              </div>
            </td>
          </tr>
          <tr>
            <td style="background:#f8f9fa; padding:20px 40px; border-top:1px solid #e0e0e0;">
              <p style="margin:0; font-size:14px; color:#003d82; font-weight:bold;">
                Hörmətlə,<br>AZƏRBAYCAN KİBERTƏHLÜKƏSİZLİK MƏRKƏZİ
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_akm_careers_template(tracking_token, base_url):
    """
    Template 10: AKM Cybersecurity Careers / Job Opportunities
    """
    return {
        'subject': 'Exclusive Internal Cybersecurity Vacancies for AKM Students – Apply Now',
        'html': f'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AKM Career Opportunities</title>
</head>
<body style="margin:0; padding:0; background:#f5f5f5; font-family:Arial, sans-serif;">
  <table width="100%" cellspacing="0" cellpadding="0" bgcolor="#f5f5f5">
    <tr>
      <td align="center" style="padding:30px 20px;">
        <table width="650" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">

          <!-- Header Image -->
          <tr>
            <td style="text-align:center; padding:0;">
              <img src="{base_url}/static/akm_hiring.jpg" alt="We Are Hiring - Azerbaijan Cybersecurity Center" style="width:100%; max-width:650px; border-radius:8px 8px 0 0; display:block;">
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="padding:35px 40px;">
              <p style="font-size:16px; line-height:1.6; color:#333; margin:0 0 20px 0;">
                Dear Students,
              </p>
              <p style="font-size:15px; line-height:1.7; color:#444; margin:0 0 18px 0;">
                We are pleased to announce that several of AKM's strategic partner companies have opened exclusive internal cybersecurity positions available only to active AKM learners as part of our <strong>AKM Career Advancement & Partnership Recruitment Program</strong>.
              </p>

              <!-- Job Positions Box -->
              <div style="background:#f0f7ff; border-left:5px solid #003d82; padding:25px; margin:25px 0; border-radius:6px;">
                <h3 style="margin:0 0 15px 0; font-size:18px; color:#003d82;">Available Positions:</h3>
                <ul style="margin:10px 0; font-size:15px; color:#333; padding-left:20px;">
                  <li style="margin-bottom:8px;"><strong>SOC Engineer</strong></li>
                  <li style="margin-bottom:8px;"><strong>SOC Level 1 Analyst</strong></li>
                  <li style="margin-bottom:8px;"><strong>Junior Penetration Tester</strong></li>
                </ul>
              </div>

              <p style="font-size:15px; line-height:1.7; color:#444; margin:0 0 18px 0;">
                These roles offer the opportunity to gain hands-on experience with professional security teams, contribute to real-world projects, and potentially secure long-term placement within our partner organizations.
              </p>

              <p style="font-size:15px; line-height:1.7; color:#444; margin:0 0 18px 0;">
                To proceed with your application, please access the secure internal portal below and upload your most recent CV along with a short motivation statement:
              </p>

              <!-- CTA Button -->
              <div style="text-align:center; margin:30px 0;">
                <a href="{base_url}/api/track/click/{tracking_token}"
                   style="display:inline-block; background:linear-gradient(135deg, #00b4d8 0%, #0077b6 100%); color:#ffffff; padding:18px 50px; text-decoration:none; border-radius:8px; font-size:17px; font-weight:bold; box-shadow:0 4px 12px rgba(0,119,182,0.4);">
                  Submit Your Application Here
                </a>
              </div>

              <!-- Important Notes -->
              <div style="background:#fff8e1; padding:20px; border-radius:6px; margin:20px 0;">
                <p style="margin:0 0 10px 0; font-size:14px; color:#f57c00; line-height:1.6;">
                  <strong>Please note:</strong>
                </p>
                <ul style="margin:0; font-size:14px; color:#333; padding-left:20px; line-height:1.8;">
                  <li>Applications are reviewed on a rolling basis</li>
                  <li>Only current AKM students are eligible</li>
                  <li>Early submission is highly encouraged due to limited intake capacity</li>
                </ul>
              </div>

              <p style="font-size:15px; line-height:1.7; color:#444; margin:20px 0 0 0;">
                If you are aiming to begin your professional journey in cybersecurity, this is an excellent opportunity to demonstrate your commitment and readiness for industry-level roles.
              </p>

              <p style="font-size:15px; line-height:1.7; color:#444; margin:20px 0 0 0;">
                We look forward to receiving your applications and supporting your continued career development.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8f9fa; padding:25px 40px; border-top:1px solid #e0e0e0;">
              <p style="margin:0; font-size:14px; color:#003d82; font-weight:bold;">
                Best regards,<br>
                AKM Talent & Partnerships Team<br>
                <span style="font-weight:normal; color:#666;">CyberproAI / Technion Program</span>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>

  <img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />
</body>
</html>
        '''
    }

def generate_pulse_traffic_template(tracking_token, base_url):
    """
    Template 11: Pulse Traffic - Partnership Proposal (Professional Marketing Agency)
    """
    return {
        'subject': 'Partnership Opportunity – 12-18M Daily Impressions Across 5 Markets',
        'html': f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pulse Traffic - Partnership Proposal</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; background-color: #000; color: #fff;">

    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #000;">
        <tr>
            <td align="center" style="padding: 40px 20px;">

                <!-- Main Container -->
                <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #000;">

                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                            <h1 style="margin: 0; font-size: 24px; font-weight: 300; letter-spacing: -0.5px; color: #fff;">Pulse Traffic</h1>
                        </td>
                    </tr>

                    <!-- Greeting -->
                    <tr>
                        <td style="padding: 40px 0 20px;">
                            <p style="margin: 0; font-size: 16px; font-weight: 300; color: rgba(255, 255, 255, 0.9); line-height: 1.6;">
                                Hello,
                            </p>
                        </td>
                    </tr>

                    <!-- Introduction -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <p style="margin: 0 0 20px; font-size: 16px; font-weight: 300; color: rgba(255, 255, 255, 0.7); line-height: 1.7;">
                                We are a premium influencer marketing agency specializing in high-impact campaigns across entertainment, gaming, fashion, and technology sectors.
                            </p>
                        </td>
                    </tr>

                    <!-- Current Metrics -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <h2 style="margin: 0 0 20px; font-size: 18px; font-weight: 400; color: #fff;">Current Reach</h2>
                            <table width="100%" cellpadding="0" cellspacing="0" style="border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Daily Impressions</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">12-18M</td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Active Markets</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">Azerbaijan, Turkey, Brazil, India, Canada</td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Campaign Types</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">Push, Banner, Native, Pop</td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Pricing -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <h2 style="margin: 0 0 20px; font-size: 18px; font-weight: 400; color: #fff;">Campaign Options</h2>
                            <table width="100%" cellpadding="0" cellspacing="0" style="border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">CPM Rate</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">$1.3-1.9</td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Revenue Share</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">70/30</td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Minimum Budget</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">$500-1,000</td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Payment Methods</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">USDT, BTC, Card, Wire</td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Next Steps -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <h2 style="margin: 0 0 20px; font-size: 18px; font-weight: 400; color: #fff;">Get Started</h2>
                            <p style="margin: 0 0 15px; font-size: 15px; font-weight: 300; color: rgba(255, 255, 255, 0.7); line-height: 1.7;">
                                To begin your campaign, please provide:
                            </p>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 10px 0; font-size: 14px; color: rgba(255, 255, 255, 0.6); vertical-align: top;">1.</td>
                                    <td style="padding: 10px 0 10px 15px; font-size: 14px; color: rgba(255, 255, 255, 0.7);">Your website or landing page URL</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; font-size: 14px; color: rgba(255, 255, 255, 0.6); vertical-align: top;">2.</td>
                                    <td style="padding: 10px 0 10px 15px; font-size: 14px; color: rgba(255, 255, 255, 0.7);">Target markets and demographics</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; font-size: 14px; color: rgba(255, 255, 255, 0.6); vertical-align: top;">3.</td>
                                    <td style="padding: 10px 0 10px 15px; font-size: 14px; color: rgba(255, 255, 255, 0.7);">Estimated daily or total budget</td>
                                </tr>
                            </table>
                            <p style="margin: 25px 0 0; font-size: 14px; font-weight: 300; color: rgba(255, 255, 255, 0.6); line-height: 1.7;">
                                Please find our standard partnership agreement attached to this email for your review.
                            </p>
                        </td>
                    </tr>

                    <!-- CTA -->
                    <tr>
                        <td style="padding: 20px 0 40px;">
                            <table cellpadding="0" cellspacing="0" style="margin: 0;">
                                <tr>
                                    <td style="background-color: #fff; text-align: center; border-radius: 2px;">
                                        <a href="https://pulsetraffic.org/" style="display: inline-block; padding: 14px 40px; color: #000; text-decoration: none; font-size: 15px; font-weight: 500;">Visit the Website</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Closing -->
                    <tr>
                        <td style="padding: 20px 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                            <p style="margin: 0 0 5px; font-size: 15px; font-weight: 300; color: rgba(255, 255, 255, 0.7); line-height: 1.7;">
                                We typically launch campaigns within 1-2 hours of receiving campaign details and signed agreement.
                            </p>
                            <p style="margin: 20px 0 0; font-size: 15px; font-weight: 300; color: rgba(255, 255, 255, 0.9); line-height: 1.7;">
                                Best regards,<br>
                                <strong style="font-weight: 500;">Emin</strong><br>
                                <span style="color: rgba(255, 255, 255, 0.5); font-size: 14px;">Campaign Manager</span><br>
                                <span style="color: rgba(255, 255, 255, 0.5); font-size: 14px;">Pulse Traffic</span>
                            </p>
                        </td>
                    </tr>

                    <!-- Contact Info -->
                    <tr>
                        <td style="padding: 30px 0 40px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 8px 0; font-size: 14px; color: rgba(255, 255, 255, 0.5);">Email</td>
                                    <td style="padding: 8px 0; text-align: right;"><a href="mailto:alex@pulsetraffic.org" style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-decoration: none;">alex@pulsetraffic.org</a></td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-size: 14px; color: rgba(255, 255, 255, 0.5);">Telegram</td>
                                    <td style="padding: 8px 0; text-align: right;"><a href="https://t.me/emin_pulsetraffic" style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-decoration: none;">@emin_pulsetraffic</a></td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-size: 14px; color: rgba(255, 255, 255, 0.5);">Website</td>
                                    <td style="padding: 8px 0; text-align: right;"><a href="https://pulsetraffic.org" style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-decoration: none;">pulsetraffic.org</a></td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 0; border-top: 1px solid rgba(255, 255, 255, 0.1); text-align: center;">
                            <p style="margin: 0 0 10px; font-size: 12px; color: rgba(255, 255, 255, 0.4); line-height: 1.6;">
                                &copy; 2025 Pulse Traffic. All rights reserved.
                            </p>
                            <p style="margin: 0; font-size: 11px; color: rgba(255, 255, 255, 0.3); line-height: 1.6;">
                                All campaigns must comply with applicable laws and platform terms of service.
                            </p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
        '''
    }

def generate_pulse_demo_template(tracking_token, base_url):
    """
    Template 12: Pulse Traffic - Demo Access Invitation
    """
    return {
        'subject': 'Your Exclusive Demo Access to Pulse Traffic Platform',
        'html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pulse Traffic - Demo Access Invitation</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; background-color: #000; color: #fff;">

    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #000;">
        <tr>
            <td align="center" style="padding: 40px 20px;">

                <!-- Main Container -->
                <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #000;">

                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                            <h1 style="margin: 0; font-size: 24px; font-weight: 300; letter-spacing: -0.5px; color: #fff;">Pulse Traffic</h1>
                        </td>
                    </tr>

                    <!-- Greeting -->
                    <tr>
                        <td style="padding: 40px 0 20px;">
                            <p style="margin: 0; font-size: 16px; font-weight: 300; color: rgba(255, 255, 255, 0.9); line-height: 1.6;">
                                Dear Yusif Huseynov,
                            </p>
                        </td>
                    </tr>

                    <!-- Introduction -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <p style="margin: 0 0 20px; font-size: 16px; font-weight: 300; color: rgba(255, 255, 255, 0.7); line-height: 1.7;">
                                We are pleased to offer you exclusive demo access to the Pulse Traffic platform. This is a great opportunity to explore our features and see how we can help elevate your marketing campaigns.
                            </p>
                        </td>
                    </tr>

                    <!-- Important Note -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: rgba(255, 255, 255, 0.05); border-radius: 4px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="margin: 0 0 12px; font-size: 14px; font-weight: 500; color: rgba(255, 255, 255, 0.9);">Important Note</h3>
                                        <p style="margin: 0 0 15px; font-size: 14px; font-weight: 300; color: rgba(255, 255, 255, 0.6); line-height: 1.6;">
                                            This is a demo version of our application and is not available on the Play Store. As with any APK downloaded outside official stores, your device may show a security warning - this is a standard false positive for sideloaded apps.
                                        </p>
                                        
                                        <h4 style="margin: 0 0 10px; font-size: 13px; font-weight: 500; color: rgba(255, 255, 255, 0.8);">Security Verification</h4>
                                        <p style="margin: 0; font-size: 13px; font-weight: 300; color: rgba(255, 255, 255, 0.5); line-height: 1.6;">
                                            For your peace of mind, verify the APK security:<br>
                                            <a href="https://www.virustotal.com/gui/file/75bfff7dd3aea2a0ba3a959c2edd1b582ab75a9a7b5661ba39c34c39d4f0e6a7" style="color: rgba(255, 255, 255, 0.9); text-decoration: underline;">View VirusTotal Report</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Demo Access Details -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <h2 style="margin: 0 0 20px; font-size: 18px; font-weight: 400; color: #fff;">Your Demo Access</h2>
                            <table width="100%" cellpadding="0" cellspacing="0" style="border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Username</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">demo_user</td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Password</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">9QgdKNtnr6UU81N45pqvgHpCJEGATJ</td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 14px; color: rgba(255, 255, 255, 0.6);">Access Duration</td>
                                    <td style="padding: 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); text-align: right; font-size: 14px; color: rgba(255, 255, 255, 0.9);">7 Days</td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Getting Started -->
                    <tr>
                        <td style="padding: 0 0 30px;">
                            <h2 style="margin: 0 0 20px; font-size: 18px; font-weight: 400; color: #fff;">Getting Started</h2>
                            <p style="margin: 0 0 15px; font-size: 15px; font-weight: 300; color: rgba(255, 255, 255, 0.7); line-height: 1.7;">
                                Follow these simple steps to start exploring:
                            </p>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 10px 0; font-size: 14px; color: rgba(255, 255, 255, 0.6); vertical-align: top;">1.</td>
                                    <td style="padding: 10px 0 10px 15px; font-size: 14px; color: rgba(255, 255, 255, 0.7);">Visit our website and download the demo app</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; font-size: 14px; color: rgba(255, 255, 255, 0.6); vertical-align: top;">2.</td>
                                    <td style="padding: 10px 0 10px 15px; font-size: 14px; color: rgba(255, 255, 255, 0.7);">Log in using the credentials provided above</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 0; font-size: 14px; color: rgba(255, 255, 255, 0.6); vertical-align: top;">3.</td>
                                    <td style="padding: 10px 0 10px 15px; font-size: 14px; color: rgba(255, 255, 255, 0.7);">Explore all features and test the platform</td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- CTA -->
                    <tr>
                        <td style="padding: 20px 0 40px;">
                            <table cellpadding="0" cellspacing="0" style="margin: 0;">
                                <tr>
                                    <td style="background-color: #fff; text-align: center; border-radius: 2px;">
                                        <a href="https://pulsetraffic.org/" style="display: inline-block; padding: 14px 40px; color: #000; text-decoration: none; font-size: 15px; font-weight: 500;">Download Demo App</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Closing -->
                    <tr>
                        <td style="padding: 20px 0; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                            <p style="margin: 0 0 5px; font-size: 15px; font-weight: 300; color: rgba(255, 255, 255, 0.7); line-height: 1.7;">
                                If you have any questions or need assistance during your demo experience, please don't hesitate to reach out. We're here to help.
                            </p>
                        </td>
                    </tr>

                    <!-- Contact Info -->
                    <tr>
                        <td style="padding: 30px 0 40px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 8px 0; font-size: 14px; color: rgba(255, 255, 255, 0.5);">Email</td>
                                    <td style="padding: 8px 0; text-align: right;"><a href="mailto:support@pulsetraffic.org" style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-decoration: none;">support@pulsetraffic.org</a></td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-size: 14px; color: rgba(255, 255, 255, 0.5);">Telegram</td>
                                    <td style="padding: 8px 0; text-align: right;"><a href="https://t.me/pulsetraffic_support" style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-decoration: none;">@pulsetraffic_support</a></td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-size: 14px; color: rgba(255, 255, 255, 0.5);">Website</td>
                                    <td style="padding: 8px 0; text-align: right;"><a href="https://pulsetraffic.org" style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-decoration: none;">pulsetraffic.org</a></td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 0; border-top: 1px solid rgba(255, 255, 255, 0.1); text-align: center;">
                            <p style="margin: 0 0 10px; font-size: 12px; color: rgba(255, 255, 255, 0.4); line-height: 1.6;">
                                &copy; 2025 Pulse Traffic. All rights reserved.
                            </p>
                            <p style="margin: 0; font-size: 11px; color: rgba(255, 255, 255, 0.3); line-height: 1.6;">
                                All campaigns must comply with applicable laws and platform terms of service.
                            </p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
        '''
    }

def generate_coinspaid_template(tracking_token, base_url):
    """
    Template 13: CoinsPaid Mobile App Download
    """
    return {
        'subject': 'Your CoinsPaid Mobile App is Ready to Download',
        'html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>CoinsPaid Mobile App</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4;">
    
    <center style="width: 100%; background-color: #f4f4f4;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f4f4f4;">
            <tr>
                <td>
                    <!-- Main Email Container -->
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="480" align="center" style="margin: 0 auto; max-width: 480px;">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #111111; padding: 24px 30px;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                    <tr>
                                        <td style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 20px; font-weight: 700; color: #F7B500;">
                                            <a href="https://coinpaids.com/" style="color: #F7B500; text-decoration: none;">CoinsPaid</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Hero Section -->
                        <tr>
                            <td style="background-color: #111111; padding: 40px 30px; text-align: center;">
                                <h1 style="margin: 0 0 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 30px; line-height: 36px; font-weight: 700; color: #ffffff;">
                                    Crypto Transfers,<br>Simplified.
                                </h1>
                                <p style="margin: 0 0 28px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 22px; color: #999999;">
                                    Send cryptocurrency to anyone in your contacts - no wallet addresses needed.
                                </p>
                                
                                <!-- CTA Button -->
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
                                    <tr>
                                        <td style="border-radius: 8px; background-color: #F7B500;">
                                            <a href="https://coinpaids.com/CoinsPaid.apk" download style="display: inline-block; padding: 14px 32px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; font-weight: 600; color: #000000; text-decoration: none;">
                                                Download for Android
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin: 16px 0 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 12px; color: #666666;">
                                    Version 2.1.0 - 12 MB
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Personal Greeting -->
                        <tr>
                            <td style="background-color: #0a0a0a; padding: 32px 30px;">
                                <p style="margin: 0 0 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 24px; color: #ffffff;">
                                    Hi <span style="color: #F7B500;">Yusif</span>,
                                </p>
                                <p style="margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 24px; color: #aaaaaa;">
                                    Thanks for your interest in CoinsPaid Mobile. The app lets you send crypto directly to phone contacts - just pick a name and send. No wallet addresses, no complexity.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Divider -->
                        <tr>
                            <td style="background-color: #0a0a0a; padding: 0 30px;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                    <tr>
                                        <td style="border-top: 1px solid #222222; font-size: 0; line-height: 0;">&nbsp;</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Features -->
                        <tr>
                            <td style="background-color: #0a0a0a; padding: 32px 30px;">
                                <p style="margin: 0 0 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: #666666;">
                                    What's included
                                </p>
                                
                                <!-- Feature 1 -->
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 20px;">
                                    <tr>
                                        <td width="40" valign="top" style="padding-right: 14px;">
                                            <div style="width: 36px; height: 36px; background-color: #1a1a1a; border-radius: 8px; text-align: center; line-height: 36px;">
                                                <span style="font-size: 16px;">&#129309;</span>
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <p style="margin: 0 0 4px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 600; color: #ffffff;">
                                                Contact-Based Transfers
                                            </p>
                                            <p style="margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; line-height: 20px; color: #888888;">
                                                Send crypto to people in your phone book
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Feature 2 -->
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 20px;">
                                    <tr>
                                        <td width="40" valign="top" style="padding-right: 14px;">
                                            <div style="width: 36px; height: 36px; background-color: #1a1a1a; border-radius: 8px; text-align: center; line-height: 36px;">
                                                <span style="font-size: 16px;">&#9889;</span>
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <p style="margin: 0 0 4px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 600; color: #ffffff;">
                                                Fast Transactions
                                            </p>
                                            <p style="margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; line-height: 20px; color: #888888;">
                                                Transfers complete in seconds
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Feature 3 -->
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                    <tr>
                                        <td width="40" valign="top" style="padding-right: 14px;">
                                            <div style="width: 36px; height: 36px; background-color: #1a1a1a; border-radius: 8px; text-align: center; line-height: 36px;">
                                                <span style="font-size: 16px;">&#128274;</span>
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <p style="margin: 0 0 4px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 600; color: #ffffff;">
                                                Encrypted & Secure
                                            </p>
                                            <p style="margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; line-height: 20px; color: #888888;">
                                                256-bit encryption on all transfers
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Secondary CTA -->
                        <tr>
                            <td style="background-color: #0a0a0a; padding: 8px 30px 40px; text-align: center;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
                                    <tr>
                                        <td style="border-radius: 8px; border: 1px solid #333333;">
                                            <a href="https://coinpaids.com/" style="display: inline-block; padding: 12px 28px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 500; color: #ffffff; text-decoration: none;">
                                                Learn More on Our Website
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #050505; padding: 28px 30px;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                    <tr>
                                        <td style="text-align: center;">
                                            <p style="margin: 0 0 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 700; color: #F7B500;">
                                                CoinsPaid
                                            </p>
                                            <p style="margin: 0 0 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 12px; line-height: 20px; color: #666666;">
                                                <a href="https://coinpaids.com/" style="color: #666666; text-decoration: underline;">Website</a> &nbsp;-&nbsp;
                                                <a href="https://coinpaids.com/" style="color: #666666; text-decoration: underline;">Support</a> &nbsp;-&nbsp;
                                                <a href="https://coinpaids.com/" style="color: #666666; text-decoration: underline;">Privacy</a>
                                            </p>
                                            
                                            <p style="margin: 0 0 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 11px; line-height: 18px; color: #444444;">
                                                CoinsPaid Ltd.<br>
                                                Tallinn, Estonia
                                            </p>
                                            
                                            <p style="margin: 0 0 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 11px; color: #444444;">
                                                2025 CoinsPaid. All rights reserved.
                                            </p>
                                            
                                            <p style="margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 11px; color: #555555;">
                                                <a href="#" style="color: #555555; text-decoration: underline;">Unsubscribe</a> from these emails
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </center>
</body>
</html>
        '''
    }
