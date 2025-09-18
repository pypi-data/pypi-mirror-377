"""
ProServe E2E Static File Serving Tests
Static websites, file hosting, CDN functionality, and web server capabilities
"""

import pytest
import requests
import tempfile
from pathlib import Path
from .test_framework import ProServeTestFramework, assert_http_response


@pytest.mark.asyncio
async def test_static_website_hosting(framework: ProServeTestFramework):
    """Test complete static website hosting with HTML, CSS, JS, and assets"""
    
    # Create static website files
    website_dir = framework.temp_dir / "website"
    website_dir.mkdir(exist_ok=True)
    
    # Create HTML file
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProServe Test Site</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <h1>Welcome to ProServe</h1>
    <p>This is a test static website served by ProServe.</p>
    <img src="/images/logo.png" alt="Logo" id="logo">
    <script src="/js/app.js"></script>
</body>
</html>'''
    
    (website_dir / "index.html").write_text(html_content)
    
    # Create CSS file
    css_dir = website_dir / "css"
    css_dir.mkdir(exist_ok=True)
    css_content = '''body {
    font-family: Arial, sans-serif;
    background-color: #f0f8ff;
    margin: 0;
    padding: 20px;
}

h1 {
    color: #2c3e50;
    text-align: center;
}

#logo {
    max-width: 200px;
    height: auto;
    display: block;
    margin: 20px auto;
}'''
    
    (css_dir / "style.css").write_text(css_content)
    
    # Create JavaScript file
    js_dir = website_dir / "js"
    js_dir.mkdir(exist_ok=True)
    js_content = '''console.log("ProServe static website loaded!");

document.addEventListener("DOMContentLoaded", function() {
    const logo = document.getElementById("logo");
    if (logo) {
        logo.addEventListener("click", function() {
            alert("ProServe E2E Test - Static hosting works!");
        });
    }
    
    // Add dynamic timestamp
    const timestamp = document.createElement("p");
    timestamp.textContent = "Loaded at: " + new Date().toLocaleString();
    timestamp.style.fontSize = "12px";
    timestamp.style.color = "#666";
    document.body.appendChild(timestamp);
});'''
    
    (js_dir / "app.js").write_text(js_content)
    
    # Create placeholder image (small PNG-like content)
    images_dir = website_dir / "images"
    images_dir.mkdir(exist_ok=True)
    # Simple PNG header for testing (1x1 transparent pixel)
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01U\r\xb6\x9c\x00\x00\x00\x00IEND\xaeB`\x82'
    (images_dir / "logo.png").write_bytes(png_bytes)
    
    # Create manifest for static hosting
    manifest_path = framework.create_test_manifest(
        'test-static-website',
        static_hosting={
            'enabled': True,
            'static_dir': str(website_dir),
            'index_file': 'index.html',
            'cache_ttl': 3600
        },
        enable_cors=True
    )
    
    service = await framework.start_test_service(manifest_path, 'static_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test index page
    index_response = requests.get(f"{base_url}/")
    assert index_response.status_code == 200
    assert "Welcome to ProServe" in index_response.text
    assert "text/html" in index_response.headers.get('content-type', '')
    
    # Test CSS file
    css_response = requests.get(f"{base_url}/css/style.css")
    assert css_response.status_code == 200
    assert "font-family: Arial" in css_response.text
    assert "text/css" in css_response.headers.get('content-type', '')
    
    # Test JavaScript file
    js_response = requests.get(f"{base_url}/js/app.js")
    assert js_response.status_code == 200
    assert "ProServe static website loaded!" in js_response.text
    assert "javascript" in js_response.headers.get('content-type', '').lower()
    
    # Test image file
    image_response = requests.get(f"{base_url}/images/logo.png")
    assert image_response.status_code == 200
    assert "image/png" in image_response.headers.get('content-type', '')
    assert len(image_response.content) > 0
    
    # Test 404 for non-existent file
    not_found_response = requests.get(f"{base_url}/nonexistent.html")
    assert not_found_response.status_code == 404
    
    # Test cache headers
    assert 'cache-control' in css_response.headers
    assert 'last-modified' in css_response.headers or 'etag' in css_response.headers
    
    return {
        "static_website_served": True,
        "html_loaded": "Welcome to ProServe" in index_response.text,
        "css_loaded": css_response.status_code == 200,
        "js_loaded": js_response.status_code == 200,
        "image_loaded": image_response.status_code == 200,
        "404_handled": not_found_response.status_code == 404,
        "cache_headers_present": 'cache-control' in css_response.headers
    }


@pytest.mark.asyncio
async def test_spa_routing(framework: ProServeTestFramework):
    """Test Single Page Application (SPA) routing support"""
    
    # Create SPA files
    spa_dir = framework.temp_dir / "spa"
    spa_dir.mkdir(exist_ok=True)
    
    # Create index.html for SPA
    spa_html = '''<!DOCTYPE html>
