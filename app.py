#!/usr/bin/env python3
"""
LogiThai Express - Python Flask Backend
บริการโลจิสติกส์ระดับมืออาชีพ

This is the main Python backend application that handles:
- Quote form submissions
- Contact form processing
- Email notifications
- Data storage and retrieval
- API endpoints for the frontend
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import json
import datetime
import os
import logging

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='.')
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE = 'logithai.db'

# Email configuration (configure these with your actual email settings)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your-email@gmail.com',  # Replace with your email
    'password': 'your-app-password',      # Replace with your app password
    'from_email': 'noreply@logithai.com'
}

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create quotes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            service_type TEXT NOT NULL,
            origin TEXT,
            destination TEXT,
            cargo_type TEXT,
            weight TEXT,
            dimensions TEXT,
            urgency TEXT,
            additional_services TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Create contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'
        )
    ''')
    
    conn.commit()
    conn.close()

def send_email(to_email, subject, body_html, body_text=None):
    """Send email notification"""
    try:
        msg = MimeMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = to_email
        
        # Add text and HTML parts
        if body_text:
            text_part = MimeText(body_text, 'plain', 'utf-8')
            msg.attach(text_part)
        
        html_part = MimeText(body_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

@app.route('/')
def index():
    """Serve the main index page"""
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_pages(filename):
    """Serve HTML pages"""
    if filename.endswith('.html'):
        return render_template(filename)
    return send_from_directory('.', filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/quote', methods=['POST'])
def submit_quote():
    """Handle quote form submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['companyName', 'contactName', 'email', 'phone', 'serviceType']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'กรุณากรอก {field} ให้ครบถ้วน'
                }), 400
        
        # Convert additional services list to JSON string
        additional_services = json.dumps(data.get('additionalServices', []))
        
        # Insert into database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quotes (
                company_name, contact_name, email, phone, service_type,
                origin, destination, cargo_type, weight, dimensions,
                urgency, additional_services, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['companyName'],
            data['contactName'],
            data['email'],
            data['phone'],
            data['serviceType'],
            data.get('origin', ''),
            data.get('destination', ''),
            data.get('cargoType', ''),
            data.get('weight', ''),
            data.get('dimensions', ''),
            data.get('urgency', ''),
            additional_services,
            data.get('description', '')
        ))
        
        quote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Send confirmation email to customer
        customer_email_html = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #1e40af; color: white; padding: 20px; text-align: center;">
                    <h1>LogiThai Express</h1>
                    <h2>ขอบคุณสำหรับการขอใบเสนอราคา</h2>
                </div>
                
                <div style="padding: 20px; background-color: #f8fafc;">
                    <p>เรียน คุณ{data['contactName']}</p>
                    
                    <p>ขอบคุณที่ให้ความสนใจบริการของ LogiThai Express</p>
                    
                    <p>เราได้รับคำขอใบเสนอราคาของท่านแล้ว (รหัสอ้างอิง: <strong>#{quote_id:06d}</strong>)</p>
                    
                    <div style="background-color: white; padding: 15px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                        <h3>รายละเอียดคำขอ:</h3>
                        <ul>
                            <li><strong>บริษัท:</strong> {data['companyName']}</li>
                            <li><strong>ประเภทบริการ:</strong> {data['serviceType']}</li>
                            <li><strong>ผู้ติดต่อ:</strong> {data['contactName']}</li>
                            <li><strong>อีเมล:</strong> {data['email']}</li>
                            <li><strong>โทรศัพท์:</strong> {data['phone']}</li>
                        </ul>
                    </div>
                    
                    <p><strong>ขั้นตอนต่อไป:</strong></p>
                    <ol>
                        <li>ทีมของเราจะศึกษาข้อมูลและความต้องการของท่าน</li>
                        <li>เราจะติดต่อกลับภายใน 24 ชั่วโมง</li>
                        <li>นำเสนอใบเสนอราคาที่เหมาะสมกับความต้องการ</li>
                    </ol>
                    
                    <div style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>ติดต่อเรา:</strong></p>
                        <p>📞 02-123-4567<br>
                        📧 info@logithai.com<br>
                        🕐 จันทร์-ศุกร์ 8:00-18:00 น.</p>
                    </div>
                    
                    <p>ขอบคุณที่ไว้วางใจ LogiThai Express</p>
                    
                    <p>ด้วยความเคารพ<br>
                    ทีม LogiThai Express</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        send_email(
            data['email'],
            f'ขอบคุณสำหรับการขอใบเสนอราคา - LogiThai Express #{quote_id:06d}',
            customer_email_html
        )
        
        # Send notification to company
        company_email_html = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>คำขอใบเสนอราคาใหม่ #{quote_id:06d}</h2>
            
            <h3>ข้อมูลลูกค้า:</h3>
            <ul>
                <li><strong>บริษัท:</strong> {data['companyName']}</li>
                <li><strong>ผู้ติดต่อ:</strong> {data['contactName']}</li>
                <li><strong>อีเมล:</strong> {data['email']}</li>
                <li><strong>โทรศัพท์:</strong> {data['phone']}</li>
            </ul>
            
            <h3>รายละเอียดบริการ:</h3>
            <ul>
                <li><strong>ประเภทบริการ:</strong> {data['serviceType']}</li>
                <li><strong>จุดต้นทาง:</strong> {data.get('origin', 'ไม่ระบุ')}</li>
                <li><strong>จุดปลายทาง:</strong> {data.get('destination', 'ไม่ระบุ')}</li>
                <li><strong>ประเภทสินค้า:</strong> {data.get('cargoType', 'ไม่ระบุ')}</li>
                <li><strong>น้ำหนัก:</strong> {data.get('weight', 'ไม่ระบุ')} กก.</li>
                <li><strong>ขนาด:</strong> {data.get('dimensions', 'ไม่ระบุ')} ซม.</li>
                <li><strong>ความเร่งด่วน:</strong> {data.get('urgency', 'ไม่ระบุ')}</li>
            </ul>
            
            <h3>รายละเอียดเพิ่มเติม:</h3>
            <p>{data.get('description', 'ไม่มี')}</p>
            
            <h3>บริการเสริม:</h3>
            <p>{', '.join(data.get('additionalServices', [])) if data.get('additionalServices') else 'ไม่มี'}</p>
            
            <p><strong>กรุณาติดต่อลูกค้าภายใน 24 ชั่วโมง</strong></p>
        </body>
        </html>
        '''
        
        send_email(
            'sales@logithai.com',  # Company email
            f'คำขอใบเสนอราคาใหม่ #{quote_id:06d} - {data["companyName"]}',
            company_email_html
        )
        
        return jsonify({
            'success': True,
            'message': 'ส่งคำขอใบเสนอราคาสำเร็จ',
            'quote_id': quote_id
        })
        
    except Exception as e:
        logger.error(f"Error submitting quote: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'เกิดข้อผิดพลาดในการส่งข้อมูล'
        }), 500

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'กรุณากรอก {field} ให้ครบถ้วน'
                }), 400
        
        # Insert into database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (name, email, phone, subject, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['email'],
            data.get('phone', ''),
            data.get('subject', ''),
            data['message']
        ))
        
        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Send confirmation email
        customer_email_html = f'''
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>ขอบคุณที่ติดต่อ LogiThai Express</h2>
            <p>เรียน คุณ{data['name']}</p>
            <p>เราได้รับข้อความของท่านแล้ว เราจะติดต่อกลับโดยเร็วที่สุด</p>
            <p>รหัสอ้างอิง: #{contact_id:06d}</p>
            <p>ขอบคุณครับ</p>
        </body>
        </html>
        '''
        
        send_email(
            data['email'],
            f'ขอบคุณที่ติดต่อ LogiThai Express #{contact_id:06d}',
            customer_email_html
        )
        
        return jsonify({
            'success': True,
            'message': 'ส่งข้อความสำเร็จ',
            'contact_id': contact_id
        })
        
    except Exception as e:
        logger.error(f"Error submitting contact: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'เกิดข้อผิดพลาดในการส่งข้อมูล'
        }), 500

@app.route('/api/quotes', methods=['GET'])
def get_quotes():
    """Get all quotes (admin endpoint)"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM quotes ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        quotes = []
        columns = [desc[0] for desc in cursor.description]
        for row in rows:
            quote = dict(zip(columns, row))
            # Parse additional services JSON
            if quote['additional_services']:
                try:
                    quote['additional_services'] = json.loads(quote['additional_services'])
                except:
                    quote['additional_services'] = []
            quotes.append(quote)
        
        return jsonify({
            'success': True,
            'quotes': quotes
        })
        
    except Exception as e:
        logger.error(f"Error getting quotes: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'เกิดข้อผิดพลาดในการดึงข้อมูล'
        }), 500

@app.route('/api/quotes/<int:quote_id>/status', methods=['PUT'])
def update_quote_status(quote_id):
    """Update quote status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['pending', 'processing', 'quoted', 'completed', 'cancelled']:
            return jsonify({
                'success': False,
                'message': 'สถานะไม่ถูกต้อง'
            }), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE quotes SET status = ? WHERE id = ?
        ''', (status, quote_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'อัปเดตสถานะสำเร็จ'
        })
        
    except Exception as e:
        logger.error(f"Error updating quote status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'เกิดข้อผิดพลาดในการอัปเดต'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'LogiThai Express Backend'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์'
    }), 500

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start the Flask development server
    print("🚀 Starting LogiThai Express Backend Server...")
    print("📋 Available endpoints:")
    print("   - Homepage: http://localhost:5000/")
    print("   - Services: http://localhost:5000/services.html")
    print("   - About: http://localhost:5000/about.html")
    print("   - Quote: http://localhost:5000/quote.html")
    print("   - API Health: http://localhost:5000/api/health")
    print("   - API Quotes: http://localhost:5000/api/quotes")
    
    app.run(debug=True, host='0.0.0.0', port=5000)