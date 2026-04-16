import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from functools import wraps
import re

app = Flask(__name__)

# ---------------- CONFIG ----------------
IPINFO_BASE_URL = "https://ipinfo.io"
IPIFY_URL = "https://api.ipify.org?format=json"

# Country flag emojis
def get_flag_emoji(country_code):
    if not country_code:
        return "🌍"
    try:
        return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)
    except:
        return "🌍"

# ---------------- HELPER FUNCTIONS ----------------
def validate_ip(ip):
    """Validate IPv4 and IPv6 addresses"""
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return True
    elif re.match(ipv6_pattern, ip):
        return True
    return False

def get_ip_info(ip_address):
    """Fetch IP information from ipinfo.io"""
    try:
        url = f"{IPINFO_BASE_URL}/{ip_address}/geo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Remove readme if present
            if "readme" in data:
                del data["readme"]
            
            # Add enhanced information
            if "country" in data:
                data["country_flag"] = get_flag_emoji(data["country"])
                data["country_name"] = get_country_name(data["country"])
            
            if "loc" in data:
                lat, lon = data["loc"].split(",")
                data["latitude"] = lat.strip()
                data["longitude"] = lon.strip()
                data["google_maps"] = f"https://www.google.com/maps?q={lat},{lon}"
            
            # Add timestamp
            data["checked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            data["checked_timestamp"] = int(datetime.now().timestamp())
            
            # Add developer info
            data["api_info"] = {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers",
                "version": "2.0.0"
            }
            
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"Failed to fetch IP info: {response.status_code}"}
            
    except requests.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def get_country_name(country_code):
    """Get full country name from code"""
    countries = {
        "IN": "India",
        "US": "United States",
        "GB": "United Kingdom",
        "CA": "Canada",
        "AU": "Australia",
        "DE": "Germany",
        "FR": "France",
        "JP": "Japan",
        "CN": "China",
        "BR": "Brazil",
        "RU": "Russia",
        "ZA": "South Africa",
        "AE": "United Arab Emirates",
        "SG": "Singapore",
        "NZ": "New Zealand",
        "PK": "Pakistan",
        "BD": "Bangladesh",
        "NP": "Nepal",
        "LK": "Sri Lanka",
    }
    return countries.get(country_code, country_code)

def batch_lookup(ips):
    """Perform batch lookup for multiple IPs"""
    results = []
    for ip in ips:
        ip = ip.strip()
        if validate_ip(ip):
            info = get_ip_info(ip)
            if info["success"]:
                results.append(info["data"])
            else:
                results.append({"ip": ip, "error": info["error"]})
        else:
            results.append({"ip": ip, "error": "Invalid IP address"})
    return results

