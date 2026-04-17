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
<title>IP Information API - Advanced Geolocation Service</title>
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<script>tailwind.config={theme:{extend:{colors:{primary:'#3b82f6',secondary:'#1e40af'},borderRadius:{'none':'0px','sm':'4px',DEFAULT:'8px','md':'12px','lg':'16px','xl':'20px','2xl':'24px','3xl':'32px','full':'9999px','button':'8px'}}}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet">
<style>
:where([class^="ri-"])::before {
content: "\f3c2";
}
</style>
</head>
<body class="bg-white min-h-screen">
<main class="pt-8 pb-8 px-4">
<header class="text-center py-8">
<h1 class="text-3xl font-bold text-gray-900 mb-2">IP Information API</h1>
<p class="text-lg text-gray-600 mb-4">Advanced IP Geolocation & Intelligence Service</p>
<p class="text-sm text-gray-500 mb-6">Precise Location Data & Real-time Intelligence</p>
<div class="mb-6">
<img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=400&fit=crop" 
     alt="Developers collaborating" 
     class="w-full h-48 object-cover object-top rounded-xl">
</div>
</header>
<section class="mb-8">
<div class="grid grid-cols-1 gap-4">
<div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
<div class="flex items-center mb-3">
<div class="w-12 h-12 flex items-center justify-center bg-blue-100 rounded-xl mr-4">
<i class="ri-map-pin-line text-blue-600 ri-xl"></i>
</div>
<div>
<h4 class="font-semibold text-gray-900">Precise Location</h4>
<p class="text-sm text-gray-600">City, Region & Coordinates</p>
</div>
</div>
</div>
<div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
<div class="flex items-center mb-3">
<div class="w-12 h-12 flex items-center justify-center bg-green-100 rounded-xl mr-4">
<i class="ri-map-2-line text-green-600 ri-xl"></i>
</div>
<div>
<h4 class="font-semibold text-gray-900">Google Maps</h4>
<p class="text-sm text-gray-600">Direct Map Integration</p>
</div>
</div>
</div>
<div class="bg-gradient-to-r from-purple-50 to-violet-50 rounded-xl p-6 border border-purple-100">
<div class="flex items-center mb-3">
<div class="w-12 h-12 flex items-center justify-center bg-purple-100 rounded-xl mr-4">
<i class="ri-flashlight-line text-purple-600 ri-xl"></i>
</div>
<div>
<h4 class="font-semibold text-gray-900">Batch Support</h4>
<p class="text-sm text-gray-600">Multiple IPs at Once</p>
</div>
</div>
</div>
</div>
</section>
<section class="mb-8">
<h2 class="text-xl font-bold text-gray-900 mb-6">API Endpoints</h2>
<div class="space-y-6">
<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
<div class="flex items-center justify-between mb-4">
<h3 class="font-semibold text-gray-900">Single IP Lookup</h3>
<span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">GET</span>
</div>
<div class="bg-white rounded-lg p-4 border border-gray-200 mb-4">
<code class="text-sm text-gray-700">/ip-info/ip?ip=YOUR_IP_ADDRESS</code>
</div>
<div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
<p class="text-sm font-medium text-blue-900 mb-2">📝 Example:</p>
<code class="text-sm text-blue-700">GET /ip-info/ip?ip=8.8.8.8</code>
</div>
</div>
<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
<div class="flex items-center justify-between mb-4">
<h3 class="font-semibold text-gray-900">Batch IP Lookup</h3>
<span class="px-3 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">POST</span>
</div>
<div class="bg-white rounded-lg p-4 border border-gray-200 mb-4">
<code class="text-sm text-gray-700">/ip-info/batch</code>
</div>
<div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
<p class="text-sm font-medium text-blue-900 mb-2">📝 Request Body:</p>
<code class="text-sm text-blue-700">{"ips": ["8.8.8.8", "1.1.1.1"]}</code>
</div>
</div>
<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
<div class="flex items-center justify-between mb-4">
<h3 class="font-semibold text-gray-900">Get Your Own IP</h3>
<span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">GET</span>
</div>
<div class="bg-white rounded-lg p-4 border border-gray-200 mb-4">
<code class="text-sm text-gray-700">/ip-info/myip</code>
</div>
<div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
<p class="text-sm font-medium text-blue-900 mb-2">📝 Example Response:</p>
<code class="text-sm text-blue-700">{"your_ip": "YOUR_IP_ADDRESS"}</code>
</div>
</div>
</div>
</section>
<section class="mb-8">
<div class="bg-gradient-to-r from-primary to-secondary rounded-xl p-6 text-white text-center">
<div class="mb-4">
<div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
<i class="ri-code-s-slash-line text-white ri-2x"></i>
</div>
<h3 class="text-xl font-bold mb-2">Try Our API</h3>
<p class="text-blue-100 text-sm mb-4">Test the endpoints with your own IP address</p>
</div>
<button id="tryApiBtn" class="bg-white text-primary px-6 py-3 rounded-button font-medium cursor-pointer !rounded-button hover:bg-blue-50 transition">
Get Started Now
</button>
</div>
</section>
<div class="text-center py-4">
<p class="text-sm text-gray-500">Developed by Creator Shyamchand & Ayan | CEO & Founder Of - Nexxon Hackers</p>
</div>
</main>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const tryBtn = document.getElementById('tryApiBtn');
    if (tryBtn) {
        tryBtn.addEventListener('click', function() {
            // Fetch user's IP and show demo
            fetch('/ip-info/myip')
                .then(res => res.json())
                .then(data => {
                    const demoModal = document.createElement('div');
                    demoModal.className = 'fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
                    demoModal.innerHTML = `
                        <div class="bg-white rounded-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
                            <div class="flex items-center justify-between mb-4">
                                <h3 class="font-bold text-gray-900">API Demo - Your IP</h3>
                                <button class="w-8 h-8 flex items-center justify-center cursor-pointer close-modal">
                                    <i class="ri-close-line text-gray-400 ri-lg"></i>
                                </button>
                            </div>
                            <div class="space-y-4">
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <p class="text-sm text-gray-600 mb-2">Your IP Address:</p>
                                    <code class="text-lg font-mono text-primary">${data.your_ip}</code>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">Test Endpoint</label>
                                    <select id="endpointSelect" class="w-full p-3 border border-gray-300 rounded-lg text-sm">
                                        <option value="myip">/ip-info/myip</option>
                                        <option value="ip">/ip-info/ip?ip=${data.your_ip}</option>
                                        <option value="batch">/ip-info/batch (POST)</option>
                                    </select>
                                </div>
                                <div id="responseArea" class="bg-gray-900 rounded-lg p-4 hidden">
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-xs text-gray-400">Response:</span>
                                        <button id="copyResponse" class="text-xs text-blue-400 hover:text-blue-300">Copy</button>
                                    </div>
                                    <pre id="responseContent" class="text-xs text-green-400 overflow-x-auto"></pre>
                                </div>
                                <button id="sendRequest" class="w-full bg-primary text-white py-3 rounded-button font-medium cursor-pointer !rounded-button hover:bg-secondary transition">
                                    Send Request
                                </button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(demoModal);
                    
                    const closeBtn = demoModal.querySelector('.close-modal');
                    const sendBtn = demoModal.querySelector('#sendRequest');
                    const select = demoModal.querySelector('#endpointSelect');
                    const responseArea = demoModal.querySelector('#responseArea');
                    const responseContent = demoModal.querySelector('#responseContent');
                    const copyBtn = demoModal.querySelector('#copyResponse');
                    
                    closeBtn.addEventListener('click', () => document.body.removeChild(demoModal));
                    demoModal.addEventListener('click', (e) => {
                        if (e.target === demoModal) document.body.removeChild(demoModal);
                    });
                    
                    sendBtn.addEventListener('click', async () => {
                        const endpoint = select.value;
                        let url, options = { method: 'GET' };
                        
                        if (endpoint === 'myip') {
                            url = '/ip-info/myip';
                        } else if (endpoint === 'ip') {
                            url = `/ip-info/ip?ip=${data.your_ip}`;
                        } else {
                            url = '/ip-info/batch';
                            options = {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ ips: [data.your_ip, '8.8.8.8'] })
                            };
                        }
                        
                        try {
                            const res = await fetch(url, options);
                            const json = await res.json();
                            responseContent.textContent = JSON.stringify(json, null, 2);
                            responseArea.classList.remove('hidden');
                        } catch (err) {
                            responseContent.textContent = 'Error: ' + err.message;
                            responseArea.classList.remove('hidden');
                        }
                    });
                    
                    copyBtn.addEventListener('click', () => {
                        navigator.clipboard.writeText(responseContent.textContent);
                        copyBtn.textContent = 'Copied!';
                        setTimeout(() => copyBtn.textContent = 'Copy', 2000);
                    });
                });
        });
    }
});
</script>
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
                "endpoint": "/ip-info/ip?ip=IP_ADDRESS",
                "example": "/ip-info/ip?ip=8.8.8.8"
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
            "single_ip": "/ip-info/ip?ip=IP_ADDRESS",
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
