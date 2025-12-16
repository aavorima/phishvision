import re
from typing import Dict, List, Tuple
import json
import math

class NLPAnalyzer:
    """
    Advanced NLP-based email analyzer for phishing detection
    Enhanced with 2024-2025 threat intelligence and patterns
    Supports: English, Turkish, Azerbaijani
    """

    # ============================================
    # ENGLISH KEYWORDS - COMPREHENSIVE
    # ============================================

    URGENT_KEYWORDS = [
        'urgent', 'immediate', 'immediately', 'action required', 'act now', 'act immediately',
        'limited time', 'expire', 'expires', 'expiring', 'expired', 'suspended', 'locked',
        'verify', 'confirm', 'update', 'security alert', 'unusual activity', 'unauthorized',
        'attention required', 'important notice', 'final warning', 'last chance', 'deadline',
        'time sensitive', 'respond immediately', 'within 24 hours', 'within 48 hours',
        'account will be', 'will be suspended', 'will be closed', 'will be terminated',
        'must verify', 'must confirm', 'must update', 'failure to', 'if you do not',
        'your account has been', 'detected suspicious', 'unusual sign-in', 'unrecognized device',
        'require immediate', 'takes only a few minutes', 'avoid interruption', 'prevent suspension',
        'restore access', 'regain access', 'unlock your', 'reactivate your'
    ]

    FINANCIAL_KEYWORDS = [
        'bank', 'account', 'credit card', 'debit card', 'payment', 'invoice', 'refund',
        'transaction', 'billing', 'wire transfer', 'paypal', 'cryptocurrency', 'bitcoin',
        'wallet', 'tax', 'irs', 'direct deposit', 'routing number', 'account number',
        'bank account', 'financial', 'fund', 'funds', 'money', 'transfer', 'withdraw',
        'withdrawal', 'balance', 'outstanding', 'overdue', 'unpaid', 'payment due',
        'past due', 'collection', 'debt', 'charge', 'fee', 'penalty', 'fine',
        'venmo', 'zelle', 'cashapp', 'cash app', 'western union', 'moneygram',
        'bank of america', 'chase', 'wells fargo', 'citibank', 'capital one',
        'credit score', 'credit report', 'tax refund', 'stimulus', 'ach transfer',
        'beneficiary', 'remittance', 'escrow', 'investment', 'trading account'
    ]

    CREDENTIAL_KEYWORDS = [
        'password', 'username', 'login', 'log in', 'signin', 'sign in', 'sign-in',
        'credential', 'credentials', 'authenticate', 'authentication', 'verification code',
        'pin', 'security question', 'social security', 'ssn', 'date of birth', 'dob',
        'mother maiden', 'security code', 'cvv', 'cvc', 'expiration date', 'card number',
        'enter your', 'provide your', 'confirm your', 'verify your', 'update your',
        'reset password', 'change password', 'forgot password', 'recover account',
        'account recovery', 'identity verification', 'verify identity', 'two-factor',
        '2fa', 'mfa', 'one-time password', 'otp', 'verification link', 'secure link',
        'login credentials', 'access credentials', 'user id', 'userid', 'member id'
    ]

    REWARD_KEYWORDS = [
        'winner', 'prize', 'reward', 'congratulations', 'lottery', 'won', 'winning',
        'claim', 'gift card', 'free', 'bonus', 'inheritance', 'beneficiary',
        'you have won', 'you have been selected', 'lucky winner', 'grand prize',
        'cash prize', 'million dollars', 'million pounds', 'unclaimed', 'sweepstakes',
        'contest winner', 'lucky draw', 'jackpot', 'award notification', 'prize claim',
        'compensation', 'settlement', 'grant', 'donation', 'charity fund',
        'exclusive offer', 'special offer', 'limited offer', 'promotional',
        'complimentary', 'no cost', 'zero cost', 'risk free', 'risk-free',
        'free trial', 'free gift', 'free money', 'earn money', 'make money fast'
    ]

    THREAT_KEYWORDS = [
        'suspended', 'terminated', 'locked', 'blocked', 'legal action', 'lawsuit',
        'arrest', 'police', 'investigation', 'fraud', 'fraudulent', 'illegal',
        'violation', 'violating', 'breach', 'unauthorized access', 'compromised',
        'hacked', 'stolen', 'criminal', 'prosecution', 'court order', 'warrant',
        'subpoena', 'law enforcement', 'federal', 'fbi', 'dea', 'cia', 'homeland',
        'interpol', 'consequences', 'penalty', 'penalize', 'terminate', 'deactivate',
        'disable', 'restrict', 'restriction', 'limited access', 'account closure',
        'permanent ban', 'permanently delete', 'legal consequences', 'take legal',
        'report to authorities', 'criminal charges', 'face charges'
    ]

    # Social Engineering / Manipulation Tactics
    SOCIAL_ENGINEERING_KEYWORDS = [
        'do not share', 'do not tell', 'keep this confidential', 'confidential',
        'between us', 'private matter', 'secret', 'discretion', 'discreet',
        'trust me', 'trust you', 'i trust', 'counting on you', 'rely on you',
        'help me', 'need your help', 'favor', 'personal favor', 'urgent favor',
        'can you help', 'assistance needed', 'your assistance', 'kindly help',
        'please help', 'i need you to', 'would you mind', 'can you please',
        'this is important', 'very important', 'extremely important', 'critical',
        'as soon as possible', 'asap', 'right away', 'without delay',
        'do this now', 'handle this', 'take care of this', 'process this'
    ]

    # BEC (Business Email Compromise) / CEO Fraud Keywords
    BEC_KEYWORDS = [
        'wire transfer', 'bank transfer', 'urgent transfer', 'fund transfer',
        'payment request', 'invoice attached', 'attached invoice', 'new bank details',
        'updated bank', 'change of bank', 'new payment', 'new vendor', 'vendor payment',
        'approved payment', 'authorize payment', 'authorize the', 'approval needed',
        'ceo', 'cfo', 'president', 'director', 'executive', 'management',
        'from my mobile', 'from my phone', 'sent from iphone', 'traveling',
        'in a meeting', 'cannot call', 'can not call', "can't call", 'reach me by email',
        'reply to this email only', 'use this email', 'contact me here',
        'keep this quiet', 'between you and me', 'do not discuss',
        'before end of day', 'before close of business', 'eod', 'cob',
        'new instructions', 'change request', 'updated instructions'
    ]

    # Account/Service Related Keywords
    ACCOUNT_KEYWORDS = [
        'account suspended', 'account locked', 'account disabled', 'account terminated',
        'account compromised', 'account verification', 'verify account', 'confirm account',
        'update account', 'account information', 'account details', 'account security',
        'unusual activity', 'suspicious activity', 'unauthorized activity', 'security breach',
        'security update', 'security notice', 'security warning', 'security alert',
        'password expired', 'password reset', 'reset your password', 'change your password',
        'login attempt', 'failed login', 'sign-in attempt', 'access attempt',
        'new device', 'unrecognized device', 'unknown device', 'new location',
        'billing problem', 'payment failed', 'payment declined', 'update payment',
        'subscription expired', 'subscription ending', 'renew subscription'
    ]

    # Spam/Scam Keywords (health, weight loss, etc.)
    # NOTE: Removed legitimate financial terms that appear in real investment newsletters
    SPAM_SCAM_KEYWORDS = [
        'miracle', 'hack', 'cure', 'weight loss', 'lbs', 'tonic', 'hormone',
        'anti-aging', 'weird trick', 'one weird trick', 'doctors hate',
        'lose weight fast', 'belly fat', 'viagra', 'cialis', 'pharmacy', 'pills',
        'diet pill', 'fat burner', 'metabolism', 'detox', 'cleanse',
        'enlargement', 'enhancement', 'potency', 'libido',
        'work from home', 'make money online', 'get rich quick',
        'be your own boss', 'easy money',
        'no experience needed', 'no skills required', 'guaranteed income',
        'double your money', 'guaranteed returns', 'risk-free investment',
        'binary options scam', 'casino', 'gambling', 'slot machine',
        'adult content', 'xxx', 'singles in your area', 'hot singles',
        'meet singles', 'lonely wives', 'affair', 'discreet encounter',
        'nigerian prince', 'wire me money', 'western union', 'moneygram urgent'
    ]

    # Delivery/Shipping Scam Keywords
    DELIVERY_KEYWORDS = [
        'package', 'parcel', 'shipment', 'delivery', 'shipping', 'tracking',
        'courier', 'fedex', 'ups', 'usps', 'dhl', 'amazon delivery', 'royal mail',
        'delivery failed', 'delivery attempt', 'failed delivery', 'undelivered',
        'reschedule delivery', 'confirm delivery', 'delivery confirmation',
        'customs fee', 'customs clearance', 'import duty', 'delivery fee',
        'pay for delivery', 'delivery charges', 'additional charges',
        'tracking number', 'track your package', 'package held', 'package waiting',
        'claim your package', 'collect your parcel'
    ]

    # Tech Support Scam Keywords
    TECH_SUPPORT_KEYWORDS = [
        'virus detected', 'malware detected', 'computer infected', 'system infected',
        'security threat detected', 'trojan detected', 'spyware detected',
        'call microsoft', 'call apple', 'tech support', 'technical support',
        'computer support', 'help desk', 'it support', 'remote access',
        'remote assistance', 'allow access', 'give access', 'grant access',
        'install software', 'download and run', 'run this program',
        'your computer', 'your device', 'your system', 'device compromised',
        'license expired', 'subscription expired', 'renew license', 'activate now',
        'windows defender', 'norton', 'mcafee', 'antivirus expired'
    ]

    # ============================================
    # TURKISH KEYWORDS
    # ============================================

    URGENT_KEYWORDS_TR = [
        'acil', 'hemen', 'dikkat', 'son uyarı', 'askıya', 'beklemede', 'iptal',
        'eylem', 'süre doluyor', 'yetkisiz', 'kısıtlandı', 'engel', 'derhal', 'son gün',
        'acil işlem', 'hemen işlem', 'süre dolmak üzere', 'hesabınız askıya',
        'hesabınız kapatılacak', 'erişiminiz engellenecek', '24 saat içinde',
        '48 saat içinde', 'gecikmeden', 'vakit kaybetmeden', 'son şans',
        'son fırsat', 'kaçırmayın', 'acil onay', 'derhal onaylayın'
    ]

    FINANCIAL_KEYWORDS_TR = [
        'fatura', 'ödeme', 'dekont', 'banka', 'para iadesi', 'borç', 'havale',
        'eft', 'maaş', 'hesap özeti', 'makbuz', 'kredi', 'tutar', 'aidat', 'vergi',
        'kredi kartı', 'banka kartı', 'hesap numarası', 'iban', 'swift',
        'para transferi', 'bakiye', 'gecikmiş ödeme', 'ödenmemiş', 'icra',
        'tahsilat', 'ceza', 'faiz', 'taksit', 'kredi notu', 'banka hesabı'
    ]

    CREDENTIAL_KEYWORDS_TR = [
        'şifre', 'giriş yap', 'parola', 'doğrula', 'kimlik', 'hesap',
        'güncelleme', 'güvenlik', 'erişim', 'doğrulama kodu', 'pin', 'oturum', 'hesabım',
        'şifre sıfırlama', 'şifre değiştirme', 'hesap kurtarma', 'kimlik doğrulama',
        'kullanıcı adı', 'üye girişi', 'giriş bilgileri', 'tc kimlik', 'tc no',
        'doğum tarihi', 'anne kızlık', 'güvenlik sorusu', 'tek kullanımlık şifre'
    ]

    REWARD_KEYWORDS_TR = [
        'tebrikler', 'kazandınız', 'hediye', 'çekiliş', 'ödül', 'ücretsiz',
        'fırsat', 'kampanya', 'bonus', 'talihli', 'bedava', 'şanslı kazanan',
        'büyük ödül', 'nakit ödül', 'hediye çeki', 'indirim kuponu',
        'özel teklif', 'sınırlı teklif', 'kaçırılmayacak fırsat'
    ]

    THREAT_KEYWORDS_TR = [
        'yasal işlem', 'icra', 'mahkeme', 'polis', 'cezai', 'avukat',
        'soruşturma', 'bloke', 'tutuklama', 'dava', 'savcılık', 'haciz',
        'yasal takip', 'hukuki süreç', 'ceza davası', 'suç duyurusu',
        'hesap dondurma', 'hesap kapatma', 'erişim engeli', 'kalıcı engel'
    ]

    # Turkish Delivery Scam Keywords
    DELIVERY_KEYWORDS_TR = [
        'kargo', 'paket', 'gönderi', 'teslimat', 'teslim', 'sipariş', 'takip',
        'kurye', 'ptt', 'yurtiçi', 'aras', 'mng', 'sürat', 'ups', 'dhl', 'fedex',
        'teslimat başarısız', 'teslim edilemedi', 'adresinize', 'gümrük',
        'gümrük ücreti', 'ödeme bekliyor', 'teslim almak', 'tıklayın',
        'paketiniz', 'kargonuz', 'gönderiniz', 'takip numarası', 'takip kodu',
        'bekletiliyor', 'depoda', 'şubede', 'iade edilecek', 'son gün',
        'teslim adresi', 'adres güncelleme', 'ödeme yapın', 'işlem ücreti',
        'doğrulama', 'onaylayın', 'hemen tıklayın', 'link', 'butona tıklayın'
    ]

    # ============================================
    # AZERBAIJANI KEYWORDS
    # ============================================

    URGENT_KEYWORDS_AZ = [
        'təcili', 'dərhal', 'diqqət', 'son xəbərdarlıq', 'bloklanıb', 'deaktiv',
        'vaxt bitir', 'xəta', 'vacib', 'əməliyyat', 'dayandırılıb', 'dondurulub',
        'təcili tədbirlər', 'gecikmədən', '24 saat ərzində', 'son müddət',
        'hesabınız dayandırılacaq', 'giriş bloklanacaq'
    ]

    FINANCIAL_KEYWORDS_AZ = [
        'faktura', 'ödəniş', 'qaimə', 'borc', 'köçürmə', 'balans', 'maaş',
        'kredit', 'vergi', 'cərimə', 'hesabdan çıxarış', 'məbləğ', 'qəbz', 'kart',
        'bank hesabı', 'kredit kartı', 'pul köçürməsi', 'iban', 'hesab nömrəsi'
    ]

    CREDENTIAL_KEYWORDS_AZ = [
        'şifrə', 'giriş', 'parol', 'təsdiq', 'kod', 'hesab', 'istifadəçi',
        'bərpa', 'yeniləyin', 'təhlükəsizlik', 'pin', 'imza', 'profil',
        'şifrə sıfırlama', 'hesab bərpası', 'kimlik təsdiqi'
    ]

    REWARD_KEYWORDS_AZ = [
        'təbriklər', 'qazandınız', 'hədiyyə', 'mükafat', 'uduş', 'bonus',
        'pulsuz', 'qalib', 'aksiya', 'lotereya', 'şans', 'xüsusi təklif'
    ]

    THREAT_KEYWORDS_AZ = [
        'məhkəmə', 'hüquq', 'polis', 'cəza', 'həbs', 'xəbərdarlıq',
        'qadağa', 'təhqiqat', 'qanun', 'prokurorluq', 'cinayət',
        'hesab bağlama', 'giriş qadağası'
    ]

    # ============================================
    # PHISHING PHRASES (High Confidence Indicators)
    # ============================================

    PHISHING_PHRASES = [
        # Account threats
        'your account has been compromised',
        'your account will be suspended',
        'your account has been locked',
        'we detected unusual activity',
        'we noticed suspicious activity',
        'unauthorized access to your account',
        'someone tried to access your account',
        'your account requires verification',
        'verify your account immediately',
        'confirm your identity',
        'update your information',
        'update your payment method',
        'your payment method has expired',
        'billing information needs to be updated',

        # Action demands
        'click here to verify',
        'click here to confirm',
        'click the link below',
        'click the button below',
        'click here immediately',
        'follow this link',
        'open the attachment',
        'download the attachment',
        'see attached document',
        'review attached invoice',
        'please find attached',

        # Fear/Urgency
        'failure to verify will result',
        'if you do not respond',
        'your access will be terminated',
        'avoid account suspension',
        'prevent account closure',
        'this is your final notice',
        'last reminder before action',
        'immediate action required',
        'respond within 24 hours',
        'act within 48 hours',

        # Fake legitimacy
        'this is not a scam',
        'this is legitimate',
        'this is not spam',
        'official notification',
        'official communication',
        'from the security team',
        'from customer support',
        'from account services',

        # Reward scams
        'you have been selected',
        'you have won',
        'claim your prize',
        'claim your reward',
        'collect your winnings',

        # BEC phrases
        'i need you to handle',
        'please process this payment',
        'wire the funds',
        'transfer the amount',
        'update the bank details',
        'new payment instructions',
        'confidential transaction',
        'keep this between us',
        'do not discuss with anyone',
        'i am in a meeting',
        'contact me by email only',

        # Bank phishing phrases (from threat intel dataset)
        'confirm your personal information',
        'notification of limited account access',
        'update your account information',
        'security measures notification',
        'unusual activity on your account',
        'verify your identity',
        'confirm your identity account',
        'secure your account',
        'security issues',
        'update your information',
        'your account has been limited',
        'your account access has been limited',
        'restore full access',
        'secure details confirmation',
        'account security measures',
        'important security notification',
        'member services notification',
        'online banking services',
        'protect your account',
        'account may be suspended',
        'immediate attention required',
        'we need to update your information',
        'confirm your account details',
        'please confirm your identity',
        'verification required',
        'account verification required',
        'security department',
        'fraud prevention',
        'unauthorized transaction',
        'suspicious login attempt',

        # eBay phishing phrases
        'your ebay account',
        'ebay member',
        'ebay billing',
        'question from ebay member',
        'ebay suspension notice',
        'ebay security',
        'ebay verification',

        # PayPal phishing phrases
        'paypal account limited',
        'paypal account suspended',
        'paypal security',
        'paypal member',
        'restore your paypal',
        'paypal notification',
        'access to your paypal'
    ]

    # ============================================
    # BRAND IMPERSONATION
    # ============================================

    IMPERSONATED_BRANDS = [
        'microsoft', 'apple', 'google', 'amazon', 'facebook', 'meta', 'instagram',
        'whatsapp', 'netflix', 'spotify', 'paypal', 'venmo', 'cashapp', 'zelle',
        'chase', 'bank of america', 'wells fargo', 'citibank', 'capital one',
        'american express', 'amex', 'visa', 'mastercard', 'discover',
        'fedex', 'ups', 'usps', 'dhl', 'royal mail',
        'dropbox', 'docusign', 'adobe', 'zoom', 'slack', 'teams',
        'linkedin', 'twitter', 'x.com', 'tiktok', 'snapchat',
        'walmart', 'target', 'bestbuy', 'ebay', 'alibaba',
        'office365', 'outlook', 'onedrive', 'sharepoint',
        'icloud', 'apple id', 'itunes', 'app store',
        'gmail', 'youtube', 'google drive', 'google docs',
        # Banks from phishing dataset (2024-2025 threat intel)
        'southtrust', 'south trust', 'keybank', 'key bank', 'regions', 'regions bank',
        'fifth third', 'fifth third bank', 'national city', 'national city bank',
        'suntrust', 'sun trust', 'citizens bank', 'charter one', 'charter one bank',
        'td bank', 'td ameritrade', 'pnc', 'pnc bank', 'bb&t', 'truist',
        'huntington', 'huntington bank', 'us bank', 'usbank', 'ally', 'ally bank',
        'synchrony', 'discover bank', 'marcus', 'goldman sachs', 'barclays'
    ]

    # Typosquatting patterns for major brands
    TYPOSQUAT_PATTERNS = {
        'microsoft': ['micros0ft', 'mircosoft', 'microsft', 'micosoft', 'microsoftt', 'rnicrosoft', 'mlcrosoft'],
        'apple': ['appie', 'app1e', 'applle', 'aple', 'appel', 'ápple', 'àpple'],
        'google': ['googie', 'g00gle', 'gooogle', 'googel', 'gogle', 'qoogle'],
        'amazon': ['amaz0n', 'arnazon', 'amazom', 'amazone', 'arnezon', 'arnazom'],
        'paypal': ['paypa1', 'paypai', 'paypol', 'paypaI', 'peypal', 'paypaI', 'paypall', 'pay-pal'],
        'facebook': ['faceb00k', 'facebok', 'faecbook', 'facebbok', 'faceboook'],
        'netflix': ['netfIix', 'netfiix', 'netf1ix', 'netfilx', 'netfliix'],
        'linkedin': ['linkedln', 'linkdin', 'linkediin', 'iinkedin', 'l1nkedin'],
        'dropbox': ['dr0pbox', 'dropb0x', 'drobox', 'drapbox', 'dropbax'],
        'docusign': ['d0cusign', 'docusing', 'docusiqn', 'docus1gn', 'docuslgn'],
        # Bank typosquatting (from threat intel dataset)
        'ebay': ['ebey', 'eaby', 'e-bay', 'ebav', 'ebày', 'ébay'],
        'chase': ['chas3', 'chasse', 'chase-bank', 'cha5e'],
        'wellsfargo': ['wells-fargo', 'wellsfarg0', 'we11sfargo', 'weilsfargo'],
        'citibank': ['c1tibank', 'citibanк', 'citi-bank', 'citib4nk'],
        'regions': ['reg1ons', 'reglons', 'regions-bank'],
        'keybank': ['k3ybank', 'keyb4nk', 'key-bank'],
        'fifththird': ['5thth1rd', 'fifthth1rd', 'fifth-third']
    }

    # ============================================
    # HOMOGLYPH / UNICODE CHARACTERS
    # ============================================

    # Cyrillic characters that look like Latin
    HOMOGLYPHS = {
        'а': 'a',  # Cyrillic а
        'е': 'e',  # Cyrillic е
        'о': 'o',  # Cyrillic о
        'р': 'p',  # Cyrillic р
        'с': 'c',  # Cyrillic с
        'х': 'x',  # Cyrillic х
        'у': 'y',  # Cyrillic у
        'і': 'i',  # Ukrainian і
        'ј': 'j',  # Cyrillic ј
        'ԁ': 'd',  # Cyrillic ԁ
        'ɡ': 'g',  # Latin small letter script g
        'ո': 'n',  # Armenian ո
        'ν': 'v',  # Greek nu
        'ω': 'w',  # Greek omega
        'ḷ': 'l',  # l with dot below
        'ṃ': 'm',  # m with dot below
        'ṅ': 'n',  # n with dot above
        'ạ': 'a',  # a with dot below
        'ẹ': 'e',  # e with dot below
        'ọ': 'o',  # o with dot below
    }

    # ============================================
    # FILE EXTENSIONS
    # ============================================

    MALICIOUS_EXTENSIONS = ['.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js', '.jse', '.wsf', '.wsh', '.ps1', '.msi']
    HIGH_RISK_EXTENSIONS = ['.eml', '.html', '.htm', '.hta', '.mht', '.mhtml', '.svg', '.xll', '.xlam']
    MEDIUM_RISK_EXTENSIONS = ['.zip', '.rar', '.7z', '.iso', '.jar', '.tar', '.gz', '.ace', '.cab']
    DOCUMENT_MACROS = ['.docm', '.xlsm', '.pptm', '.dotm', '.xltm', '.potm']

    # ============================================
    # SUSPICIOUS TLDs
    # ============================================

    SUSPICIOUS_TLDS = [
        '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work', '.click',
        '.link', '.info', '.biz', '.cc', '.ws', '.pw', '.buzz', '.icu',
        '.monster', '.cam', '.fun', '.space', '.site', '.online', '.live',
        '.club', '.vip', '.win', '.loan', '.racing', '.review', '.science',
        '.download', '.stream', '.cricket', '.party', '.gdn', '.men',
        # Additional high-risk TLDs
        '.us', '.ru', '.cn', '.su', '.br', '.in', '.pk', '.ng', '.za',
        '.bid', '.trade', '.date', '.faith', '.accountant', '.cricket',
        '.pro', '.rocks', '.world', '.today', '.ninja', '.guru', '.zone',
        '.one', '.mobi', '.tech', '.store', '.shop', '.website', '.host'
    ]

    URL_SHORTENERS = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly',
        'adf.ly', 'j.mp', 'tr.im', 'cli.gs', 'short.to', 'budurl.com', 'ping.fm',
        'post.ly', 'just.as', 'bkite.com', 'snipr.com', 'fic.kr', 'loopt.us',
        'doiop.com', 'short.ie', 'kl.am', 'wp.me', 'rubyurl.com', 'om.ly',
        'to.ly', 'bit.do', 'lnkd.in', 'db.tt', 'qr.ae', 'adf.ly', 'bitly.com',
        'cutt.ly', 'rb.gy', 'shorturl.at', 'tinycc.com', 'shortcm.li'
    ]

    # ============================================
    # TRUSTED AUTHENTICATED DOMAINS
    # When emails from these domains pass DKIM/SPF/DMARC, trust them highly
    # ============================================
    TRUSTED_AUTHENTICATED_DOMAINS = {
        # E-commerce
        'amazon.com': ['amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.fr', 'amazon.es', 'amazon.it', 'amazon.ca', 'amazon.co.jp', 'amazonses.com'],
        'ebay.com': ['ebay.com', 'ebay.co.uk', 'ebay.de'],
        'walmart.com': ['walmart.com'],
        'target.com': ['target.com'],
        'bestbuy.com': ['bestbuy.com'],
        'etsy.com': ['etsy.com'],
        'shopify.com': ['shopify.com', 'myshopify.com'],

        # Tech companies
        'microsoft.com': ['microsoft.com', 'outlook.com', 'hotmail.com', 'live.com', 'office365.com', 'microsoftonline.com'],
        'apple.com': ['apple.com', 'icloud.com', 'me.com', 'mac.com'],
        'google.com': ['google.com', 'gmail.com', 'youtube.com', 'googlemail.com'],
        'facebook.com': ['facebook.com', 'fb.com', 'meta.com', 'instagram.com', 'whatsapp.com'],
        'twitter.com': ['twitter.com', 'x.com'],
        'linkedin.com': ['linkedin.com'],
        'netflix.com': ['netflix.com'],
        'spotify.com': ['spotify.com'],
        'adobe.com': ['adobe.com'],
        'dropbox.com': ['dropbox.com'],
        'zoom.us': ['zoom.us', 'zoom.com'],
        'slack.com': ['slack.com'],

        # Financial
        'paypal.com': ['paypal.com'],
        'chase.com': ['chase.com', 'jpmorgan.com'],
        'bankofamerica.com': ['bankofamerica.com', 'bofa.com'],
        'wellsfargo.com': ['wellsfargo.com'],
        'citibank.com': ['citibank.com', 'citi.com'],
        'capitalone.com': ['capitalone.com'],
        'americanexpress.com': ['americanexpress.com', 'aexp.com'],
        'discover.com': ['discover.com'],
        'venmo.com': ['venmo.com'],
        'stripe.com': ['stripe.com'],
        'square.com': ['square.com', 'squareup.com'],

        # Shipping
        'fedex.com': ['fedex.com'],
        'ups.com': ['ups.com'],
        'usps.com': ['usps.com', 'usps.gov'],
        'dhl.com': ['dhl.com'],
    }

    # ============================================
    # LEGITIMATE EMAIL PLATFORMS (Newsletter/Marketing)
    # ============================================

    LEGITIMATE_NEWSLETTER_DOMAINS = [
        # Email marketing platforms
        'mailchimp.com', 'mail.mailchimp.com', 'mailchi.mp', 'list-manage.com',
        'sendgrid.net', 'sendgrid.com',
        'constantcontact.com', 'ccsend.com',
        'mailgun.com', 'mailgun.net',
        'sendinblue.com', 'sibautomation.com',
        'hubspot.com', 'hubspotmail.com', 'hs-email.com',
        'marketo.com', 'mktomail.com',
        'pardot.com',
        'campaignmonitor.com', 'cmail.com', 'createsend.com',
        'aweber.com',
        'getresponse.com',
        'klaviyo.com',
        'drip.com',
        'activecampaign.com',
        'convertkit.com',
        'moosend.com',
        'mailjet.com',
        'zoho.com', 'zohomail.com',
        'postmarkapp.com',
        'sparkpost.com',
        'amazonses.com',
        # Financial news platforms
        'substack.com',
        'bloomberg.com', 'bloomberg.net',
        'reuters.com', 'thomsonreuters.com',
        'wsj.com', 'dowjones.com',
        'marketwatch.com',
        'morningstar.com',
        'seekingalpha.com',
        'fool.com',  # Motley Fool
        'investopedia.com',
        'yahoo.com',  # Yahoo Finance
        'cnbc.com',
        'cnn.com',
        'forbes.com',
    ]

    # Words that indicate discussing/analyzing (not impersonating)
    NEWSLETTER_CONTEXT_WORDS = [
        'stock', 'stocks', 'share', 'shares', 'market', 'markets', 'trading',
        'investor', 'investors', 'investing', 'invest', 'portfolio',
        'analysis', 'analyst', 'analysts', 'forecast', 'outlook',
        'quarterly', 'earnings', 'revenue', 'profit', 'growth',
        'performance', 'sector', 'industry', 'economy', 'economic',
        'bull', 'bear', 'bullish', 'bearish', 'rally', 'correction',
        'dividend', 'yield', 'p/e', 'ratio', 'valuation',
        'news', 'update', 'weekly', 'daily', 'monthly', 'report',
        'nasdaq', 'nyse', 's&p', 'dow jones', 'index', 'indices',
        'buy rating', 'sell rating', 'hold rating', 'target price',
        'recommendation', 'recommends', 'upgrade', 'downgrade'
    ]

    def __init__(self):
        # Combine all keywords for comprehensive analysis
        self.all_urgent = (self.URGENT_KEYWORDS + self.URGENT_KEYWORDS_TR +
                          self.URGENT_KEYWORDS_AZ + self.ACCOUNT_KEYWORDS)
        self.all_financial = (self.FINANCIAL_KEYWORDS + self.FINANCIAL_KEYWORDS_TR +
                             self.FINANCIAL_KEYWORDS_AZ + self.BEC_KEYWORDS)
        self.all_credentials = (self.CREDENTIAL_KEYWORDS + self.CREDENTIAL_KEYWORDS_TR +
                               self.CREDENTIAL_KEYWORDS_AZ)
        self.all_rewards = (self.REWARD_KEYWORDS + self.REWARD_KEYWORDS_TR +
                           self.REWARD_KEYWORDS_AZ)
        self.all_threats = (self.THREAT_KEYWORDS + self.THREAT_KEYWORDS_TR +
                           self.THREAT_KEYWORDS_AZ)
        # Include Turkish delivery scam keywords
        self.all_spam_scam = (self.SPAM_SCAM_KEYWORDS + self.DELIVERY_KEYWORDS +
                             self.DELIVERY_KEYWORDS_TR + self.TECH_SUPPORT_KEYWORDS)
        self.all_social_engineering = self.SOCIAL_ENGINEERING_KEYWORDS

    def _parse_email_authentication(self, headers: str, sender: str) -> Dict:
        """
        Parse email authentication headers (DKIM, SPF, DMARC) and determine trust level.
        When authentication passes from a trusted domain, significantly increase trust.
        """
        auth_result = {
            'dkim_pass': False,
            'dkim_domain': None,
            'spf_pass': False,
            'dmarc_pass': False,
            'is_trusted_sender': False,
            'trusted_brand': None,
            'trust_score': 0,  # 0-100, higher = more trusted
            'auth_reasons': []
        }

        headers_lower = headers.lower() if headers else ''
        sender_lower = sender.lower()

        # Parse DKIM results
        # Common patterns: "dkim=pass", "dkim: pass", "Authentication-Results: ... dkim=pass"
        dkim_pass_patterns = [
            r'dkim\s*[=:]\s*pass',
            r'dkim-signature.*pass',
            r'authentication-results:.*dkim=pass'
        ]
        for pattern in dkim_pass_patterns:
            if re.search(pattern, headers_lower):
                auth_result['dkim_pass'] = True
                auth_result['auth_reasons'].append('DKIM authentication passed')
                # Try to extract DKIM signing domain
                dkim_domain_match = re.search(r'd=([a-zA-Z0-9.-]+)', headers_lower)
                if dkim_domain_match:
                    auth_result['dkim_domain'] = dkim_domain_match.group(1)
                break

        # Parse SPF results
        spf_pass_patterns = [
            r'spf\s*[=:]\s*pass',
            r'received-spf:\s*pass',
            r'authentication-results:.*spf=pass'
        ]
        for pattern in spf_pass_patterns:
            if re.search(pattern, headers_lower):
                auth_result['spf_pass'] = True
                auth_result['auth_reasons'].append('SPF authentication passed')
                break

        # Parse DMARC results
        dmarc_pass_patterns = [
            r'dmarc\s*[=:]\s*pass',
            r'authentication-results:.*dmarc=pass'
        ]
        for pattern in dmarc_pass_patterns:
            if re.search(pattern, headers_lower):
                auth_result['dmarc_pass'] = True
                auth_result['auth_reasons'].append('DMARC authentication passed')
                break

        # Determine sender domain
        sender_domain = None
        domain_match = re.search(r'@([a-zA-Z0-9.-]+)', sender_lower)
        if domain_match:
            sender_domain = domain_match.group(1)

        # Check if sender is from a trusted domain with passing authentication
        if sender_domain:
            for brand, trusted_domains in self.TRUSTED_AUTHENTICATED_DOMAINS.items():
                for trusted_domain in trusted_domains:
                    if sender_domain.endswith(trusted_domain) or sender_domain == trusted_domain:
                        # Sender domain matches a trusted brand
                        # Calculate trust based on authentication results
                        trust_points = 0

                        if auth_result['dkim_pass']:
                            trust_points += 40
                            # Extra trust if DKIM domain matches sender domain
                            if auth_result['dkim_domain'] and trusted_domain in auth_result['dkim_domain']:
                                trust_points += 20

                        if auth_result['spf_pass']:
                            trust_points += 20

                        if auth_result['dmarc_pass']:
                            trust_points += 20

                        # If all three pass, it's highly trusted
                        if auth_result['dkim_pass'] and auth_result['spf_pass'] and auth_result['dmarc_pass']:
                            auth_result['is_trusted_sender'] = True
                            auth_result['trusted_brand'] = brand
                            auth_result['trust_score'] = min(trust_points, 100)
                            auth_result['auth_reasons'].append(f'Verified sender from trusted brand: {brand}')
                        elif trust_points >= 40:
                            # Partial trust if at least DKIM passes
                            auth_result['is_trusted_sender'] = True
                            auth_result['trusted_brand'] = brand
                            auth_result['trust_score'] = trust_points
                            auth_result['auth_reasons'].append(f'Partially verified sender from: {brand}')

                        break
                if auth_result['is_trusted_sender']:
                    break

        return auth_result

    def analyze_email(self, subject: str, body: str, sender: str,
                     attachments: List[str] = None, headers: str = "") -> Dict:
        """
        Comprehensive email analysis with advanced phishing detection
        """
        # Combine and normalize text
        full_text = f"{subject} {body}".lower()
        original_text = f"{subject} {body}"  # Keep original for case analysis

        # FIRST: Parse email authentication to determine trust level
        auth_result = self._parse_email_authentication(headers, sender)

        # SECOND: Detect if this is a legitimate newsletter
        newsletter_context = self._detect_newsletter_context(sender, full_text, headers)

        # Perform all checks
        suspicious_keywords = self._find_suspicious_keywords(full_text)
        phishing_phrases = self._detect_phishing_phrases(full_text)
        urgency_score = self._calculate_urgency_score(full_text, original_text)
        urls = self._extract_urls(body)
        url_analysis = self._analyze_urls(urls, full_text)
        sender_analysis = self._analyze_sender(sender, subject)
        brand_impersonation = self._detect_brand_impersonation(full_text, sender)
        homoglyph_analysis = self._detect_homoglyphs(sender, subject, body)
        attachment_analysis = self._analyze_attachments(attachments or [])
        encoding_analysis = self._analyze_encoding_obfuscation(sender, subject, headers)
        image_heavy_analysis = self._analyze_image_heavy_ratio(body)
        spam_score = self._calculate_spam_score(full_text)
        link_text_mismatch = self._detect_link_text_mismatch(body)

        # Calculate risk score (pass newsletter context and auth result for adjustment)
        risk_score = self._calculate_risk_score(
            suspicious_keywords, phishing_phrases, urgency_score, url_analysis,
            sender_analysis, brand_impersonation, homoglyph_analysis,
            attachment_analysis, encoding_analysis, image_heavy_analysis,
            spam_score, link_text_mismatch, newsletter_context, auth_result
        )

        # Classify email
        classification = self._classify_risk(risk_score)

        # Generate explanation
        explanation = self._generate_explanation(
            risk_score, classification, suspicious_keywords, phishing_phrases,
            urgency_score, url_analysis, sender_analysis, brand_impersonation,
            homoglyph_analysis, attachment_analysis, encoding_analysis,
            image_heavy_analysis, spam_score, link_text_mismatch, newsletter_context,
            auth_result
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(classification, risk_score, auth_result)

        return {
            'risk_score': round(risk_score, 2),
            'classification': classification,
            'suspicious_keywords': json.dumps(suspicious_keywords),
            'url_analysis': json.dumps(url_analysis),
            'urgency_score': round(urgency_score, 2),
            'attachment_analysis': json.dumps(attachment_analysis),
            'encoding_analysis': json.dumps(encoding_analysis),
            'brand_impersonation': json.dumps(brand_impersonation),
            'phishing_phrases_detected': json.dumps(phishing_phrases),
            'explanation': explanation,
            'recommendations': json.dumps(recommendations),
            'newsletter_context': json.dumps(newsletter_context) if newsletter_context['is_newsletter'] else None,
            'email_authentication': json.dumps(auth_result)
        }

    def _detect_newsletter_context(self, sender: str, text: str, headers: str = "") -> Dict:
        """
        Detect if email is from a legitimate newsletter/marketing platform.
        This significantly reduces false positives for investment newsletters,
        marketing emails, and other legitimate bulk mail.
        """
        analysis = {
            'is_newsletter': False,
            'platform_detected': None,
            'context_score': 0,  # How "newsletter-like" is this email
            'reasons': []
        }

        sender_lower = sender.lower()
        combined = f"{sender} {headers}".lower()

        # Check if sender is from known newsletter platform
        for platform in self.LEGITIMATE_NEWSLETTER_DOMAINS:
            if platform in sender_lower or platform in combined:
                analysis['is_newsletter'] = True
                analysis['platform_detected'] = platform
                analysis['reasons'].append(f'Sent via legitimate platform: {platform}')
                analysis['context_score'] += 50
                break

        # Check for newsletter context words (investment/financial content)
        context_word_count = 0
        for word in self.NEWSLETTER_CONTEXT_WORDS:
            if word in text:
                context_word_count += 1

        # If many newsletter context words, likely a newsletter
        if context_word_count >= 5:
            analysis['context_score'] += min(context_word_count * 3, 30)
            analysis['reasons'].append(f'Contains {context_word_count} newsletter/financial context words')

        # Check for common newsletter indicators in headers/body
        newsletter_indicators = [
            'unsubscribe', 'manage preferences', 'email preferences',
            'opt-out', 'opt out', 'subscription', 'mailing list',
            'view in browser', 'view online', 'web version',
            'this email was sent', 'you received this', 'you are receiving',
            'weekly newsletter', 'daily digest', 'monthly update',
            'investment newsletter', 'market update', 'stock update'
        ]

        indicator_count = 0
        for indicator in newsletter_indicators:
            if indicator in text:
                indicator_count += 1

        if indicator_count >= 2:
            analysis['context_score'] += min(indicator_count * 8, 25)
            analysis['reasons'].append(f'Contains {indicator_count} newsletter indicators (unsubscribe, etc.)')

        # Final determination: if context score is high enough, mark as newsletter
        if analysis['context_score'] >= 30:
            analysis['is_newsletter'] = True

        return analysis

    def _find_suspicious_keywords(self, text: str) -> Dict[str, List[str]]:
        """Find suspicious keywords in text using word boundary matching"""
        found = {
            'urgent': [],
            'financial': [],
            'credentials': [],
            'rewards': [],
            'threats': [],
            'spam_scam': [],
            'social_engineering': []
        }

        # Use word boundary matching for better accuracy
        for keyword in self.all_urgent:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if keyword not in found['urgent']:
                    found['urgent'].append(keyword)

        for keyword in self.all_financial:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if keyword not in found['financial']:
                    found['financial'].append(keyword)

        for keyword in self.all_credentials:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if keyword not in found['credentials']:
                    found['credentials'].append(keyword)

        for keyword in self.all_rewards:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if keyword not in found['rewards']:
                    found['rewards'].append(keyword)

        for keyword in self.all_threats:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if keyword not in found['threats']:
                    found['threats'].append(keyword)

        for keyword in self.all_spam_scam:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if keyword not in found['spam_scam']:
                    found['spam_scam'].append(keyword)

        for keyword in self.all_social_engineering:
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if keyword not in found['social_engineering']:
                    found['social_engineering'].append(keyword)

        return found

    def _detect_phishing_phrases(self, text: str) -> List[str]:
        """Detect known phishing phrases - high confidence indicators"""
        detected = []
        for phrase in self.PHISHING_PHRASES:
            if phrase.lower() in text.lower():
                detected.append(phrase)
        return detected

    def _calculate_urgency_score(self, text: str, original_text: str) -> float:
        """Calculate urgency score with improved detection"""
        score = 0

        # Check for urgent keywords (increased weight)
        urgent_count = sum(1 for kw in self.URGENT_KEYWORDS if kw in text)
        score += min(urgent_count * 12, 35)

        # Time pressure patterns
        time_patterns = [
            (r'\b(\d+)\s*(hour|hours|hr|hrs)\b', 15),
            (r'\b(\d+)\s*(day|days)\b', 12),
            (r'\b(\d+)\s*(minute|minutes|min|mins)\b', 18),
            (r'\b(immediately|asap|right away|right now|now)\b', 15),
            (r'\b(expire|expires|expiring|expired)\b', 12),
            (r'\b(urgent|urgently)\b', 15),
            (r'\bwithin\s+\d+\s+(hours?|days?|minutes?)\b', 15),
            (r'\b(deadline|due date|final)\b', 10),
            (r'\b(today|tonight|tomorrow)\b', 8),
            (r'\b(last chance|final warning|final notice)\b', 18),
        ]

        for pattern, points in time_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += points

        # Excessive punctuation (!!!, ???)
        exclamation_count = len(re.findall(r'!', original_text))
        if exclamation_count >= 3:
            score += min(exclamation_count * 3, 15)

        # ALL CAPS detection
        caps_words = re.findall(r'\b[A-Z]{4,}\b', original_text)
        if len(caps_words) >= 2:
            score += min(len(caps_words) * 5, 20)

        # Action demand phrases
        action_patterns = [
            r'\b(must|required|need to|have to)\s+(verify|confirm|update|act|respond)\b',
            r'\b(click|tap|press)\s+(here|now|below|the link|the button)\b',
            r'\bdo not ignore\b',
            r'\bimmediate action\b',
            r'\bact now\b',
        ]

        for pattern in action_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 12

        return min(score, 100)

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"\')\]]+|www\.[^\s<>"\')\]]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        return [url.rstrip('.,;:') for url in urls]

    def _analyze_urls(self, urls: List[str], text: str) -> Dict:
        """Enhanced URL analysis with typosquatting detection"""
        analysis = {
            'total_urls': len(urls),
            'suspicious_urls': [],
            'suspicious_patterns': [],
            'typosquatting_detected': False,
            'url_shortener_detected': False
        }

        for url in urls:
            url_lower = url.lower()
            suspicious = False
            reasons = []

            # IP address instead of domain
            if re.search(r'://\d+\.\d+\.\d+\.\d+', url):
                suspicious = True
                reasons.append('Uses IP address instead of domain')

            # Suspicious TLDs
            for tld in self.SUSPICIOUS_TLDS:
                if url_lower.endswith(tld) or f'{tld}/' in url_lower or f'{tld}?' in url_lower:
                    suspicious = True
                    reasons.append(f'High-risk TLD: {tld}')
                    break

            # URL shorteners
            for shortener in self.URL_SHORTENERS:
                if shortener in url_lower:
                    suspicious = True
                    analysis['url_shortener_detected'] = True
                    reasons.append(f'URL shortener: {shortener}')
                    break

            # Very long URLs
            if len(url) > 100:
                suspicious = True
                reasons.append('Unusually long URL (may hide real destination)')

            # @ symbol in URL
            if '@' in url:
                suspicious = True
                reasons.append('@ symbol in URL (basic auth spoofing)')

            # Typosquatting detection - use word boundary matching to avoid false positives
            # e.g., "AmazonEmber" (Amazon's font) should NOT match "amazone" typosquat
            for brand, typos in self.TYPOSQUAT_PATTERNS.items():
                for typo in typos:
                    # Use word boundary regex to match whole words/domains only
                    # This prevents "amazonember" from matching "amazone"
                    if re.search(rf'\b{re.escape(typo)}\b', url_lower) or \
                       re.search(rf'{re.escape(typo)}[.\-/]', url_lower) or \
                       url_lower.endswith(typo):
                        suspicious = True
                        analysis['typosquatting_detected'] = True
                        reasons.append(f'Typosquatting detected: "{typo}" impersonating {brand}')
                        break

            # Multiple subdomains (e.g., login.microsoft.com.malicious.tk)
            subdomain_count = url_lower.count('.')
            if subdomain_count >= 4:
                suspicious = True
                reasons.append('Excessive subdomains (domain spoofing attempt)')

            # Suspicious keywords in URL path
            url_keywords = ['login', 'signin', 'verify', 'secure', 'account', 'update', 'confirm', 'authenticate']
            for kw in url_keywords:
                if kw in url_lower and not any(brand in url_lower for brand in self.IMPERSONATED_BRANDS):
                    if 'suspicious keyword' not in str(reasons):
                        reasons.append(f'Suspicious keyword in URL: {kw}')
                    break

            # Numeric domain (e.g., 192312.com)
            domain_match = re.search(r'://([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                if re.match(r'^\d+\.', domain):
                    suspicious = True
                    reasons.append('Domain starts with numbers')

            # Hexadecimal encoding in URL
            if '%' in url and re.search(r'%[0-9a-fA-F]{2}', url):
                encoded_count = len(re.findall(r'%[0-9a-fA-F]{2}', url))
                if encoded_count > 5:
                    suspicious = True
                    reasons.append('Excessive URL encoding (obfuscation attempt)')

            if suspicious or reasons:
                analysis['suspicious_urls'].append({
                    'url': url[:100],
                    'reasons': reasons
                })
                analysis['suspicious_patterns'].extend(reasons)

        return analysis

    def _analyze_sender(self, sender: str, subject: str) -> Dict:
        """Enhanced sender analysis"""
        analysis = {
            'is_suspicious': False,
            'reasons': [],
            'spoofing_indicators': []
        }

        sender_lower = sender.lower()

        # Display name vs email mismatch
        if '<' in sender and '>' in sender:
            display_name = sender.split('<')[0].strip().lower()
            email_part = sender.split('<')[1].split('>')[0].lower()

            # Check for brand in display name but not in email
            for brand in self.IMPERSONATED_BRANDS:
                if brand in display_name and brand not in email_part:
                    analysis['is_suspicious'] = True
                    analysis['spoofing_indicators'].append(f'Display name claims "{brand}" but email domain doesn\'t match')

        # Extract domain
        domain_match = re.search(r'@([a-zA-Z0-9.-]+)', sender_lower)
        if domain_match:
            domain = domain_match.group(1)

            # Check for suspicious TLDs
            for tld in self.SUSPICIOUS_TLDS:
                if domain.endswith(tld):
                    analysis['is_suspicious'] = True
                    analysis['reasons'].append(f'Sender uses suspicious TLD: {tld}')
                    break

            # Check for typosquatting in sender domain - use word boundary matching
            # to avoid false positives like "amazonember" matching "amazone"
            for brand, typos in self.TYPOSQUAT_PATTERNS.items():
                for typo in typos:
                    # Match only if typo is the domain name or a clear subdomain
                    if re.search(rf'\b{re.escape(typo)}\b', domain) or \
                       domain.startswith(typo + '.') or \
                       f'.{typo}.' in domain or \
                       domain == typo:
                        analysis['is_suspicious'] = True
                        analysis['spoofing_indicators'].append(f'Domain typosquatting: "{typo}" impersonating {brand}')

            # Random-looking domain - LOWERED thresholds for better detection
            domain_name = domain.split('.')[0]
            if len(domain_name) >= 6:  # Lowered from 10 to 6
                entropy = self._calculate_entropy(domain_name)
                if entropy > 2.5:  # Lowered from 3.5 to 2.5
                    analysis['is_suspicious'] = True
                    analysis['reasons'].append(f'Sender domain appears randomly generated (entropy: {entropy:.2f})')

            # Also flag domains with unusual character patterns
            if len(domain_name) >= 5:
                # Check for mix of uppercase/lowercase in original sender
                domain_check = sender.split('@')[-1].split('.')[0] if '@' in sender else ''
                if domain_check and re.search(r'[A-Z].*[a-z]|[a-z].*[A-Z]', domain_check):
                    analysis['is_suspicious'] = True
                    analysis['reasons'].append('Domain has unusual mixed case pattern')

            # Numbers in domain name
            if re.search(r'\d{4,}', domain_name):
                analysis['is_suspicious'] = True
                analysis['reasons'].append('Sender domain contains many numbers')

        # Reply-to mismatch indicators
        suspicious_patterns = [
            (r'noreply|no-reply|donotreply', 'Uses no-reply address'),
            (r'\d{6,}', 'Contains many consecutive numbers'),
            (r'[a-z]{20,}', 'Unusually long local part'),
        ]

        for pattern, reason in suspicious_patterns:
            if re.search(pattern, sender_lower):
                analysis['is_suspicious'] = True
                analysis['reasons'].append(reason)

        return analysis

    def _detect_brand_impersonation(self, text: str, sender: str) -> Dict:
        """
        Detect brand impersonation attempts
        IMPORTANT: Only flag when email CLAIMS to be FROM a brand, not just mentions it
        Newsletters talking ABOUT companies (e.g., stock news) are NOT impersonation
        """
        analysis = {
            'is_impersonating': False,
            'brands_mentioned': [],
            'impersonation_indicators': []
        }

        text_lower = text.lower()
        sender_lower = sender.lower()

        # Phrases that indicate the email CLAIMS to be FROM a brand (not just discussing it)
        impersonation_phrases = [
            'your {} account', 'your {} password', '{} security', '{} support',
            '{} customer service', 'from {}', '{} team', '{} billing',
            '{} verification', 'verify your {}', '{} alert', '{} notification',
            'dear {} customer', '{} account suspended', '{} account locked',
            'sign in to {}', 'log in to {}', '{} login', 'access your {}'
        ]

        # Check for brands that the email CLAIMS to represent
        for brand in self.IMPERSONATED_BRANDS:
            # Check if any impersonation phrase is used with this brand
            for phrase in impersonation_phrases:
                pattern = phrase.format(brand)
                if pattern in text_lower:
                    # This email claims to be from or about user's account with this brand
                    if brand not in sender_lower:
                        # Check for official domains
                        official_patterns = {
                            'microsoft': ['@microsoft.com', '@outlook.com', '@hotmail.com', '@live.com'],
                            'apple': ['@apple.com', '@icloud.com'],
                            'google': ['@google.com', '@gmail.com', '@youtube.com'],
                            'amazon': ['@amazon.com', '@amazon.'],
                            'paypal': ['@paypal.com', '@paypal.'],
                            'netflix': ['@netflix.com'],
                            'facebook': ['@facebook.com', '@fb.com', '@meta.com', '@instagram.com'],
                            'chase': ['@chase.com'],
                            'wells fargo': ['@wellsfargo.com'],
                        }

                        if brand in official_patterns:
                            if not any(domain in sender_lower for domain in official_patterns[brand]):
                                analysis['is_impersonating'] = True
                                analysis['brands_mentioned'].append(brand)
                                analysis['impersonation_indicators'].append(
                                    f'Email claims to be from {brand.upper()} but sender domain doesn\'t match'
                                )
                        else:
                            analysis['is_impersonating'] = True
                            analysis['brands_mentioned'].append(brand)
                            analysis['impersonation_indicators'].append(
                                f'Email claims to be from {brand.upper()} but sender domain doesn\'t match'
                            )
                    break  # Only flag once per brand

        return analysis

    def _detect_homoglyphs(self, sender: str, subject: str, body: str) -> Dict:
        """Detect homoglyph/unicode attacks"""
        analysis = {
            'homoglyphs_detected': False,
            'suspicious_characters': [],
            'locations': []
        }

        combined = f"{sender} {subject}"

        for char, latin_equiv in self.HOMOGLYPHS.items():
            if char in combined:
                analysis['homoglyphs_detected'] = True
                analysis['suspicious_characters'].append({
                    'unicode_char': char,
                    'looks_like': latin_equiv,
                    'unicode_name': f'U+{ord(char):04X}'
                })

        # Check for mixed scripts
        if re.search(r'[\u0400-\u04FF]', combined):  # Cyrillic
            if re.search(r'[a-zA-Z]', combined):  # Latin
                analysis['homoglyphs_detected'] = True
                analysis['locations'].append('Mixed Cyrillic and Latin characters detected')

        # Check for confusable domains
        if '@' in sender:
            domain = sender.split('@')[-1].split('>')[0]
            for char in domain:
                if char in self.HOMOGLYPHS:
                    analysis['homoglyphs_detected'] = True
                    analysis['locations'].append(f'Homoglyph in sender domain: "{char}" looks like "{self.HOMOGLYPHS[char]}"')

        return analysis

    def _analyze_attachments(self, attachments: List[str]) -> Dict:
        """Analyze attachments for malicious file types"""
        analysis = {
            'total_attachments': len(attachments),
            'malicious_files': [],
            'high_risk_files': [],
            'medium_risk_files': [],
            'macro_files': [],
            'risk_level': 'none',
            'reasons': []
        }

        if not attachments:
            return analysis

        for filename in attachments:
            filename_lower = filename.lower()

            # Malicious extensions
            for ext in self.MALICIOUS_EXTENSIONS:
                if filename_lower.endswith(ext):
                    analysis['malicious_files'].append(filename)
                    analysis['reasons'].append(f'CRITICAL: Executable file detected ({ext})')
                    break

            # High risk extensions
            for ext in self.HIGH_RISK_EXTENSIONS:
                if filename_lower.endswith(ext):
                    analysis['high_risk_files'].append(filename)
                    if ext == '.eml':
                        analysis['reasons'].append('HIGH RISK: Nested email (payload smuggling)')
                    elif ext in ['.html', '.htm', '.hta']:
                        analysis['reasons'].append('HIGH RISK: HTML file (likely phishing page)')
                    else:
                        analysis['reasons'].append(f'HIGH RISK: Suspicious file type ({ext})')
                    break

            # Medium risk (archives)
            for ext in self.MEDIUM_RISK_EXTENSIONS:
                if filename_lower.endswith(ext):
                    analysis['medium_risk_files'].append(filename)
                    analysis['reasons'].append(f'MEDIUM RISK: Archive file - may contain malware')
                    break

            # Macro-enabled documents
            for ext in self.DOCUMENT_MACROS:
                if filename_lower.endswith(ext):
                    analysis['macro_files'].append(filename)
                    analysis['reasons'].append(f'HIGH RISK: Macro-enabled document ({ext})')
                    break

            # Double extension trick (e.g., document.pdf.exe)
            if re.search(r'\.[a-z]{2,4}\.[a-z]{2,4}$', filename_lower):
                if any(ext in filename_lower for ext in self.MALICIOUS_EXTENSIONS):
                    analysis['malicious_files'].append(filename)
                    analysis['reasons'].append(f'CRITICAL: Double extension attack detected')

        # Determine risk level
        if analysis['malicious_files']:
            analysis['risk_level'] = 'critical'
        elif analysis['high_risk_files'] or analysis['macro_files']:
            analysis['risk_level'] = 'high'
        elif analysis['medium_risk_files']:
            analysis['risk_level'] = 'medium'

        return analysis

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy"""
        if not text:
            return 0.0

        char_freq = {}
        for char in text:
            char_freq[char] = char_freq.get(char, 0) + 1

        entropy = 0.0
        text_len = len(text)
        for count in char_freq.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)

        return entropy

    def _analyze_encoding_obfuscation(self, sender: str, subject: str, headers: str) -> Dict:
        """Detect encoding obfuscation"""
        analysis = {
            'has_base64_encoding': False,
            'has_high_entropy_domain': False,
            'encoding_count': 0,
            'risk_level': 'none',
            'reasons': []
        }

        base64_pattern = r'=\?[^?]+\?[BQ]\?[A-Za-z0-9+/=]+\?='

        subject_encodings = re.findall(base64_pattern, subject)
        if subject_encodings:
            analysis['has_base64_encoding'] = True
            analysis['encoding_count'] += len(subject_encodings)
            analysis['reasons'].append(f'Subject contains encoded text ({len(subject_encodings)} segments)')

        if headers:
            header_encodings = re.findall(base64_pattern, headers)
            if len(header_encodings) > 3:
                analysis['has_base64_encoding'] = True
                analysis['encoding_count'] += len(header_encodings)
                analysis['reasons'].append(f'Heavy header encoding ({len(header_encodings)} segments)')

        domain_match = re.search(r'@([a-zA-Z0-9.-]+)', sender)
        if domain_match:
            domain = domain_match.group(1)
            domain_name = re.sub(r'\.(com|net|org|edu|gov|co|io|us|uk|az|tr)$', '', domain, flags=re.IGNORECASE)

            if len(domain_name) >= 6:  # Lowered from 8 to 6
                entropy = self._calculate_entropy(domain_name)
                if entropy > 2.5:  # Lowered from 3.5 to 2.5
                    analysis['has_high_entropy_domain'] = True
                    analysis['reasons'].append(f'Random-looking domain (entropy: {entropy:.2f})')

        if analysis['encoding_count'] > 5 or analysis['has_high_entropy_domain']:
            analysis['risk_level'] = 'high'
        elif analysis['has_base64_encoding']:
            analysis['risk_level'] = 'medium'

        return analysis

    def _analyze_image_heavy_ratio(self, body: str) -> Dict:
        """Detect image-heavy emails (spam indicator)"""
        analysis = {
            'image_count': 0,
            'word_count': 0,
            'is_image_heavy': False,
            'risk_level': 'none',
            'reasons': []
        }

        images = re.findall(r'<img[^>]*>', body, re.IGNORECASE)
        analysis['image_count'] = len(images)

        text_only = re.sub(r'<[^>]+>', '', body)
        words = re.findall(r'\b\w+\b', text_only)
        analysis['word_count'] = len(words)

        if analysis['image_count'] > 1 and analysis['word_count'] < 50:
            analysis['is_image_heavy'] = True
            analysis['risk_level'] = 'high'
            analysis['reasons'].append(f'Image-heavy content: {analysis["image_count"]} images, only {analysis["word_count"]} words')

        return analysis

    def _calculate_spam_score(self, text: str) -> Dict:
        """Calculate spam score"""
        analysis = {
            'spam_keywords_found': [],
            'is_spam': False,
            'spam_score': 0,
            'reasons': []
        }

        for keyword in self.all_spam_scam:
            if keyword in text:
                if keyword not in analysis['spam_keywords_found']:
                    analysis['spam_keywords_found'].append(keyword)

        if analysis['spam_keywords_found']:
            analysis['is_spam'] = True
            analysis['spam_score'] = min(len(analysis['spam_keywords_found']) * 10, 40)
            analysis['reasons'].append(f'Spam keywords: {", ".join(analysis["spam_keywords_found"][:5])}')

        return analysis

    def _detect_link_text_mismatch(self, body: str) -> Dict:
        """Detect when link text doesn't match actual URL"""
        analysis = {
            'mismatches_found': [],
            'is_suspicious': False,
            'reasons': []
        }

        # Find <a> tags with href
        link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        links = re.findall(link_pattern, body, re.IGNORECASE)

        for href, text in links:
            text_lower = text.lower().strip()
            href_lower = href.lower()

            # Check if text looks like a URL but doesn't match href
            if re.match(r'https?://', text_lower) or 'www.' in text_lower:
                # Text is a URL - check if it matches href
                if text_lower not in href_lower and href_lower not in text_lower:
                    analysis['is_suspicious'] = True
                    analysis['mismatches_found'].append({
                        'displayed': text[:50],
                        'actual': href[:50]
                    })
                    analysis['reasons'].append('Link displays different URL than actual destination')

            # Check for brand names in text but suspicious href
            for brand in self.IMPERSONATED_BRANDS:
                if brand in text_lower and brand not in href_lower:
                    analysis['is_suspicious'] = True
                    analysis['reasons'].append(f'Link claims to be {brand} but goes elsewhere')

        return analysis

    def _calculate_risk_score(self, keywords: Dict, phishing_phrases: List,
                             urgency: float, url_analysis: Dict, sender_analysis: Dict,
                             brand_analysis: Dict, homoglyph_analysis: Dict,
                             attachment_analysis: Dict, encoding_analysis: Dict,
                             image_analysis: Dict, spam_analysis: Dict,
                             link_mismatch: Dict, newsletter_context: Dict = None,
                             auth_result: Dict = None) -> float:
        """Calculate comprehensive risk score (0-100) - BALANCED SCORING with newsletter and authentication awareness"""
        score = 0

        # Check if this is a legitimate newsletter
        is_newsletter = newsletter_context and newsletter_context.get('is_newsletter', False)

        # Check if sender is a verified trusted brand (DKIM/SPF/DMARC passing)
        is_trusted_authenticated = auth_result and auth_result.get('is_trusted_sender', False)
        trust_score = auth_result.get('trust_score', 0) if auth_result else 0

        # Count how many different risk categories are triggered
        risk_categories = 0

        # Phishing phrases - only count if multiple found (single phrase could be coincidence)
        # For newsletters, require MORE phrases to trigger
        phrase_threshold = 3 if is_newsletter else 2
        if len(phishing_phrases) >= phrase_threshold:
            score += min(len(phishing_phrases) * 8, 25) if is_newsletter else min(len(phishing_phrases) * 10, 30)
            risk_categories += 1
        elif len(phishing_phrases) == 1 and not is_newsletter:
            score += 8

        # Keyword scoring - INCREASED weights for better detection
        # For newsletters, financial keywords should NOT count
        keyword_category_count = 0
        keyword_scores = {
            'urgent': min(len(keywords['urgent']) * 5, 20),  # Increased from 3 to 5
            'financial': 0 if is_newsletter else min(len(keywords['financial']) * 4, 15),  # Increased
            'credentials': min(len(keywords['credentials']) * 8, 25),  # Increased - credential requests are very suspicious
            'rewards': min(len(keywords['rewards']) * 4, 15) if is_newsletter else min(len(keywords['rewards']) * 6, 20),  # Increased
            'threats': min(len(keywords['threats']) * 8, 25),  # Increased - threat language is very suspicious
            'spam_scam': 0 if is_newsletter else min(len(keywords['spam_scam']) * 6, 20),  # Increased for spam/delivery scams
            'social_engineering': min(len(keywords.get('social_engineering', [])) * 5, 15)  # Increased
        }

        for category, cat_score in keyword_scores.items():
            if cat_score > 0:
                keyword_category_count += 1

        # Add keyword score - even single category can be suspicious
        if keyword_category_count >= 2:
            score += min(sum(keyword_scores.values()), 40)  # Increased cap from 25 to 40
            risk_categories += 1
        elif keyword_category_count == 1:
            score += min(sum(keyword_scores.values()), 15)  # Increased from 10 to 15

        # Urgency - reduced weight, newsletters often have natural urgency (sales, etc.)
        urgency_multiplier = 0.08 if is_newsletter else 0.15
        if urgency > 60:
            score += min(urgency * urgency_multiplier, 12 if is_newsletter else 15)
            if not is_newsletter:
                risk_categories += 1
        elif urgency > 30:
            score += urgency * (0.05 if is_newsletter else 0.08)

        # URL analysis - these are strong indicators
        # For newsletters, only flag truly suspicious patterns, not just "many links"
        if url_analysis['suspicious_urls']:
            url_score = min(len(url_analysis['suspicious_urls']) * 8, 20)
            if is_newsletter:
                url_score = url_score // 2  # Newsletters have many links
            score += url_score
            if url_score >= 10:
                risk_categories += 1
        if url_analysis.get('typosquatting_detected'):
            score += 25  # Very strong indicator - even for newsletters
            risk_categories += 1
        if url_analysis.get('url_shortener_detected') and not is_newsletter:
            score += 5  # Skip for newsletters - they use tracking links

        # Sender analysis - INCREASED weights
        if sender_analysis['is_suspicious'] and not is_newsletter:
            score += 20  # Increased from 8 to 20 - suspicious sender is a strong indicator
            risk_categories += 1
        if sender_analysis.get('spoofing_indicators'):
            score += min(len(sender_analysis['spoofing_indicators']) * 15, 35)  # Increased
            risk_categories += 1

        # Brand impersonation - CRITICAL: Skip for newsletters discussing companies
        # Only flag if email CLAIMS to be from that brand
        if brand_analysis['is_impersonating'] and not is_newsletter:
            if sender_analysis['is_suspicious'] or sender_analysis.get('spoofing_indicators'):
                score += 30  # High confidence
            else:
                score += 15  # Could be forwarded/quoted email
            risk_categories += 1

        # Homoglyph attacks - VERY strong indicator (almost always malicious)
        # This should NEVER be ignored, even for newsletters
        if homoglyph_analysis['homoglyphs_detected']:
            score += 35
            risk_categories += 1

        # Attachments - strong indicators
        if attachment_analysis['risk_level'] == 'critical':
            score += 40
            risk_categories += 1
        elif attachment_analysis['risk_level'] == 'high':
            score += 25
            risk_categories += 1
        elif attachment_analysis['risk_level'] == 'medium':
            score += 10

        # Encoding obfuscation - INCREASED weights
        if encoding_analysis['risk_level'] == 'high':
            score += 25  # Increased from 15 - random domain is strong indicator
            risk_categories += 1
        elif encoding_analysis['risk_level'] == 'medium':
            score += 10  # Increased from 5

        # Image-heavy spam - newsletters are often image-heavy legitimately
        if image_analysis['is_image_heavy'] and not is_newsletter:
            score += 12
            risk_categories += 1

        # Spam score - skip for newsletters
        if spam_analysis['is_spam'] and not is_newsletter:
            score += min(spam_analysis['spam_score'] // 2, 15)

        # Link text mismatch - strong indicator (check even for newsletters)
        if link_mismatch['is_suspicious']:
            score += 20
            risk_categories += 1

        # COMBINATION BONUS: Multiple risk categories = higher confidence
        # For newsletters, require MORE categories to add bonus
        if is_newsletter:
            if risk_categories >= 5:
                score += 10
        else:
            if risk_categories >= 4:
                score += 15  # High confidence phishing
            elif risk_categories >= 3:
                score += 8

        # NEWSLETTER DISCOUNT: If clearly a newsletter and no critical indicators
        if is_newsletter and not homoglyph_analysis['homoglyphs_detected'] and \
           not url_analysis.get('typosquatting_detected') and \
           attachment_analysis['risk_level'] not in ['critical', 'high']:
            score = score * 0.6  # 40% reduction for clear newsletters

        # TRUSTED AUTHENTICATED SENDER DISCOUNT:
        # When email authentication (DKIM/SPF/DMARC) passes from a known trusted domain,
        # significantly reduce the risk score. This prevents false positives for legitimate
        # marketing emails from major brands like Amazon, Microsoft, etc.
        if is_trusted_authenticated and trust_score >= 80:
            # High trust (all 3 auth methods pass) - only flag for CRITICAL indicators
            if not homoglyph_analysis['homoglyphs_detected'] and \
               not url_analysis.get('typosquatting_detected') and \
               attachment_analysis['risk_level'] not in ['critical', 'high'] and \
               not link_mismatch['is_suspicious']:
                # Legitimate email from verified sender - apply heavy discount
                score = score * 0.15  # 85% reduction for fully authenticated trusted senders
            else:
                # Has some critical indicators despite authentication - could be sophisticated attack
                score = score * 0.5  # 50% reduction but still flag for review
        elif is_trusted_authenticated and trust_score >= 40:
            # Partial trust (at least DKIM passes) - moderate discount
            if not homoglyph_analysis['homoglyphs_detected'] and \
               not url_analysis.get('typosquatting_detected') and \
               attachment_analysis['risk_level'] not in ['critical', 'high']:
                score = score * 0.4  # 60% reduction for partially authenticated trusted senders

        return min(score, 100)

    def _classify_risk(self, risk_score: float) -> str:
        """Classify email - LOWERED THRESHOLDS for better detection"""
        if risk_score < 20:
            return 'safe'
        elif risk_score < 45:
            return 'suspicious'
        else:
            return 'malicious'

    def _generate_explanation(self, risk_score: float, classification: str,
                             keywords: Dict, phishing_phrases: List, urgency: float,
                             url_analysis: Dict, sender_analysis: Dict,
                             brand_analysis: Dict, homoglyph_analysis: Dict,
                             attachment_analysis: Dict, encoding_analysis: Dict,
                             image_analysis: Dict, spam_analysis: Dict,
                             link_mismatch: Dict, newsletter_context: Dict = None,
                             auth_result: Dict = None) -> str:
        """Generate detailed explanation"""
        parts = []

        # Header
        parts.append(f"RISK ASSESSMENT: {classification.upper()} (Score: {risk_score:.1f}/100)")
        parts.append("=" * 50)

        # Email authentication status - show prominently for trusted senders
        if auth_result:
            if auth_result.get('is_trusted_sender'):
                parts.append("\n✅ VERIFIED SENDER:")
                parts.append(f"  Authenticated email from trusted brand: {auth_result.get('trusted_brand', 'Unknown')}")
                auth_checks = []
                if auth_result.get('dkim_pass'):
                    auth_checks.append("DKIM ✓")
                if auth_result.get('spf_pass'):
                    auth_checks.append("SPF ✓")
                if auth_result.get('dmarc_pass'):
                    auth_checks.append("DMARC ✓")
                if auth_checks:
                    parts.append(f"  • Authentication: {' | '.join(auth_checks)}")
                parts.append(f"  • Trust Score: {auth_result.get('trust_score', 0)}/100")
                parts.append("  (Scoring adjusted - verified sender from trusted domain)")
            else:
                # Show auth status even if not trusted
                auth_checks = []
                if auth_result.get('dkim_pass'):
                    auth_checks.append("DKIM: PASS")
                if auth_result.get('spf_pass'):
                    auth_checks.append("SPF: PASS")
                if auth_result.get('dmarc_pass'):
                    auth_checks.append("DMARC: PASS")
                if auth_checks:
                    parts.append(f"\n📧 EMAIL AUTHENTICATION:")
                    parts.append(f"  • {' | '.join(auth_checks)}")

        # Newsletter context - show if detected
        if newsletter_context and newsletter_context.get('is_newsletter'):
            parts.append("\n✅ NEWSLETTER DETECTED:")
            parts.append("  This email appears to be a legitimate newsletter/marketing email.")
            if newsletter_context.get('platform_detected'):
                parts.append(f"  • Platform: {newsletter_context['platform_detected']}")
            for reason in newsletter_context.get('reasons', [])[:2]:
                parts.append(f"  • {reason}")
            parts.append("  (Scoring adjusted to reduce false positives)")

        # Critical findings first
        if homoglyph_analysis['homoglyphs_detected']:
            parts.append("\n⚠️ HOMOGLYPH ATTACK DETECTED:")
            parts.append("Unicode characters used to impersonate legitimate text")
            for char_info in homoglyph_analysis['suspicious_characters'][:3]:
                parts.append(f"  • '{char_info['unicode_char']}' looks like '{char_info['looks_like']}'")

        if brand_analysis['is_impersonating']:
            parts.append("\n⚠️ BRAND IMPERSONATION DETECTED:")
            for indicator in brand_analysis['impersonation_indicators'][:3]:
                parts.append(f"  • {indicator}")

        if attachment_analysis['risk_level'] != 'none':
            parts.append(f"\n⚠️ DANGEROUS ATTACHMENTS ({attachment_analysis['risk_level'].upper()}):")
            for reason in attachment_analysis['reasons'][:3]:
                parts.append(f"  • {reason}")

        if link_mismatch['is_suspicious']:
            parts.append("\n⚠️ LINK DECEPTION DETECTED:")
            parts.append("Displayed link text doesn't match actual destination")

        # Phishing phrases
        if phishing_phrases:
            parts.append(f"\n📧 PHISHING PHRASES DETECTED ({len(phishing_phrases)}):")
            for phrase in phishing_phrases[:5]:
                parts.append(f"  • \"{phrase}\"")

        # Keywords
        total_keywords = sum(len(v) for v in keywords.values())
        if total_keywords > 0:
            parts.append(f"\n🔍 SUSPICIOUS KEYWORDS ({total_keywords} found):")
            for category, words in keywords.items():
                if words:
                    parts.append(f"  • {category.replace('_', ' ').title()}: {', '.join(words[:4])}")

        # Urgency
        if urgency > 40:
            parts.append(f"\n⏰ HIGH URGENCY TACTICS (score: {urgency:.0f}/100)")
            parts.append("  Email uses pressure tactics to force quick action")

        # URLs
        if url_analysis['suspicious_urls']:
            parts.append(f"\n🔗 SUSPICIOUS URLS ({len(url_analysis['suspicious_urls'])}):")
            for url_info in url_analysis['suspicious_urls'][:2]:
                parts.append(f"  • {url_info['url'][:60]}...")
                for reason in url_info['reasons'][:2]:
                    parts.append(f"    - {reason}")

        # Sender
        if sender_analysis['is_suspicious']:
            parts.append("\n📤 SUSPICIOUS SENDER:")
            for reason in sender_analysis['reasons'][:3]:
                parts.append(f"  • {reason}")

        return '\n'.join(parts)

    def _generate_recommendations(self, classification: str, risk_score: float,
                                   auth_result: Dict = None) -> List[str]:
        """Generate actionable recommendations"""
        # If sender is verified from trusted domain, adjust recommendations
        is_trusted = auth_result and auth_result.get('is_trusted_sender', False)
        trust_score = auth_result.get('trust_score', 0) if auth_result else 0

        if classification == 'malicious':
            if is_trusted and trust_score >= 80:
                # Unusual case - trusted sender but still flagged as malicious
                return [
                    "This email passed authentication but contains concerning content",
                    "The sender domain appears legitimate - this could be a compromised account",
                    "Contact the organization directly through official channels to verify",
                    "Do not click links or download attachments until verified",
                    "Report to IT security for investigation"
                ]
            return [
                "DO NOT click any links or download attachments",
                "DO NOT reply or provide any information",
                "Report this email to your IT security team immediately",
                "Delete this email from your inbox",
                "If you clicked any links, change your passwords immediately",
                "Enable two-factor authentication on your accounts",
                "Monitor your accounts for suspicious activity"
            ]
        elif classification == 'suspicious':
            if is_trusted and trust_score >= 60:
                return [
                    "This email is from a verified sender but triggered some alerts",
                    "The content is likely legitimate marketing/promotional material",
                    "Exercise normal caution when clicking links",
                    "This is probably NOT a phishing attempt"
                ]
            return [
                "Exercise extreme caution with this email",
                "Do not click links or download attachments",
                "Verify the sender through official channels",
                "Contact the organization directly using known contact info",
                "Report to IT security if you're unsure",
                "Check the sender's email address carefully"
            ]
        else:
            if is_trusted and trust_score >= 80:
                return [
                    "Email is from a verified, trusted sender",
                    "Authentication passed (DKIM/SPF/DMARC)",
                    "This email is safe to interact with",
                    "Standard email security practices still apply"
                ]
            return [
                "Email appears relatively safe",
                "Always verify sender identity for sensitive requests",
                "Hover over links to preview destinations",
                "Be cautious with unexpected attachments",
                "Report anything that seems unusual"
            ]