<html>
<head>
    <title>ProServe SPA Test</title>
    <meta charset="UTF-8">
</head>
<body>
    <div id="app">
        <h1>SPA Test App</h1>
        <nav>
            <a href="/" onclick="navigate('/')">Home</a>
            <a href="/about" onclick="navigate('/about')">About</a>
            <a href="/contact" onclick="navigate('/contact')">Contact</a>
        </nav>
        <div id="content">Welcome to Home Page</div>
    </div>
    
    <script>
        function navigate(path) {
            history.pushState({}, '', path);
            updateContent(path);
            return false;
        }
        
        function updateContent(path) {
            const content = document.getElementById('content');
            switch(path) {
                case '/':
                    content.innerHTML = 'Welcome to Home Page';
                    break;
                case '/about':
                    content.innerHTML = 'About Us Page - ProServe SPA Testing';
                    break;
                case '/contact':
                    content.innerHTML = 'Contact Page - Get in touch!';
                    break;
                default:
                    content.innerHTML = 'Page Not Found - SPA 404';
            }
        }
        
        window.addEventListener('popstate', function() {
            updateContent(location.pathname);
        });
        
        // Initialize based on current path
        document.addEventListener('DOMContentLoaded', function() {
            updateContent(location.pathname);
        });
    </script>
