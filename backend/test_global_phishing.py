#!/usr/bin/env python3
"""
PhishVision Global Phishing Detection Test
Tests AI-powered detection across multiple languages and attack types.
"""

from services.hybrid_analyzer import create_hybrid_analyzer

# Global phishing test samples - different languages and attack types
TEST_CASES = [
    # 1. English - Classic credential phishing
    {
        'name': 'US English - Microsoft 365 Credential Theft',
        'subject': 'Your Microsoft 365 password expires in 24 hours',
        'body': '''Dear valued user,

Your Microsoft 365 password will expire in 24 hours. To avoid service interruption, please verify your account immediately.

Click here to verify: http://microsoft-365-verify.secure-login.tk/verify

If you do not verify within 24 hours, your account will be suspended.

Microsoft Security Team''',
        'sender': 'security@microsoft-support-center.com',
        'expected': 'malicious'
    },

    # 2. Portuguese - BEC/CEO Fraud
    {
        'name': 'BR Portuguese - CEO Fraud/BEC Attack',
        'subject': 'Urgente - Transferencia Confidencial',
        'body': '''Ola,

Sou o CEO da empresa. Preciso que voce faca uma transferencia urgente de R 50.000 para um fornecedor internacional. E uma operacao confidencial, nao fale com ninguem sobre isso.

Use os seguintes dados:
PIX: parceiro-comercial@pixpay.com
Banco: 341 - Itau
Favorecido: Importadora Global LTDA

Faca isso antes das 17h de hoje. Depois te explico pessoalmente.

Abs,
Roberto Silva
CEO''',
        'sender': 'roberto.silva@empresa-corp.com.br',
        'expected': 'malicious'
    },

    # 3. German - Bank Phishing
    {
        'name': 'DE German - Deutsche Bank Phishing',
        'subject': 'Wichtig: Ihr Konto wurde eingeschrankt',
        'body': '''Sehr geehrter Kunde,

Wir haben ungewohnliche Aktivitaten auf Ihrem Konto festgestellt. Um Ihre Sicherheit zu gewahrleisten, wurde Ihr Konto vorubergehend eingeschrankt.

Bitte bestatigen Sie Ihre Identitat innerhalb von 48 Stunden, um Ihr Konto wiederherzustellen.

Klicken Sie hier zur Verifizierung: http://deutsche-bank-sicherheit.de.com/verify

Mit freundlichen Grussen,
Deutsche Bank Sicherheitsteam''',
        'sender': 'sicherheit@deutsche-bank-de.net',
        'expected': 'malicious'
    },

    # 4. Japanese - Amazon Phishing
    {
        'name': 'JP Japanese - Amazon Account Theft',
        'subject': 'Amazon Account: Suspicious login detected',
        'body': '''Amazonをご利用いただきありがとうございます。

お客様のアカウントで不審なアクティビティが検出されました。第三者による不正アクセスの可能性があります。

24時間以内にアカウントを確認しない場合、アカウントは永久に停止されます。

今すぐ確認する: http://amazon-jp-security.tk/verify-account

Amazon Customer Service''',
        'sender': 'account-update@amazon-jp-security.com',
        'expected': 'malicious'
    },

    # 5. Russian - Cryptocurrency Scam
    {
        'name': 'RU Russian - Crypto Giveaway Scam',
        'subject': 'You won 0.5 BTC! Claim now',
        'body': '''Congratulations!

You have been selected to receive 0.5 Bitcoin (approximately 20,000 USD) in our exclusive giveaway.

To claim your reward, you need to:
1. Visit our website: http://bitcoin-giveaway-official.ru.com
2. Connect your wallet
3. Send 0.01 BTC for verification (will be returned)

Offer valid for 2 hours only!

Bitcoin Foundation''',
        'sender': 'rewards@bitcoin-foundation-official.org',
        'expected': 'malicious'
    },

    # 6. Arabic - Banking Fraud
    {
        'name': 'SA Arabic - Bank Al-Rajhi Phishing',
        'subject': 'Security Alert: Your account is suspended',
        'body': '''Dear Customer,

Your Al-Rajhi Bank account has been suspended due to suspicious activity. Please update your information immediately to avoid account closure.

Click here to update: http://alrajhi-bank-secure.com/update

Update must be completed within 24 hours.

Al-Rajhi Bank - Customer Service''',
        'sender': 'security@alrajhi-bank-support.com',
        'expected': 'malicious'
    },

    # 7. Turkish - Government Impersonation
    {
        'name': 'TR Turkish - e-Devlet Phishing',
        'subject': 'e-Devlet: Acil Guncelleme Gerekli',
        'body': '''Sayin Vatandasimiz,

e-Devlet hesabinizda guvenlik acigi tespit edilmistir. Hesabinizi korumak icin 24 saat icinde TC Kimlik bilgilerinizi dogrulamaniz gerekmektedir.

Dogrulama linki: http://e-devlet-dogrulama.tk/giris

Bu islemi yapmazsaniz hesabiniz askiya alinacaktir.

T.C. e-Devlet Guvenlik Birimi''',
        'sender': 'guvenlik@e-devlet-turkiye.org',
        'expected': 'malicious'
    },

    # 8. LEGITIMATE - Real company newsletter (should be SAFE)
    {
        'name': 'SAFE - Legitimate Newsletter',
        'subject': 'Your weekly digest from TechCrunch',
        'body': '''Hi there,

Here is your weekly roundup of the biggest tech news:

1. Apple announces new M4 MacBook Pro
2. Google updates Chrome security features
3. Microsoft releases Windows 12 preview

Click to read more on our website: https://techcrunch.com/weekly

To unsubscribe, click here or manage your preferences.

Best,
TechCrunch Team''',
        'sender': 'newsletter@techcrunch.com',
        'expected': 'safe'
    },
]


def run_tests():
    print('=' * 70)
    print('PHISHVISION - GLOBAL AI-POWERED PHISHING DETECTION TEST')
    print('=' * 70)
    print()

    hybrid = create_hybrid_analyzer()
    print()

    correct = 0
    total = len(TEST_CASES)

    for i, test in enumerate(TEST_CASES, 1):
        print(f'[{i}/{total}] {test["name"]}')
        print(f'  Subject: {test["subject"][:50]}...')
        print(f'  Sender: {test["sender"]}')

        try:
            result = hybrid.analyze_email(
                subject=test['subject'],
                body=test['body'],
                sender=test['sender']
            )

            method = result.get('analysis_method', 'unknown')
            classification = result.get('hybrid_classification', result.get('classification', 'unknown'))
            score = result.get('hybrid_risk_score', result.get('risk_score', 0))
            ai_conf = result.get('ai_confidence')

            expected = test['expected']
            is_correct = (expected == 'safe' and classification == 'safe') or \
                         (expected == 'malicious' and classification != 'safe')

            if is_correct:
                correct += 1
                status = 'CORRECT'
            else:
                status = 'WRONG'

            print(f'  Result: {classification.upper()} (Score: {score})')
            print(f'  Method: {method}' + (f', AI Confidence: {ai_conf}' if ai_conf else ''))
            print(f'  [{status}]')

            # Show AI reasoning for interesting cases
            if method in ['hybrid', 'ai'] and result.get('ai_reasoning'):
                reasoning = result.get('ai_reasoning', '')[:100]
                print(f'  AI: {reasoning}...')

        except Exception as e:
            print(f'  ERROR: {str(e)[:100]}')

        print()

    print('=' * 70)
    print(f'RESULTS: {correct}/{total} correct ({100*correct/total:.1f}% accuracy)')
    print('=' * 70)


if __name__ == '__main__':
    run_tests()