# ---------------- HTML TEMPLATE ----------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexxon Hackers - IP Information API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            width: 100%;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .content {
            padding: 40px;
        }
        
        .endpoint-section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        
        .endpoint-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
        }
        
        .method-badge {
            background: #28a745;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-left: 15px;
            font-weight: normal;
        }
        
        .url-box {
            background: #2d3748;
            color: #68d391;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            margin: 15px 0;
            word-break: break-all;
        }
        
        .example-box {
            background: #fff;
            border: 1px solid #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .example-box code {
            color: #e83e8c;
            font-family: 'Courier New', monospace;
        }
        
        .dev-info {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 12px;
            margin-top: 20px;
        }
        
        .dev-info h2 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .dev-info .founder {
            font-size: 1.2em;
            opacity: 0.95;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .feature-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .feature-card .emoji {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .feature-card h4 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .feature-card p {
            color: #666;
            font-size: 0.9em;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #e2e8f0;
        }
        
        @media (max-width: 600px) {
            .header h1 {
                font-size: 1.8em;
            }
            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 IP Information API</h1>
            <p>Advanced IP Geolocation & Intelligence Service</p>
        </div>
        
        <div class="content">
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="emoji">🎯</div>
                    <h4>Precise Location</h4>
                    <p>City, Region & Coordinates</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">🚩</div>
                    <h4>Country Flags</h4>
                    <p>Automatic Flag Emojis</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">🗺️</div>
                    <h4>Google Maps</h4>
                    <p>Direct Map Integration</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">⚡</div>
                    <h4>Batch Support</h4>
                    <p>Multiple IPs at Once</p>
                </div>
            </div>
            
            <div class="endpoint-section">
                <h3>Single IP Lookup <span class="method-badge">GET</span></h3>
                <div class="url-box">
                    /ip-info/ip?=YOUR_IP_ADDRESS
                </div>
                <div class="example-box">
                    <strong>📝 Example:</strong><br>
                    <code>GET /ip-info/ip?=8.8.8.8</code>
                </div>
            </div>
            
            <div class="endpoint-section">
                <h3>Batch IP Lookup <span class="method-badge">POST</span></h3>
                <div class="url-box">
                    /ip-info/batch
                </div>
                <div class="example-box">
                    <strong>📝 Request Body:</strong><br>
                    <code>{"ips": ["8.8.8.8", "1.1.1.1"]}</code>
                </div>
            </div>
            
            <div class="endpoint-section">
                <h3>Get Your Own IP <span class="method-badge">GET</span></h3>
                <div class="url-box">
                    /ip-info/myip
                </div>
                <div class="example-box">
                    <strong>📝 Example Response:</strong><br>
                    <code>{"ip": "YOUR_IP_ADDRESS"}</code>
                </div>
            </div>
            
            <div class="dev-info">
                <h2>⚡ Nexxon Hackers ⚡</h2>
                <div class="founder">Developed by Creator Shyamchand & Ayan</div>
                <div style="margin-top: 10px; font-size: 1.1em;">CEO & Founder Of - Nexxon Hackers</div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 Nexxon Hackers | All Rights Reserved</p>
            <p style="margin-top: 5px;">🚀 Powering IP Intelligence Worldwide</p>
        </div>
    </div>
</body>
</html>
'''

# ---------------- FLASK ROUTES ----------------
@app.route('/')
def home():
    """Home page with API documentation"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/ip-info/ip', methods=['GET'])
def ip_lookup():
    """Single IP lookup endpoint"""
    ip_param = request.args.get('ip')
    
    if not ip_param:
        return jsonify({
            "success": False,
            "error": "Missing 'ip' parameter",
            "usage": {
                "endpoint": "/ip-info/ip?=IP_ADDRESS",
                "example": "/ip-info/ip?=8.8.8.8"
            },
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 400
    
    # Handle multiple IPs separated by comma
    if ',' in ip_param:
        ips = [ip.strip() for ip in ip_param.split(',')]
        results = batch_lookup(ips)
        
        return jsonify({
            "success": True,
            "batch_mode": True,
            "total": len(results),
            "results": results,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        })
    
    # Single IP lookup
    if not validate_ip(ip_param):
        return jsonify({
            "success": False,
            "error": "Invalid IP address format",
            "provided_ip": ip_param,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 400
    
    result = get_ip_info(ip_param)
    
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify({
            "success": False,
            "error": result["error"],
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 500

@app.route('/ip-info/batch', methods=['POST'])
def batch_ip_lookup():
    """Batch IP lookup endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'ips' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'ips' array in request body",
                "example": {"ips": ["8.8.8.8", "1.1.1.1"]},
                "api_info": {
                    "developed_by": "Creator Shyamchand & Ayan",
                    "organization": "CEO & Founder Of - Nexxon Hackers"
                }
            }), 400
        
        ips = data['ips']
        if not isinstance(ips, list):
            return jsonify({
                "success": False,
                "error": "'ips' must be an array",
                "api_info": {
                    "developed_by": "Creator Shyamchand & Ayan",
                    "organization": "CEO & Founder Of - Nexxon Hackers"
                }
            }), 400
        
        results = batch_lookup(ips)
        
        return jsonify({
            "success": True,
            "total_requested": len(ips),
            "total_processed": len(results),
            "results": results,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 500

@app.route('/ip-info/myip', methods=['GET'])
def get_my_ip():
    """Get the client's own IP address"""
    try:
        # Get client IP from headers or request
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # If multiple IPs in X-Forwarded-For, get the first one
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # Try to get IP from ipify as fallback
        try:
            response = requests.get(IPIFY_URL, timeout=5)
            if response.status_code == 200:
                ipify_data = response.json()
                detected_ip = ipify_data.get('ip', client_ip)
            else:
                detected_ip = client_ip
        except:
            detected_ip = client_ip
        
        return jsonify({
            "success": True,
            "your_ip": detected_ip,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "your_ip": request.remote_addr,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 500

@app.route('/ip-info/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "IP Information API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": {
            "home": "/",
            "single_ip": "/ip-info/ip?=IP_ADDRESS",
            "batch_ip": "/ip-info/batch (POST)",
            "my_ip": "/ip-info/myip",
            "health": "/ip-info/health"
        },
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    }), 500

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
