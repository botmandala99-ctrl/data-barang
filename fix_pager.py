#!/usr/bin/env python3
"""Ganti seluruh blok pagination JS dengan versi bersih & robust.
Fixes: tombol Prev selalu tampil, Next selalu tampil, label rapih."""
with open('/tmp/data-barang/barang.html') as f:
    html = f.read()

# Cari blok lama dari 'function initPagination' sampai sebelum '</script>'
old_start = html.find('function initPagination(')
old_end = html.find('initPagination(\'bt\',10);initPagination(\'wt\',10);')
old_end = html.find(';', old_end) + 1  # ujung init call

if old_start < 0:
    print('initPagination tidak ketemu')
    raise SystemExit

new_js = r'''
/* ===== PAGINATION (10 item) ===== */
function initPagination(tid,pageSize){
 var tb=document.getElementById(tid);
 if(!tb)return;
 pageSize=pageSize||10;
 if(!window._origRows)window._origRows={};
 var rows=tb.getElementsByTagName('tr');
 var arr=[];
 for(var i=0;i<rows.length;i++)arr.push(rows[i]);
 window._origRows[tid]=arr;
 window['_size_'+tid]=pageSize;
 renderPage(tid,0);
}
function _filterMatch(tr,mode){
 if(mode==='all')return true;
 var td2=tr.getElementsByTagName('td')[2];
 var stok=td2?parseInt(td2.textContent.replace(/\./g,'').replace(/,/g,''))||0:0;
 return mode==='stok'?(stok>0):(mode==='kosong'?(stok===0):true);
}
function _pBtn(lbl,fn){
 var b=document.createElement('button');
 b.style.cssText='padding:4px 9px;border:1px solid #ccc;border-radius:4px;background:#fff;font-size:10px;cursor:pointer;margin:0 2px;';
 b.textContent=lbl;
 b.onclick=fn;
 return b;
}
function renderPage(tid,page){
 var arr=window._origRows[tid];
 if(!arr)return;
 var size=window['_size_'+tid]||10;
 var total=arr.length;
 var mode=(tid==='bt')?(window._filterMode||'all'):(tid==='wt'?(window._warnMode||'all'):'all');
 // filter
 var visible=[];
 for(var i=0;i<total;i++){
  var ok=_filterMatch(arr[i],mode);
  if(tid==='wt'&&mode!=='all'){
   var kc=arr[i].getElementsByTagName('td')[4];
   var k=kc?kc.textContent.trim():'';
   ok=(mode==='all'||k===mode);
  }
  if(ok)visible.push(i);
 }
 var vlen=visible.length;
 var vpages=Math.max(1,Math.ceil(vlen/size));
 if(page<0)page=0;if(page>=vpages)page=vpages-1;
 // sembunyikan semua lalu tampilkan halaman
 for(var i=0;i<total;i++)arr[i].style.display='none';
 var vs=page*size, ve=Math.min(vs+size,vlen);
 for(var vi=vs;vi<ve;vi++)arr[visible[vi]].style.display='';
 // kontrol
 var ctrl=document.getElementById(tid+'-page');
 if(!ctrl)return;
 ctrl.innerHTML='';
 var shownStart=vs+1, shownEnd=ve;
 var sh=shownEnd>shownStart-1?(shownStart+'-'+shownEnd):'0';
 var prev=_pBtn('◀ Prev',function(){renderPage(tid,page-1);});
 var next=_pBtn('Next ▶',function(){renderPage(tid,page+1);});
 var lbl=document.createElement('span');
 lbl.style.cssText='font-size:10px;color:#555;margin:0 6px;';
 lbl.textContent=sh+' / '+vlen+' • Hal '+(page+1)+'/'+vpages;
 if(page>0)ctrl.appendChild(prev);
 ctrl.appendChild(lbl);
 if(page<vpages-1)ctrl.appendChild(next);
 window['_page_'+tid]=page;
}
'''
# Sisipkan new_js menggantikan blok lama (dari old_start sampai old_end)
html = html[:old_start] + new_js + "\ninitPagination('bt',10);initPagination('wt',10);\n" + html[old_end:]

with open('/tmp/data-barang/barang.html','w') as f:
    f.write(html)

# Verifikasi
print("renderPage ada:", html.count('function renderPage'))
print("initPagination ada:", html.count('function initPagination'))
print("Ini ganti prev:", html.count("_pBtn('◀ Prev'"))
print("Ini ganti next:", html.count("_pBtn('Next ▶'"))
print("init call:", "initPagination('bt',10);initPagination('wt',10)" in html)
print("ukuran:", len(html))
print("OK")
