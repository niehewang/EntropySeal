#!/usr/bin/env python3
import argparse,csv,hashlib,json
from pathlib import Path
import torch

def shaf(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def tsha(t):
    return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes(order='C')).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--audit-json',required=True)
    p.add_argument('--tensor-audit-csv',required=True)
    a=p.parse_args()
    obj=torch.load(a.input,map_location='cpu')
    if set(obj.keys())!={'model_state_dict'}:
        raise RuntimeError('FP16_PROFILE_INVALID_CHECKPOINT_STRUCTURE')
    sd=obj['model_state_dict']
    rows=[];changed_tensors=0;changed_scalars=0;float_count=0;abs_sum=0.0;abs_max=0.0;nonfloat_ok=True
    for name,x in sd.items():
        before=x.detach().cpu().clone()
        if torch.is_floating_point(before):
            after=before.to(torch.float16).to(before.dtype)
            delta=torch.abs(after.to(torch.float64)-before.to(torch.float64))
            n=int(torch.count_nonzero(after!=before).item())
            changed_tensors+=int(n>0);changed_scalars+=n;float_count+=before.numel()
            if delta.numel():
                abs_sum+=float(delta.sum().item());abs_max=max(abs_max,float(delta.max().item()))
            sd[name]=after
            rows.append({'tensor':name,'dtype':str(before.dtype),'floating':True,'scalar_count':before.numel(),'changed_scalar_count':n,'source_sha256':tsha(before),'fp16_sha256':tsha(after),'byte_identical':bool(torch.equal(before,after))})
        else:
            after=before.clone();nonfloat_ok=nonfloat_ok and torch.equal(before,after)
            rows.append({'tensor':name,'dtype':str(before.dtype),'floating':False,'scalar_count':before.numel(),'changed_scalar_count':0,'source_sha256':tsha(before),'fp16_sha256':tsha(after),'byte_identical':True})
    torch.save(obj,a.output)
    audit={'whole_file_sha256':shaf(a.output),'changed_tensor_count':changed_tensors,'changed_scalar_count':changed_scalars,'floating_scalar_count':float_count,'max_abs_parameter_delta':abs_max,'mean_abs_parameter_delta_over_floating_scalars':abs_sum/max(float_count,1),'nonfloating_tensors_byte_identical':bool(nonfloat_ok),'transform':'FP16_STORAGE_ROUNDTRIP'}
    Path(a.audit_json).write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    with open(a.tensor_audit_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)

if __name__=='__main__':
    main()