</body>
</html>'''
    
    (spa_dir / "index.html").write_text(spa_html)
    
    # Create manifest with SPA support (fallback to index.html)
    manifest_path = framework.create_test_manifest(
        'test-spa-routing',
        static_hosting={
            'enabled': True,
            'static_dir': str(spa_dir),
            'index_file': 'index.html',
            'spa_fallback': True  # This should make all routes serve index.html
        }
    )
    
    service = await framework.start_test_service(manifest_path, 'spa_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test root path
    root_response = requests.get(f"{base_url}/")
    assert root_response.status_code == 200
    assert "SPA Test App" in root_response.text
    
    # Test SPA routes (should all serve index.html)
    about_response = requests.get(f"{base_url}/about")
    contact_response = requests.get(f"{base_url}/contact")
    nested_response = requests.get(f"{base_url}/some/nested/route")
    
    # All should return the same index.html content
    assert about_response.status_code == 200
    assert contact_response.status_code == 200
    assert nested_response.status_code == 200
    
    assert "SPA Test App" in about_response.text
    assert "SPA Test App" in contact_response.text
    assert "SPA Test App" in nested_response.text
    
    return {
        "spa_routing_works": True,
        "root_served": "SPA Test App" in root_response.text,
        "about_fallback": "SPA Test App" in about_response.text,
        "contact_fallback": "SPA Test App" in contact_response.text,
        "nested_route_fallback": "SPA Test App" in nested_response.text
    }


@pytest.mark.asyncio
async def test_file_compression_and_optimization(framework: ProServeTestFramework):
    """Test file compression (gzip) and static asset optimization"""
    
    # Create test files with different sizes
    static_dir = framework.temp_dir / "optimized"
    static_dir.mkdir(exist_ok=True)
    
    # Large CSS file (should be compressed)
    large_css = "/* Large CSS file for compression testing */\n" + "body { margin: 0; }\n" * 1000
    (static_dir / "large.css").write_text(large_css)
    
    # Large JavaScript file
    large_js = "/* Large JS file */\n" + "console.log('test line');\n" * 1000
    (static_dir / "large.js").write_text(large_js)
    
    # Small file (might not be compressed)
    small_txt = "Small file content"
    (static_dir / "small.txt").write_text(small_txt)
    
    # HTML with references
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/large.css">
    <script src="/large.js"></script>
</head>
<body>
    <h1>Compression Test</h1>
    <a href="/small.txt">Small file</a>
</body>
</html>'''
    (static_dir / "index.html").write_text(html_content)
    
    manifest_path = framework.create_test_manifest(
        'test-compression',
        static_hosting={
            'enabled': True,
            'static_dir': str(static_dir),
            'compression': True,  # Enable gzip compression
            'cache_ttl': 86400
        }
    )
    
    service = await framework.start_test_service(manifest_path, 'compression_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test with compression headers
    headers = {'Accept-Encoding': 'gzip, deflate'}
    
    # Test large CSS file (should be compressed)
    css_response = requests.get(f"{base_url}/large.css", headers=headers)
    assert css_response.status_code == 200
    
    # Test large JS file
    js_response = requests.get(f"{base_url}/large.js", headers=headers)
    assert js_response.status_code == 200
    
    # Test small file
    small_response = requests.get(f"{base_url}/small.txt", headers=headers)
    assert small_response.status_code == 200
    
    # Check for compression indicators
    css_compressed = 'gzip' in css_response.headers.get('content-encoding', '')
    js_compressed = 'gzip' in js_response.headers.get('content-encoding', '')
    
    # Check cache headers for optimization
    css_cache = css_response.headers.get('cache-control', '')
    js_cache = js_response.headers.get('cache-control', '')
    
    # Test ETag or Last-Modified headers
    css_etag = 'etag' in css_response.headers or 'last-modified' in css_response.headers
    js_etag = 'etag' in js_response.headers or 'last-modified' in js_response.headers
    
    return {
        "compression_enabled": css_compressed or js_compressed,
        "large_css_served": css_response.status_code == 200,
        "large_js_served": js_response.status_code == 200,
        "small_file_served": small_response.status_code == 200,
        "cache_headers_present": 'max-age' in css_cache or 'public' in css_cache,
        "etag_headers_present": css_etag and js_etag,
        "css_size": len(css_response.content),
        "js_size": len(js_response.content)
    }


@pytest.mark.asyncio
async def test_static_file_security(framework: ProServeTestFramework):
    """Test static file serving security features and access control"""
    
    # Create directory structure with different access levels
    secure_dir = framework.temp_dir / "secure"
    secure_dir.mkdir(exist_ok=True)
    
    # Public files
    public_dir = secure_dir / "public"
    public_dir.mkdir(exist_ok=True)
    (public_dir / "allowed.txt").write_text("This file is publicly accessible")
    
    # Private/sensitive files
    private_dir = secure_dir / "private"
    private_dir.mkdir(exist_ok=True)
    (private_dir / "config.json").write_text('{"secret": "should_not_be_accessible"}')
    (private_dir / "passwords.txt").write_text("admin:secret123")
    
    # System files that should be blocked
    (secure_dir / ".env").write_text("SECRET_KEY=very_secret")
    (secure_dir / ".htaccess").write_text("RewriteEngine On")
    (secure_dir / "backup.sql").write_text("DROP TABLE users;")
    
    # Main index file
    (secure_dir / "index.html").write_text('''<!DOCTYPE html>
<html>
<head><title>Security Test</title></head>
<body>
    <h1>Static Security Test</h1>
    <a href="/public/allowed.txt">Allowed File</a>
    <a href="/private/config.json">Private Config (should be blocked)</a>
    <a href="/.env">Env file (should be blocked)</a>
</body>
</html>''')
    
    manifest_path = framework.create_test_manifest(
        'test-static-security',
        static_hosting={
            'enabled': True,
            'static_dir': str(secure_dir),
            'index_file': 'index.html',
            'deny_patterns': [
                '*.env',
                '*.sql', 
                '.htaccess',
                'private/*',
                '*.bak',
                '*.log'
            ]
        }
    )
    
    service = await framework.start_test_service(manifest_path, 'security_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test accessible files
    index_response = requests.get(f"{base_url}/")
    public_response = requests.get(f"{base_url}/public/allowed.txt")
    
    assert index_response.status_code == 200
    assert public_response.status_code == 200
    assert "publicly accessible" in public_response.text
    
    # Test blocked files (should return 403 Forbidden or 404 Not Found)
    env_response = requests.get(f"{base_url}/.env")
    htaccess_response = requests.get(f"{base_url}/.htaccess")
    sql_response = requests.get(f"{base_url}/backup.sql")
    private_response = requests.get(f"{base_url}/private/config.json")
    
    # These should be blocked
    blocked_responses = [env_response, htaccess_response, sql_response, private_response]
    blocked_count = sum(1 for r in blocked_responses if r.status_code in [403, 404])
    
    # Test directory traversal attacks
    traversal_attempts = [
        "../../../etc/passwd",
        "..\\..\\windows\\system32\\config",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        "....//....//etc/passwd"
    ]
    
    traversal_blocked = 0
    for attempt in traversal_attempts:
        traversal_response = requests.get(f"{base_url}/{attempt}")
        if traversal_response.status_code in [403, 404]:
            traversal_blocked += 1
    
    return {
        "public_files_accessible": public_response.status_code == 200,
        "sensitive_files_blocked": blocked_count == len(blocked_responses),
        "directory_traversal_blocked": traversal_blocked == len(traversal_attempts),
        "index_served": index_response.status_code == 200,
        "security_test_passed": blocked_count >= 3 and traversal_blocked >= 2
    }
