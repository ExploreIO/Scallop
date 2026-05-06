from modules.base import BaseModule


class FingerprintModule(BaseModule):
    """浏览器指纹采集模块：生成注入页面的JS探测脚本"""
    
    def get_probe_script(self):
        """返回浏览器指纹采集的JS脚本"""
        return '''<script>
(function() {
    if (window.__scallop_fp_done) return;
    window.__scallop_fp_done = true;
    var fp = {};
    try {
        fp.ua = navigator.userAgent;
        fp.vendor = navigator.vendor || '';
        fp.platform = navigator.platform || '';
        fp.language = navigator.language || '';
        fp.languages = (navigator.languages || []).join(',');
        fp.screenW = screen.width;
        fp.screenH = screen.height;
        fp.availW = screen.availWidth;
        fp.availH = screen.availHeight;
        fp.colorDepth = screen.colorDepth;
        fp.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
        fp.hardwareConcurrency = navigator.hardwareConcurrency || 0;
        fp.deviceMemory = navigator.deviceMemory || 0;
        fp.doNotTrack = navigator.doNotTrack || 'unspecified';
        fp.plugins = [];
        if (navigator.plugins) {
            for (var i = 0; i < navigator.plugins.length && i < 10; i++) {
                fp.plugins.push(navigator.plugins[i].name);
            }
        }
    } catch(e) {}
    try {
        var canvas = document.createElement('canvas');
        canvas.width = 280;
        canvas.height = 60;
        canvas.style.display = 'none';
        var ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillStyle = '#f60';
        ctx.fillRect(0, 0, 100, 20);
        ctx.fillStyle = '#069';
        ctx.fillText('Scallop FP ' + new Date().getTime(), 2, 15);
        fp.canvasHash = canvas.toDataURL().slice(-32);
    } catch(e) {}
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/_fp', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(fp));
    } catch(e) {}
})();
</script>'''
    
    def get_probe_url(self):
        """返回指纹采集的API路径"""
        return '/_fp'
