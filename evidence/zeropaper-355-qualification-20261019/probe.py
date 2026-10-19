import importlib.util,pathlib,tempfile,json,sys,hashlib,subprocess,time
source=pathlib.Path(sys.argv[1]).resolve();start=time.monotonic();spec=importlib.util.spec_from_file_location('zp_probe',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as t:
 root=pathlib.Path(t);(root/'code').mkdir();f=root/'code'/'tiny.py';f.write_text('answer = 1\n');rec=m.fingerprint(root,'code/tiny.py');cases={}
 cases['unchanged']=m.compare_snapshot(root,[rec],'code')
 f.write_text('answer = 2\n');cases['changed']=m.compare_snapshot(root,[rec],'code')
 f.unlink();cases['missing']=m.compare_snapshot(root,[rec],'code')
 cases['malformed']=m.compare_snapshot(root,[{'sha256':'invalid'}],'code')
 assert not cases['unchanged'] and all(cases[k] for k in ['changed','missing','malformed'])
 assert not (root/'process_log').exists()
 r=subprocess.run([sys.executable,str(source),'check-closure','--receipt','invented.json'],cwd=t,capture_output=True,text=True);assert r.returncode==2 and 'invalid choice' in r.stderr and not(root/'process_log').exists()
 print(json.dumps({'cases':cases,'check_closure_exit':r.returncode,'check_closure_error':'parser invalid choice','process_log_created':False,'elapsed_seconds':round(time.monotonic()-start,4),'scope':'synthetic helper+CLI gap only; no registry,producer,live dataset or performance saving tested'},indent=2))
