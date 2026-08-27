import os

with open('static/js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = '''            tbody.innerHTML += <tr>
                <td style="text-align: center;"></td>
                <td></td>
                <td></td>
                <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                    <a href="/uploads/sops/" target="_blank" class="btn-table"'''

new_str = '''            let pdfUrl = s.filename.startswith('b64:') ? /uploads/sops/id_.pdf : /uploads/sops/;
            tbody.innerHTML += <tr>
                <td style="text-align: center;"></td>
                <td></td>
                <td></td>
                <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                    <a href="" target="_blank" class="btn-table"'''

content = content.replace(old_str, new_str)

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)
